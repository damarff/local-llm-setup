"""Example: Chat with local LLM via API."""

import httpx

API_URL = "http://localhost:8000"


def chat(message: str, model: str = "llama3") -> str:
    """Send a chat message and get response."""
    resp = httpx.post(
        f"{API_URL}/chat/",
        json={
            "message": message,
            "model": model,
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
        },
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def list_models() -> list:
    """List available models."""
    resp = httpx.get(f"{API_URL}/models/")
    resp.raise_for_status()
    return resp.json()["models"]


if __name__ == "__main__":
    # List models
    print("Available models:")
    for m in list_models():
        print(f"  - {m['name']}")

    # Chat
    print("\nChatting with llama3...")
    response = chat("What is the capital of France?")
    print(f"Response: {response}")
