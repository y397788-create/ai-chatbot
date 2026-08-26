import os
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

ai = genai.Client(api_key=api_key)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chatbot</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .chat-container {
            width: 95%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.12);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            background: #111827;
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .header h1 {
            font-size: 22px;
        }

        .header p {
            font-size: 13px;
            color: #cbd5e1;
            margin-top: 4px;
        }

        .clear-btn {
            background: #374151;
            color: white;
            border: none;
            padding: 9px 14px;
            border-radius: 8px;
            cursor: pointer;
        }

        .clear-btn:hover {
            background: #4b5563;
        }

        #messages {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            background: #f9fafb;
        }

        .message {
            display: flex;
            margin-bottom: 18px;
        }

        .message.user {
            justify-content: flex-end;
        }

        .bubble {
            max-width: 75%;
            padding: 13px 17px;
            border-radius: 16px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .user .bubble {
            background: #111827;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .ai .bubble {
            background: white;
            color: #1f2937;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        .welcome {
            text-align: center;
            padding: 50px 20px;
            color: #6b7280;
        }

        .welcome h2 {
            color: #111827;
            margin-bottom: 10px;
        }

        .input-area {
            padding: 18px;
            background: white;
            border-top: 1px solid #e5e7eb;
            display: flex;
            gap: 10px;
        }

        #question {
            flex: 1;
            padding: 14px 16px;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            outline: none;
            font-size: 15px;
        }

        #question:focus {
            border-color: #111827;
        }

        #send-btn {
            padding: 0 22px;
            border: none;
            border-radius: 12px;
            background: #111827;
            color: white;
            font-size: 15px;
            cursor: pointer;
        }

        #send-btn:hover {
            background: #1f2937;
        }

        #send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .typing {
            color: #6b7280;
            font-size: 14px;
            padding: 8px 0;
        }

        @media (max-width: 600px) {
            .chat-container {
                width: 100%;
                height: 100vh;
                border-radius: 0;
            }

            .bubble {
                max-width: 85%;
            }

            .header h1 {
                font-size: 18px;
            }

            #messages {
                padding: 15px;
            }
        }
    </style>
</head>

<body>

<div class="chat-container">

    <div class="header">
        <div>
            <h1>🤖 AI Chatbot</h1>
            <p>Powered by Gemini AI</p>
        </div>

        <button class="clear-btn" onclick="clearChat()">
            Clear
        </button>
    </div>

    <div id="messages">

        <div class="welcome" id="welcome">
            <h2>How can I help you?</h2>
            <p>Ask me anything and I'll try my best to help.</p>
        </div>

    </div>

    <div class="input-area">

        <input
            id="question"
            type="text"
            placeholder="Ask me anything..."
            autocomplete="off"
        >

        <button id="send-btn" onclick="sendMessage()">
            Send
        </button>

    </div>

</div>

<script>

const input = document.getElementById("question");
const messages = document.getElementById("messages");
const sendBtn = document.getElementById("send-btn");

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function addMessage(text, type) {

    const welcome = document.getElementById("welcome");

    if (welcome) {
        welcome.remove();
    }

    const message = document.createElement("div");
    message.className = "message " + type;

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    bubble.textContent = text;

    message.appendChild(bubble);
    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {

    const question = input.value.trim();

    if (!question) return;

    addMessage(question, "user");

    input.value = "";
    sendBtn.disabled = true;
    sendBtn.textContent = "Thinking...";

    const typing = document.createElement("div");
    typing.className = "typing";
    typing.id = "typing";
    typing.textContent = "AI is thinking...";
    messages.appendChild(typing);

    messages.scrollTop = messages.scrollHeight;

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        const typingElement = document.getElementById("typing");

        if (typingElement) {
            typingElement.remove();
        }

        if (data.answer) {
            addMessage(data.answer, "ai");
        } else {
            addMessage("Sorry, something went wrong.", "ai");
        }

    } catch (error) {

        const typingElement = document.getElementById("typing");

        if (typingElement) {
            typingElement.remove();
        }

        addMessage(
            "Unable to connect to the server. Please try again.",
            "ai"
        );

    }

    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
    input.focus();
}

function clearChat() {

    messages.innerHTML = `
        <div class="welcome" id="welcome">
            <h2>How can I help you?</h2>
            <p>Ask me anything and I'll try my best to help.</p>
        </div>
    `;
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "answer": "Please enter a question."
        })

    try:

        response = ai.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=question
        )

        return jsonify({
            "answer": response.text
        })

    except Exception as e:

        return jsonify({
            "answer": "Sorry, I could not process your request."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)