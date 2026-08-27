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

    <title>My AI Assistant</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f7f7f8;
            color: #111827;
            height: 100vh;
            overflow: hidden;
        }

        body.dark {
            background: #212121;
            color: #ffffff;
        }

        .app {
            display: flex;
            height: 100vh;
        }

        /* SIDEBAR */

        .sidebar {
            width: 260px;
            background: #111827;
            color: white;
            padding: 15px;
            display: flex;
            flex-direction: column;
            transition: 0.3s;
        }

        .brand {
            font-size: 20px;
            font-weight: bold;
            padding: 12px;
            margin-bottom: 15px;
        }

        .new-chat {
            width: 100%;
            padding: 12px;
            background: #374151;
            border: 1px solid #4b5563;
            color: white;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 15px;
        }

        .new-chat:hover {
            background: #4b5563;
        }

        .history-title {
            font-size: 12px;
            color: #9ca3af;
            margin: 10px 5px;
        }

        #history {
            flex: 1;
            overflow-y: auto;
        }

        .history-item {
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .history-item:hover {
            background: #374151;
        }

        .theme-btn {
            padding: 11px;
            border: none;
            border-radius: 9px;
            background: #374151;
            color: white;
            cursor: pointer;
        }

        /* MAIN */

        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }

        .topbar {
            height: 60px;
            padding: 0 20px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #e5e7eb;
            background: white;
        }

        body.dark .topbar {
            background: #212121;
            border-color: #3f3f3f;
        }

        .topbar h2 {
            font-size: 18px;
        }

        .menu-btn {
            display: none;
            margin-right: 15px;
            border: none;
            background: none;
            font-size: 24px;
            cursor: pointer;
        }

        body.dark .menu-btn {
            color: white;
        }

        /* CHAT */

        #messages {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
        }

        .welcome {
            text-align: center;
            margin-top: 15vh;
        }

        .welcome h1 {
            font-size: 30px;
            margin-bottom: 10px;
        }

        .welcome p {
            color: #6b7280;
        }

        .message {
            max-width: 850px;
            margin: 0 auto 22px;
            display: flex;
        }

        .message.user {
            justify-content: flex-end;
        }

        .bubble {
            max-width: 75%;
            padding: 13px 17px;
            border-radius: 15px;
            line-height: 1.55;
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
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        body.dark .ai .bubble {
            background: #2f2f2f;
            border-color: #444;
            color: white;
        }

        .copy-btn {
            margin-left: 8px;
            align-self: flex-end;
            border: none;
            background: transparent;
            cursor: pointer;
            opacity: 0.6;
        }

        body.dark .copy-btn {
            color: white;
        }

        /* INPUT */

        .input-wrapper {
            padding: 15px 20px 20px;
            background: #f7f7f8;
        }

        body.dark .input-wrapper {
            background: #212121;
        }

        .input-box {
            max-width: 850px;
            margin: auto;
            display: flex;
            gap: 10px;
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 15px;
            padding: 8px;
        }

        body.dark .input-box {
            background: #2f2f2f;
            border-color: #555;
        }

        #question {
            flex: 1;
            border: none;
            outline: none;
            padding: 10px;
            font-size: 15px;
            background: transparent;
            color: inherit;
        }

        #send-btn {
            border: none;
            background: #111827;
            color: white;
            padding: 0 20px;
            border-radius: 10px;
            cursor: pointer;
        }

        #send-btn:disabled {
            opacity: 0.5;
        }

        .typing {
            max-width: 850px;
            margin: 0 auto 15px;
            color: #6b7280;
            font-size: 14px;
        }

        /* MOBILE */

        @media (max-width: 700px) {

            .sidebar {
                position: fixed;
                left: -270px;
                top: 0;
                bottom: 0;
                z-index: 10;
            }

            .sidebar.open {
                left: 0;
            }

            .menu-btn {
                display: block;
            }

            #messages {
                padding: 20px 12px;
            }

            .bubble {
                max-width: 88%;
            }

            .welcome h1 {
                font-size: 24px;
            }
        }
    </style>
</head>

<body>

<div class="app">

    <aside class="sidebar" id="sidebar">

        <div class="brand">
            🤖 My AI Assistant
        </div>

        <button class="new-chat" onclick="newChat()">
            + New Chat
        </button>

        <div class="history-title">
            CHAT HISTORY
        </div>

        <div id="history"></div>

        <button class="theme-btn" onclick="toggleTheme()">
            🌙 Dark / ☀️ Light
        </button>

    </aside>

    <main class="main">

        <header class="topbar">

            <button class="menu-btn" onclick="toggleSidebar()">
                ☰
            </button>

            <h2>AI Assistant</h2>

        </header>

        <div id="messages">

            <div class="welcome" id="welcome">
                <h1>👋 How can I help you?</h1>
                <p>Ask me anything and I'll try my best to help.</p>
            </div>

        </div>

        <div class="input-wrapper">

            <div class="input-box">

                <input
                    id="question"
                    type="text"
                    placeholder="Message AI Assistant..."
                    autocomplete="off"
                >

                <button id="send-btn" onclick="sendMessage()">
                    Send
                </button>

            </div>

        </div>

    </main>

</div>

<script>

const input = document.getElementById("question");
const messages = document.getElementById("messages");
const sendBtn = document.getElementById("send-btn");
const history = document.getElementById("history");

let chats = JSON.parse(localStorage.getItem("ai_chats") || "[]");

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

    if (type === "ai") {

        const copy = document.createElement("button");

        copy.className = "copy-btn";
        copy.textContent = "📋";

        copy.onclick = function() {
            navigator.clipboard.writeText(text);
            copy.textContent = "✅";

            setTimeout(function() {
                copy.textContent = "📋";
            }, 1500);
        };

        message.appendChild(copy);
    }

    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {

    const question = input.value.trim();

    if (!question) {
        return;
    }

    addMessage(question, "user");

    input.value = "";

    sendBtn.disabled = true;
    sendBtn.textContent = "Thinking...";

    const typing = document.createElement("div");

    typing.className = "typing";
    typing.id = "typing";
    typing.textContent = "🤖 AI is thinking...";

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

        addMessage(
            data.answer || "Sorry, I couldn't generate a response.",
            "ai"
        );

        saveChat(question, data.answer);

    } catch (error) {

        const typingElement = document.getElementById("typing");

        if (typingElement) {
            typingElement.remove();
        }

        addMessage(
            "❌ Unable to connect to the server. Please try again.",
            "ai"
        );

    }

    sendBtn.disabled = false;
    sendBtn.textContent = "Send";

    input.focus();
}

function saveChat(question, answer) {

    chats.unshift({
        question: question,
        answer: answer,
        time: new Date().toLocaleString()
    });

    chats = chats.slice(0, 20);

    localStorage.setItem("ai_chats", JSON.stringify(chats));

    renderHistory();
}

function renderHistory() {

    history.innerHTML = "";

    chats.forEach(function(chat) {

        const item = document.createElement("div");

        item.className = "history-item";

        item.textContent = chat.question;

        item.onclick = function() {

            messages.innerHTML = "";

            addMessage(chat.question, "user");
            addMessage(chat.answer, "ai");

        };

        history.appendChild(item);

    });
}

function newChat() {

    messages.innerHTML = `
        <div class="welcome" id="welcome">
            <h1>👋 How can I help you?</h1>
            <p>Ask me anything and I'll try my best to help.</p>
        </div>
    `;

    input.focus();

    if (window.innerWidth <= 700) {
        document.getElementById("sidebar").classList.remove("open");
    }
}

function toggleTheme() {

    document.body.classList.toggle("dark");

    localStorage.setItem(
        "theme",
        document.body.classList.contains("dark")
        ? "dark"
        : "light"
    );
}

function toggleSidebar() {

    document.getElementById("sidebar")
        .classList.toggle("open");

}

if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
}

renderHistory();

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}

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

    except Exception:

        return jsonify({
            "answer": "Sorry, something went wrong. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )