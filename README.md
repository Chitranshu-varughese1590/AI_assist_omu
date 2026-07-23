# Omu — Omnimind Utility

A local-first AI assistant that runs entirely on your machine. No cloud API keys, no subscriptions, no sending your conversations anywhere. Omu talks to a local LLM through Ollama, remembers past conversations using a vector database, and comes with both a terminal interface and a polished desktop GUI with voice input/output.

![Omu](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.10+-blue)

---

## Features

- **100% local inference** — powered by [Ollama](https://ollama.com) running `llama3.2:3b`, no internet required after setup
- **Long-term memory** — every exchange is embedded and stored in ChromaDB, so Omu recalls relevant past conversations as context for new ones
- **Desktop GUI** — built with CustomTkinter: chat bubbles, live status indicator (ready / thinking / listening), typing animation, mute toggle, and a pulsing mic button
- **Voice in & out** — speech-to-text input and text-to-speech replies, both running on background threads so the UI never freezes
- **Terminal mode** — a lightweight CLI (`main.py`) for chatting with Omu without the GUI
- **Persistent memory** — conversations are saved to disk (ChromaDB) and survive restarts

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM inference | Ollama (`llama3.2:3b`) |
| Memory / vector store | ChromaDB |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| GUI | CustomTkinter |
| Voice input | SpeechRecognition |
| Voice output | pyttsx3 |
| Concurrency | Python `threading` |

---

## Project Structure

```
omu/
├── main.py       # Terminal entry point
├── gui.py        # Desktop GUI entry point
├── memory.py     # ChromaDB-backed long-term memory
├── llm.py        # Ollama API wrapper
├── voice.py      # Text-to-speech
├── listen.py     # Speech-to-text
└── omu_memory_db/  # Persisted vector DB (created on first run)
```

---

## Setup

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running

### 2. Pull the model
```bash
ollama pull llama3.2:3b
```

### 3. Install dependencies
```bash
pip install customtkinter chromadb sentence-transformers requests SpeechRecognition pyttsx3 pyaudio
```

> **Note:** On first run, `sentence-transformers` downloads the embedding model from Hugging Face Hub. You may see a warning about unauthenticated requests — this is harmless, but if you want to avoid it, set an `HF_TOKEN` environment variable with a free [Hugging Face token](https://huggingface.co/settings/tokens).

### 4. Run Omu

**Desktop GUI:**
```bash
python gui.py
```

**Terminal mode:**
```bash
python main.py
```

---

## How It Works

1. **You send a message** — typed or spoken (via the mic button / `v` in terminal mode).
2. **Memory recall** — Omu embeds your message and queries ChromaDB for the most relevant past exchanges.
3. **LLM call** — your message plus the recalled context is sent to the local Ollama model.
4. **Response** — Omu replies in the chat window (and optionally speaks it aloud), and the exchange is saved back into memory for future recall.

---

## Known Limitations

- Model size is capped at `llama3.2:3b` to stay within 16GB RAM systems — larger models (e.g. `llama3.1:8b`) give richer answers but may cause slowdowns or crashes on lower-memory machines.
- Voice recognition accuracy depends on `SpeechRecognition`'s backend and microphone quality.
- No multi-user support — memory is a single local ChromaDB instance per install.

---

## Roadmap

- [ ] Model auto-selection based on available system RAM
- [ ] Conversation export (Markdown/JSON)
- [ ] Plugin system for tool use (web search, file access, etc.)
- [ ] Cross-platform packaging (Windows/macOS/Linux installers)

---

