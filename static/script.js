// Global variables
let chatMessages = document.getElementById('chatMessages');
let messageInput = document.getElementById('messageInput');
let chatForm = document.getElementById('chatForm');
let clearBtn = document.getElementById('clearBtn');
let statusIndicator = document.getElementById('statusIndicator');
let chartContainer = document.getElementById('chartContainer');
let emptyState = document.getElementById('emptyState');
let myChart = null;

// Event listeners
chatForm.addEventListener('submit', handleSendMessage);
clearBtn.addEventListener('click', handleClearHistory);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

async function handleSendMessage(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    // Disable input
    messageInput.disabled = true;
    chatForm.querySelector('.send-btn').disabled = true;
    setStatus('loading');

    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();

        // Add assistant response to chat
        addMessage(data.response, 'assistant');

        // Handle chart if present
        if (data.chart) {
            displayChart(data.chart);
        }

        setStatus('success');
    } catch (error) {
        console.error('Error:', error);
        addMessage(`⚠️ Error: ${error.message}`, 'assistant');
        setStatus('error');
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        chatForm.querySelector('.send-btn').disabled = false;
        messageInput.focus();
    }
}

function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const p = document.createElement('p');
    p.textContent = text;

    messageDiv.appendChild(p);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displayChart(chartData) {
    // Show chart container and hide empty state
    chartContainer.style.display = 'block';
    emptyState.style.display = 'none';

    // Get canvas
    const canvas = document.getElementById('myChart');
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (myChart) {
        myChart.destroy();
    }

    // Determine colors based on chart type
    const colors = generateColors(chartData.data.length);

    let chartConfig = {
        type: chartData.type || 'bar',
        data: {
            labels: chartData.labels || [],
            datasets: [{
                label: chartData.title || 'Data',
                data: chartData.data || [],
                backgroundColor: chartData.type === 'pie' || chartData.type === 'doughnut'
                    ? colors
                    : 'rgba(102, 126, 234, 0.6)',
                borderColor: chartData.type === 'pie' || chartData.type === 'doughnut'
                    ? colors
                    : 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: chartData.type === 'line'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: chartData.type === 'pie' || chartData.type === 'doughnut',
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: chartData.title || 'Chart'
                }
            },
            scales: chartData.type === 'pie' || chartData.type === 'doughnut' ? {} : {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#666'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        color: '#666'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    };

    myChart = new Chart(ctx, chartConfig);
}

function generateColors(count) {
    const colors = [
        'rgba(102, 126, 234, 0.6)',
        'rgba(118, 75, 162, 0.6)',
        'rgba(255, 107, 107, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 243, 0.6)',
        'rgba(201, 203, 207, 0.6)'
    ];

    let result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

async function handleClearHistory() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        try {
            await fetch('/clear', { method: 'POST' });
            chatMessages.innerHTML = '<div class="message assistant-message"><p>👋 Chat cleared! Ready for a new conversation.</p></div>';
            chartContainer.style.display = 'none';
            emptyState.style.display = 'flex';
            emptyState.flexDirection = 'column';
            emptyState.justifyContent = 'center';
            emptyState.alignItems = 'center';
        } catch (error) {
            console.error('Error clearing history:', error);
        }
    }
}

function setStatus(status) {
    statusIndicator.className = 'status-indicator';
    if (status === 'loading') {
        statusIndicator.classList.add('loading');
    } else if (status === 'error') {
        statusIndicator.classList.add('error');
        setTimeout(() => statusIndicator.classList.remove('error'), 3000);
    }
}

// Focus on input on load
window.addEventListener('load', () => {
    messageInput.focus();
});
