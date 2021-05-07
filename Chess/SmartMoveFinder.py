import random
from Chess import ChessBuddyEngine, ChessBuddyMain

pieceScore = {"K": 0, "Q": 9, "R": 5, "N": 3, "B": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

# STYLE BIAS is a 4 number tuple, the four numbers represent the likelihood of making different styles of moves
# The four numbers can total 100 to better represent percentages
# The four numbers represent the likelihood of (Best move, worst move, aggressive move, defensive)
STYLE_BIAS = [65, 15, 15, 5]
CURRENT_STYLE = 0

# Moods determine how hard the AI thinks in certain situations

# "Bad Sport" represents the tendency of some players to give up or stop trying when they are losing
# When the AI is losing by this many points, it tends toward making worst move
BAD_SPORT = 9

# "Comeback" represents the tendency of some players to try even harder when they are losing.
# when the AI is losing by this many points, but less points than "bad sport", they tend toward make "best" move
COMEBACK = 4

# "overconfident" represents the tendency of some players to not think as hard when they are winning
# when the AI is winning by this many points, it tends towards makes aggressive moves
OVERCONFIDENT = 5

# "Cautious" represents the tendency of some players to hold on to smaller leads
# when the AI is winning by this many points, but less points than "overconfident", it tends to make moves defensively
CAUTIOUS = 2

# amount of points that STYLE_BIAS values get changed by when the computer gets in certain "moods"
MOOD_BIAS = 10



def findRandomMove(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score


def chooseStyle():
    style_sum = sum(STYLE_BIAS)
    style_choice = random.randint(0, style_sum)

    #change style to best move
    if style_choice < STYLE_BIAS[0]:
        CURRENT_STYLE = 0
        print("choosing a good move")
    elif style_choice < (STYLE_BIAS[0] + STYLE_BIAS[1]):
        CURRENT_STYLE = 1
        print("choosing a bad move")
    elif style_choice < (STYLE_BIAS[0] + STYLE_BIAS[1] + STYLE_BIAS[2]):
        CURRENT_STYLE = 2
        print("choosing an aggressive move")
    else:
        CURRENT_STYLE = 3
        print("choosing a defensive move")

def chooseMood(gs):
    score = scoreMaterial(gs.board)
    if not gs.white_to_move:
        score = score * -1
    if score >= OVERCONFIDENT:
        print("feeling overconfident")
        STYLE_BIAS[2] += MOOD_BIAS
    elif score >= CAUTIOUS:
        print("feeling cautious")
        STYLE_BIAS[3] += MOOD_BIAS
    elif BAD_SPORT < score <= COMEBACK * -1:
        print("feeling a comeback")
        STYLE_BIAS[0] += MOOD_BIAS
    elif score <= BAD_SPORT * -1:
        print("I'm a bad sport")
        STYLE_BIAS[1] += MOOD_BIAS
    else:
        print("feeling neutral")
        return



def findBestMoveMinMax(gs, valid_moves):
    chooseMood(gs)
    chooseStyle()
    global nextMove
    nextMove = None
    findMoveMinMax(gs, valid_moves, DEPTH, gs.white_to_move)
    return nextMove


# recursive function
def findMoveMinMax(gs, valid_moves, depth, white_to_move):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    random.shuffle(valid_moves)

    if CURRENT_STYLE == 3:  # defensive AI will not capture a piece unless it has no other choice
        # print("attempting to be defensive")
        for i in range(len(valid_moves) - 1, -1, -1):
            if valid_moves[i].piece_captured != '--' and 1 < len(valid_moves):
                valid_moves.remove(valid_moves[i])
                # print("removed an aggressive move")
    elif CURRENT_STYLE  == 2:
        # print("attempting to be aggressive")
        for i in range(len(valid_moves) - 1, -1, -1):
            if valid_moves[i].piece_captured == '--' and 1 < len(valid_moves):
                valid_moves.remove(valid_moves[i])
                # print("removed a non-aggressive move")

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

    if CURRENT_STYLE == 0: #scores to find "best" move
        for row in gs.board:
            for square in row:
                if square[0] == 'w':
                    score += pieceScore[square[1]]
                elif square[0] == 'b':
                    score -= pieceScore[square[1]]
    elif CURRENT_STYLE == 1: #scores to find worst move
        for row in gs.board:
            for square in row:
                if square[0] == 'b':
                    score += pieceScore[square[1]]
                elif square[0] == 'w':
                    score -= pieceScore[square[1]]
    elif CURRENT_STYLE == 3:  # only wants to protect own pieces
        for row in gs.board:
            for square in row:
                if gs.white_to_move:
                    if square[0] == 'w':
                        score += pieceScore[square[1]]
                else:
                    if square[0] == 'b':
                        score -= pieceScore[square[1]]
    elif CURRENT_STYLE == 2:  # wants to decrease the amount of opponent pieces at any cost
        for row in gs.board:
            for square in row:
                if gs.white_to_move:
                    if square[0] == 'b':
                        score -= pieceScore[square[1]]
                else:
                    if square[0] == 'w':
                        score += pieceScore[square[1]]

    return score
