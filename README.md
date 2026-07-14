# Omu — Personal AI Assistant with Memory

Everything here is free and runs locally on your machine. No cloud accounts, no API keys.

## What you already have
- Ollama installed, with `llama3.1:8b` pulled and stored on your `D:` drive.

## Setup (one-time)

1. Put these files in a folder, e.g. `D:\Omu\`
   - `main.py`
   - `memory.py`
   - `llm.py`
   - `requirements.txt`

2. Open Command Prompt and go to that folder:
   ```
   cd D:\Omu
   ```

3. Create a virtual environment (keeps packages tidy, optional but recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   This downloads chromadb, sentence-transformers, and requests — all free, no accounts needed.

## Running Omu

1. Make sure Ollama is running (check the system tray icon, or just run `ollama list` in a terminal — if it returns without error, it's running).

2. In your Omu folder, run:
   ```
   python main.py
   ```

3. Chat with Omu in the terminal. Type `exit` to quit.

## How the memory works

- Every time you talk to Omu, the conversation is saved into a local database folder called `omu_memory_db` (created automatically next to your script).
- Next time you ask something related, Omu searches that database for relevant past exchanges and includes them as context before generating its reply.
- This is what gives the *feeling* of Omu "remembering" you over time — no fine-tuning needed.

## Next steps once this works

- Swap the terminal input/output for a simple GUI (e.g. using `customtkinter` or a small FastAPI + React web page)
- Add voice input/output (e.g. `SpeechRecognition` + `pyttsx3`, both free)
- Add "skills" — e.g. functions Omu can call for weather, opening apps, web search, etc.

Let me know once you've got this running and we can build the next layer.
Built by Chitranshu
