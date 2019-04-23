#!/usr/bin/env python3

"""
File Name:      my_agent.py
Authors:        Alex Le Jesse Huang
Date:           April 18, 2019

Description:    Python file for my agent.
Source:         Adapted from recon-chess (https://pypi.org/project/reconchess/)
"""

import chess
from player import Player
from jhuang347_alex3_mover import find_best_move
from jhuang347_alex3_scouter import Scouter
from jhuang347_alex3_predictor import Predictor


class MDP_Only(Player):

    def __init__(self):
        self.turn = -1
        self.board = chess.Board()
        self.players_board = None
        
    def handle_game_start(self, color, board):
        """
        This function is called at the start of the game.

        :param color: chess.BLACK or chess.WHITE -- your color assignment for the game
        :param board: chess.Board -- initial board state
        :return:
        """
        # print("Game Start")
        self.color = color
        self.scouter = Scouter(color)
        self.predictor = Predictor(color)
        white_fen = "8/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        black_fen = "rnbqkbnr/pppppppp/8/8/8/8/8/8 w KQkq - 0 1"
        if color == chess.WHITE:
            self.players_board = chess.Board(white_fen)
        else:
            self.players_board = chess.Board(black_fen)
        
    def handle_opponent_move_result(self, captured_piece, captured_square):
        """
        This function is called at the start of your turn and gives you the chance to update your board.

        :param captured_piece: bool - true if your opponents captured your piece with their last move
        :param captured_square: chess.Square - position where your piece was captured
        """
        self.scouter.handle_opponent_move(captured_piece, captured_square)
        self.predictor.update_opponent_move(captured_piece, captured_square)
        self.turn += 1

    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        """
        This function is called to choose a square to perform a sense on.

        :param possible_sense: List(chess.SQUARES) -- list of squares to sense around
        :param possible_moves: List(chess.Moves) -- list of acceptable moves based on current board
        :param seconds_left: float -- seconds left in the game

        :return: chess.SQUARE -- the center of 3x3 section of the board you want to sense
        :example: choice = chess.A1
        """
        # print("choose_sense")
        choice = self.scouter.choose_sense(possible_sense, possible_moves, self.turn, self.players_board)
        return choice
        
    def handle_sense_result(self, sense_result):
        """
        This is a function called after your picked your 3x3 square to sense and gives you the chance to update your
        board.

        :param sense_result: A list of tuples, where each tuple contains a :class:`Square` in the sense, and if there
                             was a piece on the square, then the corresponding :class:`chess.Piece`, otherwise `None`.
        :example:
        [handle_sense_result
            (A8, Piece(ROOK, BLACK)), (B8, Piece(KNIGHT, BLACK)), (C8, Piece(BISHOP, BLACK)),
            (A7, Piece(PAWN, BLACK)), (B7, Piece(PAWN, BLACK)), (C7, Piece(PAWN, BLACK)),
            (A6, None), (B6, None), (C6, None)
        ]
        """
        # print("handle_sense_result")
        self.predictor.sense_update(sense_result)
        pass

    def choose_move(self, possible_moves, seconds_left):
        """
        Choose a move to enact from a list of possible moves.

        :param possible_moves: List(chess.Moves) -- list of acceptable moves based only on pieces
        :param seconds_left: float -- seconds left to make a move
        
        :return: chess.Move -- object that includes the square you're moving from to the square you're moving to
        :example: choice = chess.Move(chess.F2, chess.F4)
        
        :condition: If you intend to move a pawn for promotion other than Queen, please specify the promotion parameter
        :example: choice = chess.Move(chess.G7, chess.G8, promotion=chess.KNIGHT) *default is Queen
        """
        # print("choose_move")
        predicted_board = self.predictor.predict_board(self.players_board)
        print("Prediction")
        print(predicted_board)
        predicted_board.turn = self.color
        choice = find_best_move(predicted_board, min(5, seconds_left), self.color)
        return choice
        
    def handle_move_result(self, requested_move, taken_move, reason, captured_piece, captured_square):
        """
        This is a function called at the end of your turn/after your move was made and gives you the chance to update
        your board.

        :param requested_move: chess.Move -- the move you intended to make
        :param taken_move: chess.Move -- the move that was actually made
        :param reason: String -- description of the result from trying to make requested_move
        :param captured_piece: bool - true if you captured your opponents piece
        :param captured_square: chess.Square - position where you captured the piece
        """
        # print("handle_move_result")
        success = (requested_move == taken_move)
        self.players_board.turn = self.color
        if taken_move is not None:
            self.players_board.push(taken_move)
        self.predictor.update_your_move(self.players_board, success, taken_move, captured_piece, captured_square)
        
    def handle_game_end(self, winner_color, win_reason):  # possible GameHistory object...
        """
        This function is called at the end of the game to declare a winner.

        :param winner_color: Chess.BLACK/chess.WHITE -- the winning color
        :param win_reason: String -- the reason for the game ending
        """
        pass
