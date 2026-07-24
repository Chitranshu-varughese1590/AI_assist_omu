import customtkinter as ctk
import chess
from chess_ai import ChessAI

PIECE_UNICODE = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}

SQUARE_SIZE = 60
LIGHT_COLOR = "#EEEED2"
DARK_COLOR = "#769656"
SELECTED_COLOR = "#F6F669"


class ChessFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.board = chess.Board()
        self.ai = ChessAI(depth=3)
        self.selected_square = None

        self.canvas = ctk.CTkCanvas(
            self, width=SQUARE_SIZE * 8, height=SQUARE_SIZE * 8, highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        self.status_label = ctk.CTkLabel(self, text="Your move (White)")
        self.status_label.pack(pady=(0, 10))

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for rank in range(8):
            for file in range(8):
                x1 = file * SQUARE_SIZE
                y1 = rank * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                square = chess.square(file, 7 - rank)  # rank 0 = top of screen = rank 8
                color = LIGHT_COLOR if (rank + file) % 2 == 0 else DARK_COLOR
                if square == self.selected_square:
                    color = SELECTED_COLOR

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.board.piece_at(square)
                if piece:
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE / 2,
                        y1 + SQUARE_SIZE / 2,
                        text=PIECE_UNICODE[piece.symbol()],
                        font=("Arial", 32),
                    )

    def on_click(self, event):
        if self.board.turn != chess.WHITE or self.board.is_game_over():
            return  # not the player's turn, or game already finished

        file = event.x // SQUARE_SIZE
        rank = 7 - (event.y // SQUARE_SIZE)
        square = chess.square(file, rank)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
                self.draw_board()
        else:
            move = chess.Move(self.selected_square, square)
            if move not in self.board.legal_moves:
                # try auto-queen promotion (e.g. pawn reaching the last rank)
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
            self.try_player_move(move)

    def try_player_move(self, move):
        if move in self.board.legal_moves:
            self.board.push(move)
            self.selected_square = None
            self.draw_board()
            self.check_game_over()
            if not self.board.is_game_over():
                self.status_label.configure(text="Omu is thinking...")
                self.after(300, self.ai_move)  # slight delay so it feels natural
        else:
            self.selected_square = None
            self.draw_board()

    def ai_move(self):
        move = self.ai.choose_move(self.board)
        self.board.push(move)
        self.draw_board()
        self.check_game_over()
        if not self.board.is_game_over():
            self.status_label.configure(text="Your move (White)")

    def check_game_over(self):
        if self.board.is_checkmate():
            winner = "Omu (Black)" if self.board.turn == chess.WHITE else "You (White)"
            self.status_label.configure(text=f"Checkmate — {winner} wins!")
        elif self.board.is_stalemate():
            self.status_label.configure(text="Stalemate — it's a draw")
        elif self.board.is_insufficient_material():
            self.status_label.configure(text="Draw — insufficient material")