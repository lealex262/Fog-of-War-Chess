import chess
import numpy as np
import copy

class Predictor(object):
    
    def __init__(self, color):
        # Setup Board
        self.predicted_board = chess.Board()
        white_fen = "8/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        black_fen = "rnbqkbnr/pppppppp/8/8/8/8/8/8 w KQkq - 0 1"
        if color == chess.WHITE:
            self.your_board = chess.Board(white_fen)
        else:
            self.your_board = chess.Board(black_fen)
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

        # Type
        self.piece_type2indices = dict()
        for ii in range(0, 16):
            piece_type = self.idx2pieces[ii][0]
            if piece_type in self.piece_type2indices:
                self.piece_type2indices[piece_type].append(ii)
            else:
                self.piece_type2indices[piece_type] = [ii]

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


    def predict_board(self, your_board):
        self.your_board = your_board
        self.update_piece_location_dict()
        self.set_pieces_position(your_board)
        return self.get_predicted_board()

        
    def get_predicted_board(self):
        return self.predicted_board


    def set_predicted_board(self, board):
        self.predicted_board = board


    def set_your_board(self, board):
        self.your_board = board


    def update_piece_location_dict(self):
        self.loc2piece_idx = dict()
        self.piece_idx2loc = np.ones((16, 2), dtype=np.int) * -1

        # Save Positions
        for ii in range(16):
            position = np.unravel_index(self.probability_board[ii].argmax(), (8, 8))
            
            # Check if dead
            if self.probability_board[ii, position[0], position[1]] == 0.0:
                position = (-1, -1)
            
            # Save
            self.loc2piece_idx[position] = ii
            self.piece_idx2loc[ii] = np.array(position)


    # Set predicted board with the stored positional values
    def set_pieces_position(self, board):
        self.set_your_pieces_position(board)
        self.set_opponent_pieces_position()


    # Clear and Set Your Pieces
    def set_your_pieces_position(self, board):
        # self.set_predicted_board(copy.deepcopy(board))
        self.set_predicted_board(board.copy())


    def set_opponent_pieces_position(self):
        
        for ii in range(0, 16):
            position = self.piece_idx2loc[ii]

            # Check if Alive
            if tuple(position) != (-1, -1):
                piece = chess.Piece(self.idx2pieces[ii][0], self.opponentcolor)
                square = self.point2square(position)

                # Set Piece
                if self.predicted_board.piece_type_at(square) == None:
                    self.predicted_board.set_piece_at(square, piece)



    def update_opponent_move(self, captured_piece, captured_square):
        # # Update Predict Board
        # self.update_piece_location_dict()
        # self.set_pieces_position(self.your_board)

        if captured_piece:
            # Find most likely piece was moved to get there
            position = self.square2point(captured_square)
            best_idx = self.mostly_likely_piece(captured_square)
            
            # Changed Probablility to match Sense
            self.probability_board[best_idx, :, :] = 0.0
            self.probability_board[best_idx, position[0], position[1]] = 1.0

        else:
            self.opponent_prob_step()

        # Update Predict Board
        self.update_piece_location_dict()
        self.set_pieces_position(self.your_board)
        


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
        action_prob = 1.0/num_legal_moves if num_legal_moves else 1.0
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
                # Find most likely piece was moved to get there
                best_idx = self.mostly_likely_piece(captured_square)
                
                # Changed Probablility to match observation
                self.probability_board[best_idx, :, :] = 0.0
        else:
            # TODO Not Sure what to do here
            pass

        # Update Predict Board
        self.update_piece_location_dict()
        self.set_pieces_position(self.your_board)
 

    def sense_update(self, sense_result):
        for result in sense_result:
            position = self.square2point(result[0])
            piece = result[1]

            if piece == None or piece.color == self.mycolor:
                self.probability_board[:, position[0], position[1]] = 0.0
            else:
                # Find most likely piece was moved to get there
                best_prob = 0.0
                best_idx = None
                for idx in self.piece_type2indices[piece.piece_type]:
                    current_posiiton = self.piece_idx2loc[idx]
                    current_posiiton = self.point2square(current_posiiton)
                    prob = self.probability_board[idx, position[0], position[1]] + (1 - chess.square_distance(result[0], current_posiiton)/16.0)

                    if prob >= best_prob:
                        best_prob = prob
                        best_idx = idx
                
                # Changed Probablility to match Sense
                self.probability_board[best_idx, :, :] = 0.0
                self.probability_board[best_idx, position[0], position[1]] = 1.0

        # Update Predict Board
        self.update_piece_location_dict()
        self.set_pieces_position(self.your_board)


    def mostly_likely_piece(self, captured_square):
        position = self.square2point(captured_square)

        # Find most likely piece was moved to get there
        best_prob = 0.0
        best_idx = None
        for idx in range(0, 16):
            current_posiiton = self.piece_idx2loc[idx]
            current_posiiton = self.point2square(current_posiiton)
            prob = self.probability_board[idx, position[0], position[1]] + (1 - chess.square_distance(captured_square, current_posiiton)/16.0)

            if prob >= best_prob:
                best_prob = prob
                best_idx = idx

        return best_idx


def main():
    # TEST
    predictor = Predictor(chess.WHITE)

    predictor.opponent_prob_step()
    print(predictor.probability_board[2])
    board = chess.Board()
    board.clear_board()
    print(predictor.predict_board(board))
    print(predictor.probability_board[2])


    sense_results = [(chess.A8, chess.Piece(chess.ROOK, chess.BLACK)), (chess.B8, chess.Piece(chess.KNIGHT, chess.BLACK)), (chess.C8, chess.Piece(chess.BISHOP, chess.BLACK)),
                    (chess.A7, chess.Piece(chess.PAWN, chess.BLACK)), (chess.B7, None), (chess.C7, chess.Piece(chess.PAWN, chess.BLACK)),
                    (chess.A6, None), (chess.B6, chess.Piece(chess.PAWN, chess.BLACK)), (chess.C6, None)
                    ]
    predictor.sense_update(sense_results)
    board.clear_board()
    print(predictor.predict_board(board))
    print(predictor.probability_board[2])



if __name__ == "__main__":
    main()
