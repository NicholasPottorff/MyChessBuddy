import random
from Chess import ChessBuddyEngine, ChessBuddyMain

pieceScore = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

#Aggressive Bias can be set to -1 for defensive, 0 for neutral, and 1 for aggressive
AGGRESSIVE_BIAS = 0


def findRandomMove(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def findBestMove(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1
    opponent_minmax_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)

    for player_move in valid_moves:
        gs.makeMove(player_move)
        opponents_moves = gs.getValidMoves()
        if gs.stalemate:
            opponent_max_score = STALEMATE
        elif gs.checkmate:
            opponent_max_score = CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponents_move in opponents_moves:
                gs.makeMove(opponents_move)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * scoreMaterial(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undoMove()
        if opponent_max_score < opponent_minmax_score:
            opponent_minmax_score = opponent_max_score
            best_player_move = player_move
        gs.undoMove()
    return best_player_move


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score


def findBestMoveMinMax(gs, valid_moves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, valid_moves, DEPTH, gs.white_to_move)
    return nextMove


def findMoveMinMax(gs, valid_moves, depth, white_to_move):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    random.shuffle(valid_moves)

    if AGGRESSIVE_BIAS == -1: #defensive AI will not capture a piece unless it has no other choice
        #print("attempting to be defensive")
        for i in range(len(valid_moves) - 1, -1, -1):
            if valid_moves[i].piece_captured != '--' and 1 < len(valid_moves):
                valid_moves.remove(valid_moves[i])
                #print("removed an aggressive move")
    elif AGGRESSIVE_BIAS == 1:
        #print("attempting to be aggressive")
        for i in range(len(valid_moves) - 1, -1, -1):
            if valid_moves[i].piece_captured == '--' and 1 < len(valid_moves):
                valid_moves.remove(valid_moves[i])
                #print("removed a non-aggressive move")

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.makeMove(move)
            next_moves = gs.getValidMoves()
            score = findMoveMinMax(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.makeMove(move)
            next_moves = gs.getValidMoves()
            score = findMoveMinMax(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return min_score


def scoreBoard(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE  # black win
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    if AGGRESSIVE_BIAS == 0:
        for row in gs.board:
            for square in row:
                if square[0] == 'w':
                    score += pieceScore[square[1]]
                elif square[0] == 'b':
                    score -= pieceScore[square[1]]
    if AGGRESSIVE_BIAS == -1: #only wants to protect own pieces
        for row in gs.board:
            for square in row:
                if gs.white_to_move:
                    if square[0] == 'w':
                        score += pieceScore[square[1]]
                else:
                    if square[0] == 'b':
                        score -= pieceScore[square[1]]
    if AGGRESSIVE_BIAS == 1: #wants to decrease the amount of opponent pieces at any cost
        for row in gs.board:
            for square in row:
                if gs.white_to_move:
                    if square[0] == 'b':
                        score -= pieceScore[square[1]]
                else:
                    if square[0] == 'w':
                        score += pieceScore[square[1]]

    return score

