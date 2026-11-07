import random
import tkinter as tk
from tkinter import ttk
import chess

import chessAI  

PIECE_GLYPHS = {
    (chess.WHITE, chess.KING): "♔",
    (chess.WHITE, chess.QUEEN): "♕",
    (chess.WHITE, chess.ROOK): "♖",
    (chess.WHITE, chess.BISHOP): "♗",
    (chess.WHITE, chess.KNIGHT): "♘",
    (chess.WHITE, chess.PAWN): "♙",
    (chess.BLACK, chess.KING): "♚",
    (chess.BLACK, chess.QUEEN): "♛",
    (chess.BLACK, chess.ROOK): "♜",
    (chess.BLACK, chess.BISHOP): "♝",
    (chess.BLACK, chess.KNIGHT): "♞",
    (chess.BLACK, chess.PAWN): "♟",
}


class ChessGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Chess")
        self.root.minsize(480, 520)
        self.root.configure(bg="#f4f1e8")

        self.board = chess.Board()
        self.selected_square: chess.Square | None = None
        self.last_move: chess.Move | None = None
        self.ai_job: str | None = None
        self.status = tk.StringVar(value="Your turn (White)")

        header = ttk.Frame(root, padding=(16, 12))
        header.pack(fill="x")
        ttk.Label(header, textvariable=self.status, font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(header, text="New game", command=self.new_game).pack(side="right")

        self.canvas = tk.Canvas(root, width=640, height=640, highlightthickness=0, bg="#f4f1e8")
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Configure>", lambda _event: self.draw_board())
        self.draw_board()

    def handle_click(self, event: tk.Event) -> None:
        if self.board.turn != chess.WHITE or self.board.is_game_over() or self.ai_job is not None:
            return

        square_size = min(self.canvas.winfo_width(), self.canvas.winfo_height()) / 8
        left = (self.canvas.winfo_width() - square_size * 8) / 2
        top = (self.canvas.winfo_height() - square_size * 8) / 2
        column = int((event.x - left) // square_size)
        row = int((event.y - top) // square_size)
        if not (0 <= column < 8 and 0 <= row < 8):
            return

        square = chess.square(column, 7 - row)
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece is not None and piece.color == chess.WHITE:
                self.selected_square = square
                self.draw_board()
            return

        moves = [
            move for move in self.board.legal_moves
            if move.from_square == self.selected_square and move.to_square == square
        ]
        if moves:
            move = self.choose_promotion(moves[0]) if moves[0].promotion else moves[0]
            self.board.push(move)
            print ("in human move", {chessAI.material_evaluation(self.board)})
            self.last_move = move
            self.selected_square = None
            self.draw_board()
            if self.board.is_game_over():
                self.update_status()
            else:
                self.status.set("Opponent is thinking...")
                self.ai_job = self.root.after(250, self.play_opponent_move)
            return

        piece = self.board.piece_at(square)
        self.selected_square = square if piece is not None and piece.color == chess.WHITE else None
        self.draw_board()
        
        

    def choose_promotion(self, move: chess.Move) -> chess.Move:
        dialog = tk.Toplevel(self.root)
        dialog.title("Promote pawn")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.grab_set()
        ttk.Label(dialog, text="Choose a piece:", padding=(12, 12, 12, 4)).pack()

        choice = tk.IntVar(value=chess.QUEEN)

        def select_piece(piece_type: chess.PieceType) -> None:
            choice.set(piece_type)
            dialog.destroy()

        buttons = ttk.Frame(dialog, padding=(8, 4, 8, 10))
        buttons.pack()
        for piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT):
            ttk.Button(
                buttons,
                text=PIECE_GLYPHS[(chess.WHITE, piece_type)],
                command=lambda selected=piece_type: select_piece(selected),
                width=4,
            ).pack(side="left", padx=2)

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        self.root.wait_window(dialog)
        return chess.Move(move.from_square, move.to_square, promotion=choice.get())

    def play_opponent_move(self) -> None:
        self.ai_job = None
        if self.board.is_game_over():
            self.update_status()
            return

        #replace this with own AI move
        move = chessAI.AI_move(list(self.board.legal_moves), self.board) #random.choice(list(self.board.legal_moves))
        self.board.push(move)
        self.last_move = move
        self.draw_board()
        if self.board.is_game_over():
            self.update_status()
        else:
            self.status.set(f"Opponent played {move.uci()}. Your turn (White)")

    def update_status(self) -> None:
        if self.board.is_game_over():
            self.status.set(f"Game over: {self.board.result()}")

    def new_game(self) -> None:
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None
        self.board.reset()
        self.selected_square = None
        self.last_move = None
        self.status.set("Your turn (White)")
        self.draw_board()

    def draw_board(self) -> None:
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        square_size = min(width, height) / 8
        left = (width - square_size * 8) / 2
        top = (height - square_size * 8) / 2
        legal_targets = {
            move.to_square for move in self.board.legal_moves
            if move.from_square == self.selected_square
        } if self.selected_square is not None else set()

        for row in range(8):
            for column in range(8):
                square = chess.square(column, 7 - row)
                x1 = left + column * square_size
                y1 = top + row * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                color = "#eeeedd" if (row + column) % 2 == 0 else "#769656"
                if self.last_move is not None and square in (self.last_move.from_square, self.last_move.to_square):
                    color = "#f6f669" if (row + column) % 2 == 0 else "#baca44"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                if square == self.selected_square:
                    self.canvas.create_rectangle(
                        x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="#e28b20", width=4
                    )
                if square in legal_targets:
                    radius = square_size * 0.11
                    self.canvas.create_oval(
                        (x1 + x2) / 2 - radius, (y1 + y2) / 2 - radius,
                        (x1 + x2) / 2 + radius, (y1 + y2) / 2 + radius,
                        fill="#34352f", outline="",
                    )

                piece = self.board.piece_at(square)
                if piece is not None:
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    glyph = PIECE_GLYPHS[(piece.color, piece.piece_type)]
                    font = ("Segoe UI Symbol", max(24, int(square_size * 0.68)))
                    if piece.color == chess.WHITE:
                        for offset_x, offset_y in (
                            (-1, -1), (-1, 0), (-1, 1),
                            (0, -1), (0, 1),
                            (1, -1), (1, 0), (1, 1),
                        ):
                            self.canvas.create_text(
                                center_x + offset_x,
                                center_y + offset_y,
                                text=glyph,
                                font=font,
                                fill="#000000",
                            )
                        fill = "#ffffff"
                    else:
                        fill = "#000000"
                    self.canvas.create_text(
                        center_x,
                        center_y,
                        text=glyph,
                        font=font,
                        fill=fill,
                    )

        self.canvas.create_rectangle(left, top, left + square_size * 8, top + square_size * 8,
                                     outline="#34352f", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    ChessGame(root)
    root.mainloop()