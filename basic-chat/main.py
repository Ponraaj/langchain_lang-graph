import os
from dotenv import load_dotenv
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
client = firestore.Client(project=PROJECT_ID)

chat_history = FirestoreChatMessageHistory(
    session_id="Testing", collection="chat_history", client=client
)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
print("Previous chat\n", chat_history)
print("\nStart talking with AI. Type 'exit' to quit")

while True:
    msg = input("User: ")
    if msg.lower() == "exit":
        break

    chat_history.add_user_message(msg)

    ai_res = llm.invoke(chat_history.messages)
    chat_history.add_ai_message(ai_res.content)

    print(f"AI: {ai_res.content}")
