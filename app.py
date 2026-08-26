import os
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

ai = genai.Client(api_key=api_key)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Chatbot</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f2f2;
            display: flex;
            justify-content: center;
            padding-top: 50px;
        }

        .chatbox {
            width: 500px;
            background: white;
            padding: 20px;
            border-radius: 10px;
        }

        #messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
        }

        input {
            width: 75%;
            padding: 10px;
        }

        button {
            padding: 10px;
            cursor: pointer;
        }
    </style>
</head>

<body>

<div class="chatbox">
    <h2>🤖 AI Chatbot</h2>

    <div id="messages"></div>

    <input id="question" placeholder="Ask me anything...">
    <button onclick="sendMessage()">Send</button>
</div>

<script>
async function sendMessage() {

    const input = document.getElementById("question");
    const messages = document.getElementById("messages");

    const question = input.value.trim();

    if (!question) return;

    messages.innerHTML += "<p><b>You:</b> " + question + "</p>";

    input.value = "";

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

    messages.innerHTML += "<p><b>AI:</b> " + data.answer + "</p>";
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
    question = data.get("question", "")

    response = ai.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=question
    )

    return jsonify({
        "answer": response.text
    })


if __name__ == "__main__":
    app.run(debug=True)