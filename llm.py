"""
llm.py — talks to your local Ollama model.

Assumes Ollama is already running in the background (it starts automatically
after install, and stays running via the system tray).
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"  


def ask_llm(prompt, memory_context=None):
    """
    Send a prompt to Ollama, optionally injecting relevant memory as context.
    Returns the model's reply as a string.
    """
    if memory_context:
        context_text = "\n".join(memory_context)
        full_prompt = (
            "You are Omu, a helpful personal AI assistant. "
            "Here are some relevant past conversations for context:\n"
            f"{context_text}\n\n"
            f"Now respond to this new message:\n{prompt}"
        )
    else:
        full_prompt = (
            "You are Omu, a helpful personal AI assistant.\n"
            f"User: {prompt}"
        )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False,
        },
        timeout=300,
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print(f"Ollama error response: {response.text}")
        raise
    return response.json()["response"].strip()
