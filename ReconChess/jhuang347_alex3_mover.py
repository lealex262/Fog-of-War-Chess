import chess
import time

def material_difference(board):
    wK, wQ, wR, wB, wN, wP = 200, 9, 5, 3, 3, 1
    nWK = len(board.pieces(chess.KING, True))
    nWQ = len(board.pieces(chess.QUEEN, True))
    nWR = len(board.pieces(chess.ROOK, True))
    nWB = len(board.pieces(chess.BISHOP, True))
    nWN = len(board.pieces(chess.KNIGHT, True))
    nWP = len(board.pieces(chess.PAWN, True))

    nBK = len(board.pieces(chess.KING, False))
    nBQ = len(board.pieces(chess.QUEEN, False))
    nBR = len(board.pieces(chess.ROOK, False))
    nBB = len(board.pieces(chess.BISHOP, False))
    nBN = len(board.pieces(chess.KNIGHT, False))
    nBP = len(board.pieces(chess.PAWN, False))
    
    md = wK * (nWK - nBK) + wQ * (nWQ - nBQ) + wR * (nWR - nBR) + wB * (nWB - nBB) + wN * (nWN - nBN) + wP * (nWP - nBP)
    return md

def piece_values(board, color):
    if not color:
        board = board.mirror()
    
    value = 0
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
    for piece_type in piece_types:
        for space in board.pieces(piece_type, True):
            value += piece_table(piece_type, space)
        
    return value

def position_difference(board):
    return piece_values(board, True) - piece_values(board, False)

def show_evaluate(board):
    md = material_difference(board)
    pd = position_difference(board)
    return md, pd, md + pd / 100.

def evaluate(board):
    md = material_difference(board)
    pd = position_difference(board)
    return md + pd / 100.


def piece_table(piece_type, position):
    pawns = [0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10,-20,-20, 10, 10,  5,
            5, -5,-10,  0,  0,-10, -5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5,  5, 10, 25, 25, 10,  5,  5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 50, 50, 50, 50, 50, 50,
            0,  0,  0,  0,  0,  0,  0,  0]
        
    knights = [-50,-40,-30,-30,-30,-30,-40,-50,
               -40,-20,  0,  5,  5,  0,-20,-40,
               -30,  5, 10, 15, 15, 10,  5,-30,
               -30,  0, 15, 20, 20, 15,  0,-30,
               -30,  5, 15, 20, 20, 15,  5,-30,
               -30,  0, 10, 15, 15, 10,  0,-30,
               -40,-20,  0,  0,  0,  0,-20,-40,
               -50,-40,-30,-30,-30,-30,-40,-50,]
    
    bishops = [-20,-10,-10,-10,-10,-10,-10,-20,
               -10,  5,  0,  0,  0,  0,  5,-10,
               -10, 10, 10, 10, 10, 10, 10,-10,
               -10,  0, 10, 10, 10, 10,  0,-10,
               -10,  5,  5, 10, 10,  5,  5,-10,
               -10,  0,  5, 10, 10,  5,  0,-10,
               -10,  0,  0,  0,  0,  0,  0,-10,
               -20,-10,-10,-10,-10,-10,-10,-20,]
    
    rooks = [ 0,  0,  0,  5,  5,  0,  0,  0,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
              5, 10, 10, 10, 10, 10, 10,  5,
              0,  0,  0,  0,  0,  0,  0,  0,]
    
    queens = [-20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -10,  5,  5,  5,  5,  5,  0,-10,
              0,  0,  5,  5,  5,  5,  0, -5,
             -5,  0,  5,  5,  5,  5,  0, -5,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20,]
    
    kings = [20, 30, 10,  0,  0, 10, 30, 20,
             20, 20,  0,  0,  0,  0, 20, 20,
            -10,-20,-20,-20,-20,-20,-20,-10,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,]
    
    mapping = dict()
    mapping[chess.PAWN] = pawns
    mapping[chess.KNIGHT] = knights
    mapping[chess.BISHOP] = bishops
    mapping[chess.ROOK] = rooks
    mapping[chess.QUEEN] = queens
    mapping[chess.KING] = kings
    
    return mapping[piece_type][position];

def minimax(node, depth, isMaximizingPlayer, alpha, beta, max_depth, time_remaining):
    now = time.time()
    if time_remaining < 0.1:
        return None, None
    if depth == max_depth:
        return evaluate(node), node.copy()

    if isMaximizingPlayer:
        bestVal = -999999999
        bestBoard = None
        for move in node.generate_pseudo_legal_moves():
            node.push(move)
            value, board = minimax(node, depth+1, False, alpha, beta, max_depth, time_remaining - (time.time() - now))
            if value is None:
                return None, None
            node.pop()
            if value > bestVal:
                bestVal = value
                bestBoard = board
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestBoard

    else:
        bestVal = 999999999
        bestBoard = None
        for move in node.generate_pseudo_legal_moves():
            node.push(move)
            value, board = minimax(node, depth+1, True, alpha, beta, max_depth, time_remaining - (time.time() - now))
            if value is None:
                return None, None
            node.pop()
            if value < bestVal:
                bestVal = value
                bestBoard = board
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestBoard
    
def find_best_move(board, time_remaining, color):
    now = time.time()
    value, b = minimax(board.copy(stack=False), 0, color, -float('inf'), float('inf'), 1, time_remaining)
    depth = 2
    td = time.time() - now
    while td < time_remaining:
        candidate, cb = minimax(board.copy(stack=False), 0, color, -float('inf'), float('inf'), depth, time_remaining - td)
        td = time.time() - now
        if cb is None:
            break
        else:
            value = candidate
            b = cb
            depth += 1
            
    if b is None:
        return None
    return b.move_stack[0]
