"""
gui.py — a simple desktop window for Omu, built with customtkinter.

- Omu's messages appear in green
- Your messages appear in white
- A separate animated "thinking..." label shows below the chat while waiting,
  and disappears cleanly once the reply arrives (no more duplicate text bug).
"""

import customtkinter as ctk
import threading

from memory import Memory
from llm import ask_llm
from voice import speak

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OMU_COLOR = "#4ADE80"     # green
USER_COLOR = "#F5F5F5"    # near-white


class OmuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Omu — Your AI Assistant")
        self.geometry("600x700")
        self.configure(fg_color="#111827")

        # Load memory once at startup (this can take a few seconds)
        self.memory = Memory()

        # --- Chat display area ---
        self.chat_box = ctk.CTkTextbox(
            self, width=560, height=520, wrap="word",
            font=("Segoe UI", 13), fg_color="#1F2937", corner_radius=10
        )
        self.chat_box.pack(padx=20, pady=(20, 5), fill="both", expand=True)
        self.chat_box.configure(state="disabled")

        self.chat_box.tag_config("omu", foreground=OMU_COLOR)
        self.chat_box.tag_config("user", foreground=USER_COLOR)

        # --- Loading indicator (its own label, separate from the chat text) ---
        self.loading_label = ctk.CTkLabel(self, text="", text_color="#9CA3AF", font=("Segoe UI", 12))
        self.loading_label.pack(padx=20, pady=(0, 5), anchor="w")

        # --- Input row ---
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(padx=20, pady=(0, 20), fill="x")

        self.entry = ctk.CTkEntry(input_frame, placeholder_text="Type a message to Omu...", font=("Segoe UI", 13))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(input_frame, text="Send", width=80, command=self.send_message)
        self.send_button.pack(side="right")

        # Loading animation state
        self._loading = False
        self._loading_dots = 0

        self._append_chat("Omu", "Hi! I'm Omu. Ask me anything.", "omu")

    def _append_chat(self, sender, text, tag):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"{sender}: ", tag)
        self.chat_box.insert("end", f"{text}\n\n", tag)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def _start_loading(self):
        self._loading = True
        self._loading_dots = 0
        self._animate_loading()

    def _animate_loading(self):
        if not self._loading:
            return
        self._loading_dots = (self._loading_dots % 3) + 1
        dots = "." * self._loading_dots
        # This REPLACES the label's text each time — no stacking, no duplication
        self.loading_label.configure(text=f"Omu is thinking{dots}")
        self.after(400, self._animate_loading)

    def _stop_loading(self):
        self._loading = False
        self.loading_label.configure(text="")

    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, "end")
        self._append_chat("You", user_text, "user")

        self.entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self._start_loading()

        threading.Thread(target=self._get_reply, args=(user_text,), daemon=True).start()

    def _get_reply(self, user_text):
        try:
            relevant_memories = self.memory.recall(user_text)
            reply = ask_llm(user_text, memory_context=relevant_memories)
            self.memory.add_memory(user_text, reply)
        except Exception as e:
            reply = f"(Error talking to Ollama: {e})"

        self.after(0, self._show_reply, reply)

    def _show_reply(self, reply):
        self._stop_loading()
        self._append_chat("Omu", reply, "omu")
        self.entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.entry.focus()

        threading.Thread(target=speak, args=(reply,), daemon=True).start()


if __name__ == "__main__":
    app = OmuApp()
    app.mainloop()
