class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = False
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks, self.current_castling_right.wqs, self.current_castling_right.bqs)]




    def makeMove(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # update king location
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # en passant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'

        #update enpassant possible
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.enpassant_possible = ()

        # castle
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: # kingside
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1] #move rook
                self.board[move.end_row][move.end_col + 1] = '--'
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]  # move rook
                self.board[move.end_row][move.end_col - 2] = '--'

        # update castle rights
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_right.wks,self.current_castling_right.bks,self.current_castling_right.wqs,self.current_castling_right.bqs))

    def undoMove(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # move king back if undo move
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            #undo enpassant
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)

            #undo 2 square pawn move
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()

            #undo castling rights
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castling_right = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)

            #undo castling move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2: #kingside
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else: #queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            self.checkmate = False
            self.stalemate = False


    def updateCastleRights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_right.wqs = False
                elif move.start_col == 7:
                    self.current_castling_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_right.bqs = False
                elif move.start_col == 7:
                    self.current_castling_right.bks = False

    # all moves considering checks
    def getValidMoves(self):
        temp_enpassant_possible = self.enpassant_possible
        temp_castling_rights = CastleRights(self.current_castling_right.wks,self.current_castling_right.bks,
                                            self.current_castling_right.wqs,self.current_castling_right.bqs)
        # generate all possible moves
        moves = self.getAllPossibleMoves()

        # make each move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # generate all opponents moves and see if they attack king
            self.white_to_move = not self.white_to_move
            if self.inCheck():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True

        if self.white_to_move:
            self.getCastleMoves(self.white_king_location[0],self.white_king_location[1], moves)
        else:
            self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)
        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_right = temp_castling_rights
        return moves


    def inCheck(self):
        if self.white_to_move:
            return self.squareUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])

        # determine if the enemy can attack the square r, c

    def squareUnderAttack(self, r, c):
        self.white_to_move = not self.white_to_move
        opp_moves = self.getAllPossibleMoves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

        # all moves not considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board)):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves


    def getPawnMoves(self, r, c, moves):
        # white pawns and black pawns move differently
        if self.white_to_move:
            if self.board[r - 1][c] == "--":  # move 1 square ahead
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # move 2 squares ahead
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':  # diagonal right capture
                    moves.append(Move((r, c,), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_enpassant_move = True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':  # diagonal left capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_enpassant_move = True))

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            #captures
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':  # diagonal right capture
                    moves.append(Move((r, c,), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_enpassant_move = True))

            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':  # diagonal left capture
                    moves.append(Move((r, c,), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_enpassant_move = True))
            #pawn promotions later

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # checks if square is on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty space, valid move
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece, capture move
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece, invalid move
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, 2), (-1, -2), (1, 2), (1, -2))
        ally_color = "w" if self.white_to_move else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # checks if square is on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # empty space, valid move
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty space, valid move
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece, capture move
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece, invalid move
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # empty space, valid move
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move():
    # Some useful dictionaries
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = startSq[0]
        self.start_col = startSq[1]
        self.end_row = endSq[0]
        self.end_col = endSq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or \
                               (self.piece_moved == 'bp' and self.end_row == 7)
        #en passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        #castle
        self.is_castle_move = is_castle_move


        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        #print(self.move_ID)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.start_row, self.start_col) + self.getRankFile(self.end_row, self.end_col)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
