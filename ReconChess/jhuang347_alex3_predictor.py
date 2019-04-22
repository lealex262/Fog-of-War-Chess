import chess
import numpy as np

class Predictor(object):
    
    def __init__(self, color):
        # Setup Board
        self.predicted_board = chess.Board()
        self.your_board = None
        self.mycolor = color
        if self.mycolor == chess.WHITE:
            self.opponentcolor = chess.BLACK
        else:
            self.opponentcolor = chess.WHITE

        # Set Up Pieces
        self.idx2pieces = list()
        self.idx2pieces.append((chess.ROOK, 1))
        self.idx2pieces.append((chess.KNIGHT, 1))
        self.idx2pieces.append((chess.BISHOP, 1))
        self.idx2pieces.append((chess.QUEEN, 1))
        self.idx2pieces.append((chess.KING, 1))
        self.idx2pieces.append((chess.BISHOP, 2))
        self.idx2pieces.append((chess.KNIGHT, 2))
        self.idx2pieces.append((chess.ROOK, 2))
        for ii in range(8, 16):
            self.idx2pieces.append((chess.PAWN, ii - 7))

        # Setup Probabilies
        self.probability_board = np.zeros((16, 8, 8), dtype=np.float)
        for jj in range(0, 2):
            for ii in range(0, 8):
                self.probability_board[((jj * 8) + ii), ii, jj] = 1.0

        # Check Color
        if color == chess.WHITE:
            self.probability_board = np.flip(self.probability_board, axis=2)

        # Map 2 Games pieces
        self.update_piece_location_dict()

        
    def get_predicted_board(self):
        return self.predicted_board


    def set_predicted_board(self, board):
        self.predicted_board = board


    def set_your_board(self, board):
        self.predicted_board = board


    def update_piece_location_dict(self):
        self.loc2piece_idx = dict()
        self.piece_idx2loc = np.ones((16, 2), dtype=np.int) * -1

        # Save Positions
        for ii in range(16):
            position = np.unravel_index(self.probability_board[ii].argmax(), (8, 8))
            if self.probability_board[ii, position[0], position[1]] == 0.0:
                position = (-1, -1)
            self.loc2piece_idx[position] = ii
            self.piece_idx2loc[ii] = np.array(position)


    # Set predicted board with the stored positional values
    def set_pieces_position(self, board):
        self.set_your_pieces_position(board)
        self.set_opponent_pieces_position()


    # Clear and Set Your Pieces
    def set_your_pieces_position(self, board):
        self.set_predicted_board(board)


    def set_opponent_pieces_position(self):
        
        for ii in range(0, 16):
            position = self.piece_idx2loc[ii]

            # Check if Alive
            if position != (-1, -1):
                piece = chess.piece(self.idx2pieces[ii][0], self.opponentcolor)
                square = self.point2square(position)

                # Set Piece
                self.predicted_board.set_piece_at(square, piece)



    def update_opponent_move(self, captured_piece, captured_square):
        
        pass


    def opponent_prob_step(self):
        # Generate Legal Moves
        self.predicted_board.turn = self.opponentcolor
        legal_moves = [mm for mm in self.predicted_board.legal_moves]
        num_legal_moves = len(legal_moves)

        # Convert Points
        moves_by_piece = [list() for ii in range(0, 16)]
        for move in legal_moves:
            s_point = move.from_square
            d_point = move.to_square

            # Split legal to individual Pieces
            position = self.square2point(s_point)
            idx = self.loc2piece_idx[position]
            moves_by_piece[idx].append(d_point)

        # HMM on each Piece
        action_prob = 1.0/num_legal_moves
        for ii in range(0, 16):

            # Values
            moves = moves_by_piece[ii]
            if len(moves) != 0:
                s_position = self.piece_idx2loc[ii]
                s_position_prob = self.probability_board[ii, s_position[0], s_position[1]]

                # Loop on Actions
                for move in moves:
                    t_position = self.square2point(move)
                    self.probability_board[ii, t_position[0], t_position[1]] += action_prob * s_position_prob

                # Prob of staying
                self.probability_board[ii, s_position[0], s_position[1]] += s_position_prob * (1 - (action_prob * len(moves)))
            
                # Normalize Probability
                p_sum = np.sum(self.probability_board[ii])
                self.probability_board[ii] /= p_sum



    def square2point(self, square):
        return (square % 8, square // 8)


    def point2square(self, point):
        return (point[1] * 8) + point[0]


    def update_your_move(self, board, success, taken_move, captured_piece, captured_square):
        if success:
            self.set_your_board(board)
            
            if captured_piece:
                pass
        else:
            pass


    def update_sense(self, sense):
        pass
        



def main():
    # TEST
    predictor = Predictor(chess.BLACK)

    predictor.opponent_prob_step()
    print(predictor.probability_board[8])
    


if __name__ == "__main__":
    main()