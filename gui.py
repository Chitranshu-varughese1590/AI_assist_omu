"""
gui.py — a polished desktop window for Omu, built with customtkinter.

Enhancements over the original:
- Real chat "bubbles" (rounded frames) instead of a single text box, with
  Omu on the left / you on the right, sender label + timestamp on each.
- A status dot in the header (green = ready, amber = thinking) instead of a
  plain text label, plus a live "typing..." bubble that gets swapped out
  cleanly when the reply lands (no duplicate text bug).
- A mic button that turns red and pulses while actively listening.
- A mute/unmute toggle so Omu's spoken replies can be silenced without
  killing the thread every time.
- A "clear chat" button that resets the conversation view.
- Errors render as a distinct red-tinted bubble instead of blending in.
- Auto-scroll to the newest message, resizable window with a sane minsize,
  and Enter-to-send / Escape-to-clear-input shortcuts.
"""

import customtkinter as ctk
import threading
from datetime import datetime

from memory import Memory
from llm import ask_llm
from voice import speak
from listen import listen_for_speech
from chess_gui import ChessFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Palette -----------------------------------------------------------
BG_COLOR = "#0F172A"
PANEL_COLOR = "#111827"
CHAT_BG = "#1F2937"

OMU_BUBBLE = "#14532D"      # deep green
OMU_TEXT = "#4ADE80"        # bright green
USER_BUBBLE = "#374151"     # slate
USER_TEXT = "#F5F5F5"       # near-white
ERROR_BUBBLE = "#7F1D1D"
ERROR_TEXT = "#FCA5A5"
MUTED_TEXT = "#9CA3AF"

STATUS_READY = "#22C55E"
STATUS_BUSY = "#FBBF24"
STATUS_LISTEN = "#EF4444"


class OmuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OMU  Your AI Assistant")
        self.geometry("640x760")
        self.minsize(480, 560)
        self.configure(fg_color=BG_COLOR)

        # Load memory once at startup (this can take a few seconds)
        self.memory = Memory()

        self.voice_enabled = True
        self._loading = False
        self._loading_dots = 0
        self._thinking_bubble = None
        self.chess_window = None

        self._build_header()
        self._build_chat_area()
        self._build_input_row()

        self._add_bubble("Omu", "Hi! I'm OMU . Ask me anything.", is_user=False)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=PANEL_COLOR, height=56, corner_radius=0)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=16)

        self.status_dot = ctk.CTkLabel(
            left, text="●", text_color=STATUS_READY, font=("Segoe UI", 16)
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        title_box = ctk.CTkFrame(left, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(
            title_box, text="Omu", font=("Segoe UI", 16, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w")
        self.status_label = ctk.CTkLabel(
            title_box, text="ready", font=("Segoe UI", 11), text_color=MUTED_TEXT
        )
        self.status_label.pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=16)

        self.mute_button = ctk.CTkButton(
            right, text="🔊", width=36, height=32,
            fg_color="transparent", hover_color="#1F2937",
            command=self.toggle_mute,
        )
        self.mute_button.pack(side="right", padx=(8, 0))

        self.clear_button = ctk.CTkButton(
            right, text="🗑", width=36, height=32,
            fg_color="transparent", hover_color="#1F2937",
            command=self.clear_chat,
        )
        self.clear_button.pack(side="right")

    def _build_chat_area(self):
        self.chat_scroll = ctk.CTkScrollableFrame(
            self, fg_color=CHAT_BG, corner_radius=10
        )
        self.chat_scroll.pack(padx=20, pady=(16, 8), fill="both", expand=True)
        # single-column layout; bubbles are packed top-to-bottom
        self.chat_scroll.grid_columnconfigure(0, weight=1)

    def _build_input_row(self):
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(padx=20, pady=(0, 20), fill="x")

        self.entry = ctk.CTkEntry(
            input_frame, placeholder_text="Type a message to OMU...",
            font=("Segoe UI", 13), height=40,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda event: self.send_message())
        self.entry.bind("<Escape>", lambda event: self.entry.delete(0, "end"))

        self.send_button = ctk.CTkButton(
            input_frame, text="Send", width=80, height=40, command=self.send_message
        )
        self.send_button.pack(side="right")

        self.mic_button = ctk.CTkButton(
            input_frame, text="🎤", width=44, height=40, command=self.start_voice_input
        )
        self.mic_button.pack(side="right", padx=(0, 10))

    # ------------------------------------------------------------------
    # Chat bubbles
    # ------------------------------------------------------------------
    def _add_bubble(self, sender, text, is_user, is_error=False, is_thinking=False):
        """Create a rounded message bubble and return it (so it can be removed later)."""
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4, padx=4)

        if is_error:
            bubble_color, text_color = ERROR_BUBBLE, ERROR_TEXT
        elif is_user:
            bubble_color, text_color = USER_BUBBLE, USER_TEXT
        else:
            bubble_color, text_color = OMU_BUBBLE, OMU_TEXT

        bubble = ctk.CTkFrame(row, fg_color=bubble_color, corner_radius=14)
        # right-align user bubbles, left-align everything else
        bubble.pack(side="right" if is_user else "left", anchor="e" if is_user else "w")

        header_row = ctk.CTkFrame(bubble, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(8, 0))

        ctk.CTkLabel(
            header_row, text=sender, font=("Segoe UI", 11, "bold"), text_color=text_color
        ).pack(side="left")

        if not is_thinking:
            timestamp = datetime.now().strftime("%H:%M")
            ctk.CTkLabel(
                header_row, text=timestamp, font=("Segoe UI", 9), text_color=MUTED_TEXT
            ).pack(side="left", padx=(8, 0))

        body_label = ctk.CTkLabel(
            bubble, text=text, font=("Segoe UI", 13), text_color=text_color,
            wraplength=420, justify="left", anchor="w",
        )
        body_label.pack(fill="x", padx=12, pady=(2, 10), anchor="w")

        self._scroll_to_bottom()
        return row, body_label

    def _scroll_to_bottom(self):
        self.after(30, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

    def clear_chat(self):
        for child in self.chat_scroll.winfo_children():
            child.destroy()
        self._add_bubble("OMU", "Chat cleared. What's next?", is_user=False)

    def open_chess_window(self):
        # If a chess window is already open, just bring it to front instead of
        # spawning a second one.
        if self.chess_window is not None and self.chess_window.winfo_exists():
            self.chess_window.lift()
            return

        self.chess_window = ctk.CTkToplevel(self)
        self.chess_window.title("Chess vs Omu")
        self.chess_window.geometry("520x620")
        self.chess_window.configure(fg_color=BG_COLOR)

        chess_frame = ChessFrame(self.chess_window, fg_color=PANEL_COLOR)
        chess_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # ------------------------------------------------------------------
    # Status / mute helpers
    # ------------------------------------------------------------------
    def _set_status(self, text, color):
        self.status_label.configure(text=text)
        self.status_dot.configure(text_color=color)

    def toggle_mute(self):
        self.voice_enabled = not self.voice_enabled
        self.mute_button.configure(text="🔊" if self.voice_enabled else "🔇")

    # ------------------------------------------------------------------
    # Thinking indicator
    # ------------------------------------------------------------------
    def _start_loading(self):
        self._loading = True
        self._loading_dots = 0
        self._set_status("thinking...", STATUS_BUSY)
        self._thinking_bubble, self._thinking_label = self._add_bubble(
            "OMU", "thinking", is_user=False, is_thinking=True
        )
        self._animate_loading()

    def _animate_loading(self):
        if not self._loading:
            return
        self._loading_dots = (self._loading_dots % 3) + 1
        dots = "." * self._loading_dots
        self._thinking_label.configure(text=f"thinking{dots}")
        self.after(400, self._animate_loading)

    def _stop_loading(self):
        self._loading = False
        if self._thinking_bubble is not None:
            self._thinking_bubble.destroy()
            self._thinking_bubble = None
        self._set_status("ready", STATUS_READY)

    # ------------------------------------------------------------------
    # Sending messages
    # ------------------------------------------------------------------
    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, "end")
        self._add_bubble("You", user_text, is_user=True)

        if user_text.lower() == "chess":
            self._add_bubble("Omu", "Opening the chess board...", is_user=False)
            self.open_chess_window()
            return

        self.entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.mic_button.configure(state="disabled")
        self._start_loading()

        threading.Thread(target=self._get_reply, args=(user_text,), daemon=True).start()

    def _get_reply(self, user_text):
        is_error = False
        try:
            relevant_memories = self.memory.recall(user_text)
            reply = ask_llm(user_text, memory_context=relevant_memories)
            self.memory.add_memory(user_text, reply)
        except Exception as e:
            reply = f"Error talking to Ollama: {e}"
            is_error = True

        self.after(0, self._show_reply, reply, is_error)

    def _show_reply(self, reply, is_error=False):
        self._stop_loading()
        self._add_bubble("Omu", reply, is_user=False, is_error=is_error)
        self.entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.mic_button.configure(state="normal")
        self.entry.focus()

        if self.voice_enabled and not is_error:
            threading.Thread(target=speak, args=(reply,), daemon=True).start()

    # ------------------------------------------------------------------
    # Voice input
    # ------------------------------------------------------------------
    def start_voice_input(self):
        self.entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.mic_button.configure(
            state="disabled", text="●", fg_color=STATUS_LISTEN, hover_color="#DC2626"
        )
        self._set_status("listening...", STATUS_LISTEN)

        threading.Thread(target=self._listen_and_fill, daemon=True).start()

    def _listen_and_fill(self):
        text = listen_for_speech()
        self.after(0, self._on_voice_result, text)

    def _on_voice_result(self, text):
        default_fg = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.mic_button.configure(
            state="normal", text="🎤", fg_color=default_fg, hover_color=("#325882", "#14375e")
        )
        self._set_status("ready", STATUS_READY)

        if text:
            self.entry.delete(0, "end")
            self.entry.insert(0, text)
            self.send_message()
        


if __name__ == "__main__":
    app = OmuApp()
    app.mainloop()
