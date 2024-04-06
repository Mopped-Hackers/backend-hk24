import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")


def call_ollama(model: str, system_message: str, user_message: str):
    url = f"{OLLAMA_API_URL}/api/chat"
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }
    response = requests.post(url, json=body)
    response = response.json()

    # TODO dump into mongodb

    content = response["message"]['content']
    return content

