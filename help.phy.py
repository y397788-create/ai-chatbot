import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

ai =  genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat = ai.chats.create(
    model="gemini-3.5-flash-lite",
    config={
        "system_instruction": """
Answer ONLY the user's question.
Do not greet the user.
Do not add unrelated information.
"""
    }
)

while True:
    question = input("Ask me anything: ")

    if question.lower() == "exit":
        break

    response = chat.send_message(question)

    print("Answer:", response.text)