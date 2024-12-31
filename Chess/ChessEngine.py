import numpy as np


piece_points = {'K': 20000, 'Q': 900, 'R': 500, 'N': 330, 'B': 330, 'p': 100}
# creates GameState object
class GameState:
    def __init__(self):
        # initial board
        self.board = np.array([
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ])
        # current turn
        self.white_to_move = True
        # list of all moves played
        self.move_log = []
        self.move_funcs = {'p': self.pawn_moves, 'R': self.rook_moves, 'N': self.knight_moves,
                           'B': self.bishop_moves, 'Q': self.queen_moves, 'K': self.king_moves}
        # king locations
        self.white_king = (7, 4)
        self.black_king = (0, 4)
        # checkmate, stalemate, and resign
        self.checkmate = False
        self.stalemate = False
        self.resign = False
        # square where enpassant is possible
        self.enpassant_possible = ()
        self.enpassant_possible_log = [self.enpassant_possible]
        # current castling rights and log of castle rights
        self.current_castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks,
                                               self.current_castle_rights.wqs, self.current_castle_rights.bqs)]

    # make a move
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # update kings location if piece moved is king
        if move.piece_moved == 'wK':
            self.white_king = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king = (move.end_row, move.end_col)
        # check for pawn promotion add options later
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'
        # check for enpassant
        if move.is_enpassant:
            self.board[move.start_row][move.end_col] = '--'
        # update square where enpassant is possible
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()
        # check for castle
        if move.is_castle:
            # king side
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            # queen side
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'
        self.enpassant_possible_log.append(self.enpassant_possible)
        # update castling rights and castle log
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks,
                                                   self.current_castle_rights.wqs, self.current_castle_rights.bqs))

    # undo a move
    def undo_move(self):
        if len(self.move_log) != 0:
            # get last move from move log
            last_move = self.move_log.pop()
            # reverse last move and turn
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
            self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
            self.white_to_move = not self.white_to_move
            # update kings location if last piece moved is king
            if last_move.piece_moved == 'wK':
                self.white_king = (last_move.start_row, last_move.start_col)
            elif last_move.piece_moved == 'bK':
                self.black_king = (last_move.start_row, last_move.start_col)
            # reverse enpassant
            if last_move.is_enpassant:
                self.board[last_move.end_row][last_move.end_col] = '--'
                self.board[last_move.start_row][last_move.end_col] = last_move.piece_captured
            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]
            # update castle rights
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castle_rights = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
            # reverse castle
            if last_move.is_castle:
                # king side
                if last_move.end_col - last_move.start_col == 2:
                    self.board[last_move.end_row][last_move.end_col + 1] = self.board[last_move.end_row][
                        last_move.end_col - 1]
                    self.board[last_move.end_row][last_move.end_col - 1] = '--'
                # queen side
                else:
                    self.board[last_move.end_row][last_move.end_col - 2] = self.board[last_move.end_row][
                        last_move.end_col + 1]
                    self.board[last_move.end_row][last_move.end_col + 1] = '--'
            self.checkmate = False
            self.stalemate = False
            self.resign = False

    # after every move check if player still has the ability to castle
    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castle_rights.wks = False
            self.current_castle_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castle_rights.bks = False
            self.current_castle_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castle_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castle_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castle_rights.bks = False
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castle_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castle_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castle_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castle_rights.bks = False

    # gets all valid moves considering checks and pins
    def get_valid_moves(self) -> list:
        # create temp variables to store current attributes so no changes are made
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks,
                                          self.current_castle_rights.wqs, self.current_castle_rights.bqs)
        # get all possible moves
        moves = self.all_possible_moves()
        # get castling moves
        if self.white_to_move:
            self.get_castle_moves(self.white_king[0], self.white_king[1], moves)
        else:
            self.get_castle_moves(self.black_king[0], self.black_king[1], moves)
        # simulate all current player moves and check for checks
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
        # checkmate and stalemate conditions
        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        # reset current attributes after simulation
        self.enpassant_possible = temp_enpassant_possible
        self.current_castle_rights = temp_castle_rights
        # returns list of all valid moves for current player
        return moves

    # check for checks helps get_valid_moves
    def in_check(self) -> bool:
        if self.white_to_move:
            return self.square_under_attack(self.white_king[0], self.white_king[1])
        else:
            return self.square_under_attack(self.black_king[0], self.black_king[1])

    # check for a square under attack helps in_check and get_valid_moves
    def square_under_attack(self, row, col) -> bool:
        # simulate all opponent moves
        self.white_to_move = not self.white_to_move
        opp_moves = self.all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    # gets all possible moves for current player without considering checks and pins
    def all_possible_moves(self) -> list:
        moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                turn, piece = self.board[i][j][0], self.board[i][j][1]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    self.move_funcs[piece](i, j, moves)
        # returns a list of all possible moves
        return moves

    # gets all possible pawn moves helps all_possible_moves
    def pawn_moves(self, row, col, moves):
        # white
        if self.white_to_move:
            # forward
            if row - 1 >= 0:
                if row == 6:
                    if self.board[row - 1][col] == '--':
                        moves.append(Move((row, col), (row - 1, col), self.board))
                        if self.board[row - 2][col] == '--':
                            moves.append(Move((row, col), (row - 2, col), self.board))
                else:
                    if self.board[row - 1][col] == '--':
                        moves.append(Move((row, col), (row - 1, col), self.board))
                # capture left
                if col - 1 >= 0:
                    if self.board[row - 1][col - 1][0] == 'b':
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
                    # enpassant
                    elif (row - 1, col - 1) == self.enpassant_possible:
                        moves.append(Move((row, col), (row - 1, col - 1), self.board, True))
                # capture right
                if col + 1 <= 7:
                    if self.board[row - 1][col + 1][0] == 'b':
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
                    # enpassant
                    elif (row - 1, col + 1) == self.enpassant_possible:
                        moves.append(Move((row, col), (row - 1, col + 1), self.board, True))
        # black
        else:
            # forward
            if row + 1 <= 7:
                if row == 1:
                    if self.board[row + 1][col] == '--':
                        moves.append(Move((row, col), (row + 1, col), self.board))
                        if self.board[row + 2][col] == '--':
                            moves.append(Move((row, col), (row + 2, col), self.board))
                else:
                    if self.board[row + 1][col] == '--':
                        moves.append(Move((row, col), (row + 1, col), self.board))
                # capture right
                if col - 1 >= 0:
                    if self.board[row + 1][col - 1][0] == 'w':
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                    # enpassant
                    elif (row + 1, col - 1) == self.enpassant_possible:
                        moves.append(Move((row, col), (row + 1, col - 1), self.board, True))
                # capture left
                if col + 1 <= 7:
                    if self.board[row + 1][col + 1][0] == 'w':
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))
                    # enpassant
                    elif (row + 1, col + 1) == self.enpassant_possible:
                        moves.append(Move((row, col), (row + 1, col + 1), self.board, True))

    # gets all possible rook moves helps all_possible_moves
    def rook_moves(self, row, col, moves):
        # (-1,0) direction
        for i in range(col - 1, -1, -1):
            if self.board[row][i] == '--':
                moves.append(Move((row, col), (row, i), self.board))
            else:
                if self.board[row][col][0] == 'w' and self.board[row][i][0] == 'b':
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                elif self.board[row][col][0] == 'b' and self.board[row][i][0] == 'w':
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                else:
                    break
        # (1,0) direction
        for i in range(col + 1, 8, 1):
            if self.board[row][i] == '--':
                moves.append(Move((row, col), (row, i), self.board))
            else:
                if self.board[row][col][0] == 'w' and self.board[row][i][0] == 'b':
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                if self.board[row][col][0] == 'b' and self.board[row][i][0] == 'w':
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                else:
                    break
        # (0,1) direction
        for i in range(row - 1, -1, -1):
            if self.board[i][col] == '--':
                moves.append(Move((row, col), (i, col), self.board))
            else:
                if self.board[row][col][0] == 'w' and self.board[i][col][0] == 'b':
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                if self.board[row][col][0] == 'b' and self.board[i][col][0] == 'w':
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                else:
                    break
        # (0,-1) direction
        for i in range(row + 1, 8, 1):
            if self.board[i][col] == '--':
                moves.append(Move((row, col), (i, col), self.board))
            else:
                if self.board[row][col][0] == 'w' and self.board[i][col][0] == 'b':
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                if self.board[row][col][0] == 'b' and self.board[i][col][0] == 'w':
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                else:
                    break

    # gets all possible knight moves helps all_possible_moves
    def knight_moves(self, row, col, moves):
        # check all 8 squares
        possible_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        friend = 'w' if self.white_to_move else 'b'
        for move in possible_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.board[end_row][end_col][0] != friend:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    # gets all possible bishop moves helps all_possible_moves
    def bishop_moves(self, row, col, moves):
        # (1,1) direction
        i, j = row - 1, col + 1
        while i >= 0 and j <= 7:
            if self.board[i][j] == '--':
                moves.append(Move((row, col), (i, j), self.board))
                i -= 1
                j += 1
            else:
                if self.board[row][col][0] == 'w' and self.board[i][j][0] == 'b':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                elif self.board[row][col][0] == 'b' and self.board[i][j][0] == 'w':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                else:
                    break
        # (-1,-1) direction
        i, j = row + 1, col - 1
        while j >= 0 and i <= 7:
            if self.board[i][j] == '--':
                moves.append(Move((row, col), (i, j), self.board))
                i += 1
                j -= 1
            else:
                if self.board[row][col][0] == 'w' and self.board[i][j][0] == 'b':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                elif self.board[row][col][0] == 'b' and self.board[i][j][0] == 'w':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                else:
                    break
        # (1,-1) direction
        i, j = row + 1, col + 1
        while i <= 7 and j <= 7:
            if self.board[i][j] == '--':
                moves.append(Move((row, col), (i, j), self.board))
                i += 1
                j += 1
            else:
                if self.board[row][col][0] == 'w' and self.board[i][j][0] == 'b':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                elif self.board[row][col][0] == 'b' and self.board[i][j][0] == 'w':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                else:
                    break
        # (-1,1) direction
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if self.board[i][j] == '--':
                moves.append(Move((row, col), (i, j), self.board))
                i -= 1
                j -= 1
            else:
                if self.board[row][col][0] == 'w' and self.board[i][j][0] == 'b':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                elif self.board[row][col][0] == 'b' and self.board[i][j][0] == 'w':
                    moves.append(Move((row, col), (i, j), self.board))
                    break
                else:
                    break

    # gets all possible queen moves helps all_possible_moves
    def queen_moves(self, row, col, moves):
        # combine rook and bishop moves
        self.rook_moves(row, col, moves)
        self.bishop_moves(row, col, moves)

    # gets all possible king moves helps all_possible_moves
    def king_moves(self, row, col, moves):
        # check all 8 squares
        possible_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        friend = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = row + possible_moves[i][0]
            end_col = col + possible_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.board[end_row][end_col][0] != friend:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    # gets all possible castle moves helps get_valid_moves
    def get_castle_moves(self, row, col, moves):
        # cannot castle if checked
        if self.square_under_attack(row, col):
            return
        # kings side castle
        if (self.white_to_move and self.current_castle_rights.wks == True) or (
                not self.white_to_move and self.current_castle_rights.bks == True):
            self.king_side_castle_moves(row, col, moves)
        # queen side castle
        if (self.white_to_move and self.current_castle_rights.wqs == True) or (
                not self.white_to_move and self.current_castle_rights.bqs == True):
            self.queen_side_castle_moves(row, col, moves)

    # gets all possible king side castle moves helps get_castle_moves
    def king_side_castle_moves(self, row, col, moves):
        # if the squares the king travels are empty and are not under attack
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle=True))

    # gets all possible queen side castle moves helps get_castle_moves
    def queen_side_castle_moves(self, row, col, moves):
        # if the squares the king travels are empty and are not under attack
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle=True))

    def move_value(self, move):
        capture_value = piece_points[move.piece_captured[1]] if move.piece_captured != '--' else 0
        threatened_penalty = -piece_points[move.piece_moved[1]] // 10 if self.square_under_attack(move.end_row, move.end_col) else 0
        return capture_value + threatened_penalty

# stores castling rights
class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


# creates Move object
class Move:
    rank_to_row = {'1': 7, '2': 6, '3': 5, '4': 4,
                   '5': 3, '6': 2, '7': 1, '8': 0}
    row_to_rank = {v: k for k, v in rank_to_row.items()}
    file_to_col = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                   'e': 4, 'f': 5, 'g': 6, 'h': 7}
    col_to_file = {v: k for k, v in file_to_col.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant=False, is_castle=False):
        # stores start position, end position, piece moved, piece captured, and move id
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        # attribute is True if the move is a pawn promotion
        self.is_pawn_promotion = ((self.piece_moved == 'wp' and self.end_row == 0) or (
                self.piece_moved == 'bp' and self.end_row == 7))
        # attribute is True if the move is enpassant
        self.is_enpassant = is_enpassant
        if self.is_enpassant:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'
        # attribute is true is the move is a castle
        self.is_castle = is_castle

    # overrides print method and prints move in chess notation
    def __str__(self) -> str:
        if self.is_castle:
            return 'O-O' if self.end_col == 6 else 'O-O-O'
        else:
            if self.piece_captured == '--':
                if self.piece_moved == 'bp' or self.piece_moved == 'wp':
                    return self.get_rank_file(self.end_row, self.end_col)
                else:
                    return self.piece_moved + ' ' + self.get_rank_file(self.end_row, self.end_col)
            else:
                if self.piece_moved == 'bp' or self.piece_moved == 'wp':
                    return 'X' + self.get_rank_file(self.end_row, self.end_col)
                else:
                    return self.piece_moved + 'X' + self.get_rank_file(self.end_row, self.end_col)

    # gets file and rank of a piece helps __str__
    def get_rank_file(self, row, col) -> str:
        return self.col_to_file[col] + self.row_to_rank[row]

    # overrides == operator to work for the move object
    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
