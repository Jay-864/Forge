import os

from ollama import Client


class OllamaLLM:
    def __init__(self, model: str):
        host = os.getenv("OLLAMA_HOST")

        if not host:
            host = "http://127.0.0.1:11434"

        self.model = model
        self.client = Client(host=host)

        print(f"[Forge] Ollama host: {host}")
        print(f"[Forge] Model: {model}")

    def chat(self, messages, tools=None):
        kwargs = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools

        response = self.client.chat(**kwargs)

        return response.message