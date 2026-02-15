# 🤖 AI Chart Bot - Gemini-powered Chatbot with Chart Generation

A beautiful, web-based AI chatbot built with Flask and the Gemini REST API that can generate interactive charts on the fly. Chat about anything and request visualizations!

## ✨ Features

- **Real-time Chat Interface**: Modern, responsive chat UI with real-time message streaming
- **AI Power**: Uses Google's Gemini REST API for intelligent responses
- **Chart Generation**: Automatically generate bar, line, pie, and doughnut charts from AI responses
- **Conversation Memory**: Bot remembers context from your chat history
- **Beautiful UI**: Gradient design, smooth animations, and mobile-responsive layout
- **Empty State Protection**: Clear visual feedback for charts and status indicators

## 📋 Requirements

- Python 3.8+
- Gemini API Key (get one from Google AI Studio)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Gemini API Key

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=your-gemini-api-key-here
```

Or set the environment variable directly:

**Windows (Command Prompt):**
```bash
set OPENAI_API_KEY=your-gemini-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-gemini-api-key-here"
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY="your-gemini-api-key-here"
```

### 3. Run the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## 📊 How to Use

1. **Open the chat**: Navigate to `http://localhost:5000` in your browser
2. **Chat normally**: Type any question or request
3. **Generate charts**: Ask the bot to create visualizations, e.g.:
   - "Show a bar chart of Q1, Q2, Q3 sales with values 100, 150, 200"
   - "Create a pie chart showing market share: Apple 30%, Google 50%, Amazon 20%"
   - "Line chart of Bitcoin prices this month: Jan 30k, Feb 35k, Mar 32k"

## 🎨 Chart Types Supported

- **Bar Chart**: Great for comparisons
- **Line Chart**: Perfect for trends over time
- **Pie Chart**: Shows distribution/percentages
- **Doughnut Chart**: Similar to pie but with a hole in the center

## 📁 Project Structure

```
Chatbot/
├── app.py                 # Flask backend with OpenAI integration
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main chat UI
└── static/
    ├── style.css         # Styling
    └── script.js         # Frontend logic & Chart.js integration
```

## 🔧 Technical Details

### Backend (Flask)

- Uses the Gemini REST API for responses
- Supports markdown formatting
- Charts are generated through special XML-like tags: `[CHART]...data...[/CHART]`
- Maintains conversation history for context (last 20 messages)

### Frontend (Vanilla JS + Chart.js)

- Real-time message rendering
- Dynamic chart generation with Chart.js library
- Responsive grid layout (2-column on desktop, 1-column on mobile)
- Smooth animations and transitions
- Status indicator for connection state

## 🎯 Example Prompts

```
"Create a bar chart comparing Python, JavaScript, and Java with values 85, 92, 78"
"Show me a pie chart of programming languages used: Python 40%, JS 35%, Java 25%"
"Line chart of website traffic: Monday 1000, Tuesday 1200, Wednesday 950"
"What are the top programming languages and show them in a chart?"
```

## 🐛 Troubleshooting

### API Key Error
- Ensure `OPENAI_API_KEY` is set correctly and never committed to Git
- Test with: `echo $OPENAI_API_KEY` (Mac/Linux) or `echo %OPENAI_API_KEY%` (Windows)

### Connection Refused
- Make sure Flask is running on port 5000
- Check if another app is using port 5000

### Charts Not Appearing
- Check browser console (F12) for JavaScript errors
- Ensure Chart.js library loaded: `https://cdn.jsdelivr.net/npm/chart.js`

## 🚀 Advanced Features You Can Add

- Database to store chat history
- User authentication
- Export chats as PDF
- Dark mode toggle
- Voice input
- Streaming responses
- Custom system prompts

## 📄 License

Feel free to use and modify this project!

## 💡 Tips

- **Tip 1**: Be specific with chart requests for better results
- **Tip 2**: The bot will automatically decide when to include charts
- **Tip 3**: Ask follow-up questions to refine visualizations
- **Tip 4**: Clear chat history when starting a new topic

Enjoy your AI Chart Bot! 🎉
