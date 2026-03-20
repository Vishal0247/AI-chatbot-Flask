import os
import json
import re
import requests
import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Gemini API key (support legacy OPENAI_API_KEY for compatibility)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set (this should be your Gemini API key)")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
CHAT_HISTORY_FILE = "chat_history.json"

# Storage structure: { "threads": [ {"id": str, "title": str, "messages": [...] , "last_updated": str } ], "last_saved": str }
threads = []
active_thread_id = None

def load_storage():
    """Load threads from disk; migrate old flat format if necessary."""
    global threads, active_thread_id
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as f:
                data = json.load(f)
                # Support legacy format { messages: [...] }
                if "threads" in data:
                    threads = data.get("threads", [])
                elif "messages" in data:
                    threads = [
                        {
                            "id": datetime.datetime.now().isoformat(),
                            "title": "Saved Conversation",
                            "messages": data.get("messages", []),
                            "last_updated": data.get("last_saved") or datetime.datetime.now().isoformat()
                        }
                    ]
                else:
                    threads = []
                if threads:
                    active_thread_id = threads[-1]["id"]
                print(f"✅ Loaded {len(threads)} thread(s) from storage")
        except Exception as e:
            print(f"⚠️ Could not load storage: {e}")
            threads = []
            active_thread_id = None
    else:
        threads = []
        active_thread_id = None

def save_storage():
    """Save threads to disk"""
    try:
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump({
                "threads": threads,
                "last_saved": datetime.datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save storage: {e}")

def get_active_thread():
    """Return the active thread dict and ensure conversation list points to it."""
    global threads, active_thread_id
    if not threads:
        # create new empty thread
        tid = datetime.datetime.now().isoformat()
        thread = {"id": tid, "title": "Conversation", "messages": [], "last_updated": datetime.datetime.now().isoformat()}
        threads.append(thread)
        active_thread_id = tid
        return thread
    for t in threads:
        if t["id"] == active_thread_id:
            return t
    # fallback to last thread
    active_thread_id = threads[-1]["id"]
    return threads[-1]

def parse_chart_request(text):
    pattern = r"\[CHART\](.*?)\[/CHART\]"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            chart = json.loads(match.group(1))
            clean = re.sub(pattern, "", text, flags=re.DOTALL).strip()
            return clean, chart
        except json.JSONDecodeError:
            return text, None
    return text, None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        thread = get_active_thread()
        thread_messages = thread.setdefault("messages", [])
        thread_messages.append({
            "role": "user",
            "content": user_message
        })

        # Detect if this is an emotional/casual conversation
        emotional_keywords = ["how are you", "feeling", "sad", "happy", "love", "hate", "miss", "friend", "lonely", "tired", "excited", "thanks", "please", "hi", "hello", "hey", "goodbye", "bye"]
        is_emotional = any(keyword in user_message.lower() for keyword in emotional_keywords)
        
        # Set max tokens based on conversation type
        max_tokens = 1000 if is_emotional else 8000

        # Build request for Gemini REST API
        message_contents = []
        for msg in thread_messages:
            message_contents.append({
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            })

        payload = {
            "systemInstruction": {
                "parts": {
                    "text": """You are a helpful, friendly AI chatbot. 
Always read and understand what the user says first, then respond accordingly.

For personal/emotional conversations (like greetings, feelings, personal topics):
- Keep responses brief and warm - under 200 words
- Acknowledge what they said
- Show genuine interest
- Ask follow-up questions if appropriate

For informational questions (research, facts, explanations):
- Provide detailed comprehensive answers
- Use web search for current information
- Give thorough explanations

Example:
- User: "heyy how are you?" → "I'm doing great, thanks for asking! How are YOU doing today? What brings you here?"
- User: "I'm feeling sad" → "I'm sorry to hear that. Do you want to talk about it? I'm here to listen and help."

When useful, include chart data in this format:
[CHART]{"type":"bar|line|pie|doughnut","labels":[],"data":[],"title":"Title"}[/CHART]

Always be authentic, warm, and respond to what the user actually says."""
                }
            },
            "contents": message_contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": max_tokens
            },
            "tools": [
                {
                    "googleSearch": {}
                }
            ]
        }

        # Call Gemini API with web search enabled
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload
        )

        if response.status_code != 200:
            return jsonify({"error": f"Gemini API error: {response.text}"}), 500

        data = response.json()
        
        # Safe extraction of text from Gemini API response
        candidates = data.get("candidates", [])
        if not candidates:
            prompt_feedback = data.get("promptFeedback", {})
            if "blockReason" in prompt_feedback:
                return jsonify({"error": f"Message blocked by safety settings: {prompt_feedback.get('blockReason')}"}), 400
            return jsonify({"error": "No response generated. Please try again."}), 400
            
        candidate = candidates[0]
        if "content" not in candidate:
            finish_reason = candidate.get("finishReason", "UNKNOWN")
            return jsonify({"error": f"Response could not be generated. Reason: {finish_reason}"}), 400
        
        parts = candidate["content"].get("parts", [])
        assistant_text = ""
        for part in parts:
            if "text" in part:
                assistant_text += part["text"]

        clean_text, chart_data = parse_chart_request(assistant_text)

        thread_messages.append({
            "role": "model",
            "content": clean_text
        })
        thread["last_updated"] = datetime.datetime.now().isoformat()
        # Keep only last 200 messages per thread to limit size
        if len(thread_messages) > 200:
            thread["messages"] = thread_messages[-200:]
        # Save storage
        save_storage()

        return jsonify({
            "response": clean_text,
            "chart": chart_data
        })

    except Exception as e:
        print("🔥 BACKEND ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/clear", methods=["POST"])
def clear_chat():
    # clear current active thread messages
    thread = get_active_thread()
    thread["messages"] = []
    thread["last_updated"] = datetime.datetime.now().isoformat()
    save_storage()
    return jsonify({"status": "cleared"})

@app.route("/history", methods=["GET"])
def get_history():
    """Return list of saved threads (id, title, count, last_updated)"""
    items = []
    for t in threads:
        items.append({
            "id": t["id"],
            "title": t.get("title", "Conversation"),
            "count": len(t.get("messages", [])),
            "last_updated": t.get("last_updated")
        })
    return jsonify({"threads": items})


@app.route("/thread/<thread_id>", methods=["GET"]) 
def get_thread(thread_id):
    """Return messages for a single thread"""
    for t in threads:
        if t["id"] == thread_id:
            return jsonify({"thread": t})
    return jsonify({"error": "thread not found"}), 404


@app.route("/delete_message", methods=["POST"])
def delete_message():
    data = request.json or {}
    thread_id = data.get("thread_id")
    index = data.get("index")
    if thread_id is None or index is None:
        return jsonify({"error": "thread_id and index required"}), 400
    for t in threads:
        if t["id"] == thread_id:
            msgs = t.get("messages", [])
            if 0 <= index < len(msgs):
                msgs.pop(index)
                t["last_updated"] = datetime.datetime.now().isoformat()
                save_storage()
                return jsonify({"status": "deleted"})
            return jsonify({"error": "index out of range"}), 400
    return jsonify({"error": "thread not found"}), 404


@app.route("/export/<thread_id>", methods=["GET"])
def export_thread(thread_id):
    for t in threads:
        if t["id"] == thread_id:
            return jsonify(t)
    return jsonify({"error": "thread not found"}), 404


@app.route("/delete_thread", methods=["POST"])
def delete_thread():
    data = request.json or {}
    thread_id = data.get("thread_id")
    if not thread_id:
        return jsonify({"error": "thread_id required"}), 400
    global threads, active_thread_id
    for i, t in enumerate(threads):
        if t["id"] == thread_id:
            threads.pop(i)
            # reset active thread if needed
            if active_thread_id == thread_id:
                active_thread_id = threads[-1]["id"] if threads else None
            save_storage()
            return jsonify({"status": "deleted"})
    return jsonify({"error": "thread not found"}), 404

# Ensure storage is loaded when running under WSGI servers and scripts.
load_storage()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
