import chess

PIECE_VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0,
}


class ChessAI:
    def __init__(self, depth=3):
        self.depth = depth

    def evaluate(self, board: chess.Board) -> int:
        if board.is_checkmate():
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        for square, piece in board.piece_map().items():
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
        return score

    def minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)

        if maximizing:
            value = -float("inf")
            for move in board.legal_moves:
                board.push(move)
                value = max(value, self.minimax(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float("inf")
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self.minimax(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def choose_move(self, board: chess.Board) -> chess.Move:
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            raise ValueError("No legal moves — game is already over.")
        if len(legal_moves) == 1:
            return legal_moves[0]

        best_move = None
        best_score = -float("inf") if board.turn == chess.WHITE else float("inf")
        maximizing = board.turn == chess.WHITE

        for move in legal_moves:
            board.push(move)
            score = self.minimax(board, self.depth - 1, -float("inf"), float("inf"), not maximizing)
            board.pop()

            if maximizing and score > best_score:
                best_score, best_move = score, move
            elif not maximizing and score < best_score:
                best_score, best_move = score, move

        return best_move


if __name__ == "__main__":
        board = chess.Board()
        ai = ChessAI(depth=3)

        for i in range(6): 
            move = ai.choose_move(board)
            board.push(move)
            print(f"Move {i+1}:{move}")
            print(board,"\n")