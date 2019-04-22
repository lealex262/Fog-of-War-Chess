import chess
import random


class Scouter:
    def __init__(self, color):
        self.scout_history = [0 for _ in range(64)]
        self.next_scout = None
        self.color = color

    def handle_opponent_move(self, captured_piece, captured_square):
        if captured_piece:
            self.next_scout = captured_square
        else:
            bv = 0
            bs = None
            # TODO: Choose randomly between equally past histories
            for fil in range(1, 8):
                for rank in range(1, 8):
                    sq = chess.square(fil, rank)
                    value = self._get_history_sum(sq)
                    if value > bv:
                        bv = value
                        bs = sq

            self.next_scout = bs

        
    def update_scout_history(self, move):
        # TODO: Scout history should be 0 where our pieces are
        self.scout_history = [x + 1 for x in self.scout_history]
        fil, rank = chess.square_file(move), chess.square_rank(move)
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                x = fil + i
                y = rank + j
                if 0 <= x < 8 and 0 <= y < 8:
                    self.scout_history[chess.square(x, y)] = 0

    def choose_sense(self, possible_sense, possible_moves, turn):
        if turn == 0:
            if self.color:
                self.next_scout = chess.Square(45)
            else:
                self.next_scout = chess.Square(21)
        print(turn)
        print(self.next_scout)
        self.update_scout_history(self.next_scout)
        return self.next_scout


    def _get_history_sum(self, square):
        value = 0
        fil, rank = chess.square_file(square), chess.square_rank(square)
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                x = fil + i
                y = rank + j
                if 0 <= x < 8 and 0 <= y < 8:
                    value += self.scout_history[chess.square(x, y)]
        return value
