import chess
import numpy as np

class Predictor(Object):
    
    def __init__(self, color):
        self.predicted_board = chess.board()
        self.probability_board = np.zeros((18, 8, 8))
        
        # Set Up Pieces
        self.idx2pieces = dict()
        self.idx2pieces.add(0:(chess.ROOK))
        self.idx2pieces.add(1:(chess.KNIGHT))
        self.idx2pieces.add(2:(chess.BISHOP ))
        self.idx2pieces.add(3:(chess.QUEEN))
        self.idx2pieces.add(4:(chess.KING))
        self.idx2pieces.add(5:(chess.BISHOP ))
        self.idx2pieces.add(6:(chess.KNIGHT))
        self.idx2pieces.add(7:(chess.ROOK))
        for ii in range(8, 16):
            self.idx2pieces.add(ii:(chess.PAWN))


        self.color = color

    def get_predicted_board(self):
        return self.predicted_board

    def predicted()


