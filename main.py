"""
main.py — Omu's entry point.

Run this to chat with Omu in your terminal. Every exchange is:
  1. Used to recall relevant past memory
  2. Sent to the local LLM (Ollama) along with that memory as context
  3. Saved back into memory for next time

Type 'exit' or 'quit' to stop.
""""""
main.py — Omu's entry point.

Run this to chat with Omu in your terminal. Every exchange is:
  1. Used to recall relevant past memory
  2. Sent to the local LLM (Ollama) along with that memory as context
  3. Saved back into memory for next time

Type 'exit' or 'quit' to stop.
"""

from memory import Memory
from llm import ask_llm
from voice import speak


def main():
    print("Booting Omu... (loading memory + embedding model, this can take a few seconds)")
    memory = Memory()
    print("Omu is ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Omu: Goodbye!")
            break
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

from memory import Memory
from llm import ask_llm


def main():
    print("Booting Omu... (loading memory + embedding model, this can take a few seconds)")
    memory = Memory()
    print("Omu is ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Omu: Goodbye!")
            break
        if not user_input:
            continue

        # 1. Recall relevant past context
        relevant_memories = memory.recall(user_input)

        # 2. Ask the LLM, passing in memory as context
        reply = ask_llm(user_input, memory_context=relevant_memories)
        print(f"Omu: {reply}\n")

        # 3. Save this exchange for future recall
        memory.add_memory(user_input, reply)


if __name__ == "__main__":
    main()
