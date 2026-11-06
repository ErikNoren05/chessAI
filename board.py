import random

import chess


def play_game() -> None:
    board = chess.Board()

    while not board.is_game_over():
        print()
        print(board)
        print("\nYour move as UCI (for example, e2e4; type 'quit' to exit).")

        try:
            move_text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGame ended.")
            return

        if move_text.lower() in {"quit", "exit"}:
            print("Game ended.")
            return

        try:
            move = chess.Move.from_uci(move_text)
        except ValueError:
            print("Invalid move format. Enter a move such as e2e4.")
            continue

        if move not in board.legal_moves:
            print("That move is not legal. Try again.")
            continue

        board.push(move)
        if board.is_game_over():
            break

        opponent_move = random.choice(list(board.legal_moves))
        board.push(opponent_move)
        print(f"Opponent played: {opponent_move.uci()}")

    print()
    print(board)
    print(f"\nGame over: {board.result()}")


if __name__ == "__main__":
    play_game()