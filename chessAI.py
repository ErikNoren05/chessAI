import random
import chess
import time

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

def AI_move(possible_moves, board):
    # Implement your AI logic here to choose a move
    print("in ai move",  material_evaluation(board))
    time.sleep(2)
    return random.choice(possible_moves)


def evalutation(possible_moves, board):
    eval = 0
    amount_possible_moves = len(possible_moves)
    material_evaluation = material_evaluation(board)
    #opponent_possible_moves = 

def material_evaluation(board):
    piece_evaluation = 0
    for i in range (0, 64, 1):
        piece = board.piece_at(i)
        if piece != None:
            if piece.color == chess.BLACK:
                piece_evaluation = piece_evaluation + PIECE_VALUES[piece.piece_type]
            elif piece.color == chess.WHITE:
                piece_evaluation = piece_evaluation - PIECE_VALUES[piece.piece_type]
    return piece_evaluation