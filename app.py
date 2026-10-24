from flask import Flask, request, jsonify, render_template_string
from chatbot import CostOptimizerChatbot
from bigquery_client import BigQueryClient
from config import Config
import json

app = Flask(__name__)

# Initialize chatbot
print("???? Initializing chatbot...")
Config.validate()
chatbot = CostOptimizerChatbot()
bq_client = BigQueryClient()
print(" Chatbot ready!")

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCP Cost Optimizer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            background: linear-gradient(135deg, #4285F4 0%, #34A853 100%);
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4285F4;
        }
        
        .chat-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            height: 600px;
        }
        
        .chat-header {
            background: #4285F4;
            color: white;
            padding: 20px;
            border-radius: 15px 15px 0 0;
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 20px;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message-user {
            text-align: right;
        }
        
        .message-content {
            display: inline-block;
            max-width: 70%;
            padding: 15px 20px;
            border-radius: 20px;
            margin-bottom: 5px;
        }
        
        .message-user .message-content {
            background: #4285F4;
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .message-bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #ddd;
            border-bottom-left-radius: 5px;
            text-align: left;
            white-space: pre-wrap;
        }
        
        .message-time {
            font-size: 0.75rem;
            color: #999;
            margin-top: 5px;
        }
        
        .chat-input-container {
            padding: 20px;
            border-top: 1px solid #ddd;
            background: white;
            border-radius: 0 0 15px 15px;
        }
        
        .quick-queries {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .quick-query-btn {
            padding: 8px 15px;
            background: #f1f3f4;
            border: 1px solid #ddd;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.3s;
        }
        
        .quick-query-btn:hover {
            background: #4285F4;
            color: white;
            border-color: #4285F4;
        }
        
        .input-wrapper {
            display: flex;
            gap: 10px;
        }
        
        #user-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        #user-input:focus {
            border-color: #4285F4;
        }
        
        #send-btn {
            padding: 15px 30px;
            background: #4285F4;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
            font-weight: bold;
        }
        
        #send-btn:hover {
            background: #357ae8;
        }
        
        #send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #f5c6cb;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .chat-container {
                height: 500px;
            }
            
            .quick-queries {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1> GCP Cost Optimizer</h1>
            <p>AI-Powered Cloud Cost Analysis & Recommendations</p>
        </div>
        
        <!-- Dashboard Metrics -->
        <div class="dashboard" id="dashboard">
            <div class="metric-card">
                <div class="metric-label"> Total Cost</div>
                <div class="metric-value" id="total-cost">Loading...</div>
            </div>
            <div class="metric-card">
                <div class="metric-label"> Projects</div>
                <div class="metric-value" id="total-projects">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label"> Services</div>
                <div class="metric-value" id="total-services">-</div>
            </div>
            <div class="metric-card">
                <div class="metric-label"> Savings Potential</div>
                <div class="metric-value" style="color: #34A853;">15-20%</div>
            </div>
        </div>
        
        <!-- Chat Container -->
        <div class="chat-container">
            <div class="chat-header">
                 Cost Optimization Assistant
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message message-bot">
                    <div class="message-content">
                         Hello! I'm your GCP Cost Optimization Assistant.<br><br>
                        I can help you:<br>
                        • Analyze your cloud spending<br>
                        • Identify cost drivers<br>
                        • Suggest optimization strategies<br>
                        • Recommend GCP cost-saving features<br><br>
                        Try asking: "What are my top cost drivers?"
                    </div>
                    <div class="message-time">Just now</div>
                </div>
            </div>
            
            <div class="chat-input-container">
                <!-- Quick Query Buttons -->
                <div class="quick-queries">
                    <button class="quick-query-btn" onclick="sendQuickQuery('What are my top 5 cost drivers?')">
                         Top Cost Drivers
                    </button>
                    <button class="quick-query-btn" onclick="sendQuickQuery('How can I reduce Compute Engine costs?')">
                         Optimize Compute
                    </button>
                    <button class="quick-query-btn" onclick="sendQuickQuery('Compare production vs development costs')">
                        Compare Projects
                    </button>
                    <button class="quick-query-btn" onclick="sendQuickQuery('Suggest committed use discounts')">
                         Savings Tips
                    </button>
                </div>
                
                <!-- Input Box -->
                <div class="input-wrapper">
                    <input 
                        type="text" 
                        id="user-input" 
                        placeholder="Ask about your GCP costs..."
                        onkeypress="if(event.key==='Enter') sendMessage()"
                    >
                    <button id="send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load dashboard on page load
        window.onload = function() {
            loadDashboard();
        };
        
        function loadDashboard() {
            fetch('/api/dashboard')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('total-cost').textContent = 
                        '$' + data.total_cost.toFixed(2).replace(/\\d(?=(\\d{3})+\\.)/g, '$&,');
                    document.getElementById('total-projects').textContent = data.total_projects;
                    document.getElementById('total-services').textContent = data.total_services;
                })
                .catch(err => console.error('Dashboard error:', err));
        }
        
        function sendQuickQuery(query) {
            document.getElementById('user-input').value = query;
            sendMessage();
        }
        
        function sendMessage() {
            const input = document.getElementById('user-input');
            const query = input.value.trim();
            
            if (!query) return;
            
            // Add user message
            addMessage('user', query);
            input.value = '';
            
            // Disable send button
            const sendBtn = document.getElementById('send-btn');
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="loading"></span>';
            
            // Add loading message
            const loadingId = addMessage('bot', 'Analyzing your costs...');
            
            // Send to API
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            })
            .then(res => res.json())
            .then(data => {
                // Remove loading message
                document.getElementById(loadingId).remove();
                
                // Add AI response
                if (data.status === 'success') {
                    addMessage('bot', data.analysis);
                    
                    // Update dashboard
                    if (data.metadata) {
                        document.getElementById('total-cost').textContent = 
                            '$' + data.metadata.total_cost.toFixed(2).replace(/\\d(?=(\\d{3})+\\.)/g, '$&,');
                        document.getElementById('total-projects').textContent = data.metadata.total_projects;
                        document.getElementById('total-services').textContent = data.metadata.total_services;
                    }
                } else {
                    addMessage('bot', ' Error: ' + data.message);
                }
            })
            .catch(err => {
                document.getElementById(loadingId).remove();
                addMessage('bot', ' Connection error. Please try again.');
                console.error('Error:', err);
            })
            .finally(() => {
                // Re-enable send button
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
            });
        }
        
        function addMessage(type, content) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageId = 'msg-' + Date.now();
            
            const messageDiv = document.createElement('div');
            messageDiv.id = messageId;
            messageDiv.className = 'message message-' + type;
            
            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            messageDiv.innerHTML = 
                <div class="message-content">${content}</div>
                <div class="message-time">${time}</div>
            ;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            return messageId;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Render main chat interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'status': 'error', 'message': 'No query provided'}), 400
        
        # Process query
        result = chatbot.process_query(query)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    """Get dashboard metrics."""
    try:
        total = bq_client.get_total_cost()
        projects = bq_client.get_project_breakdown()
        summary = bq_client.get_cost_summary()
        
        services = len(set(item['service_description'] for item in summary))
        
        return jsonify({
            'total_cost': total,
            'total_projects': len(projects),
            'total_services': services
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\\n" + "="*80)
    print(" Starting Flask Web Server...")
    print("="*80)
    print("\\n Access Options:")
    print("   • Local: http://localhost:8080")
    print("   • Cloud Shell: Use Web Preview on port 8080")
    print("\\n Press Ctrl+C to stop\\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
