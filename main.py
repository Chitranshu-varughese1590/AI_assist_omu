"""
main.py — Omu's entry point.

Run this to chat with Omu in your terminal. Every exchange is:
  1. Used to recall relevant past memory
  2. Sent to the local LLM (Ollama) along with that memory as context
  3. Saved back into memory for next time

Type 'exit' or 'quit' to stop.
Type 'v' to speak your input instead of typing it.
"""

from memory import Memory
from llm import ask_llm
from voice import speak
from listen import listen_for_speech


def main():
    print("Booting Omu... (loading memory + embedding model, this can take a few seconds)")
    memory = Memory()
    print("Omu is ready. Type 'exit' to quit, or 'v' to speak instead.\n")

    while True:
        raw = input("You (or 'v' for voice): ").strip()

        if raw.lower() in ("exit", "quit"):
            print("Omu: Goodbye!")
            break

        if raw.lower() == "v":
            user_input = listen_for_speech()
            if not user_input:
                continue
        else:
            user_input = raw

        if not user_input:
            continue

        # 1. Recall relevant past context
        relevant_memories = memory.recall(user_input)

        # 2. Ask the LLM, passing in memory as context
        reply = ask_llm(user_input, memory_context=relevant_memories)
        print(f"Omu: {reply}\n")
        speak(reply)

        # 3. Save this exchange for future recall
        memory.add_memory(user_input, reply)


if __name__ == "__main__":
    main()
