import customtkinter as ctk
from chess_gui import ChessFrame

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.title("Chess Test")

frame = ChessFrame(app)
frame.pack(padx=20, pady=20)

app.mainloop()