import requests
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_MODEL_NAME_GPT4 = os.getenv("AZURE_OPENAI_MODEL_NAME_GPT4")


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

    content = response["message"]["content"]
    return content


def call_openai(model: str, system_message: str, user_message: str):

    if "gpt-4" in model:
        model = OPENAI_MODEL_NAME_GPT4

    client = AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_KEY,
        api_version="2024-02-15-preview",
    )
    message_text = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=message_text,
        temperature=0.0,
        max_tokens=28000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    return completion.choices[0].message.content
