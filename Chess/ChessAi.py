import random

piece_points = {'K': 20000, 'Q': 900, 'R': 500, 'N': 330, 'B': 330, 'p': 100}
CHECKMATE = 100000
STALEMATE = 0



def get_random_move(valid_moves):
    return random.choice(valid_moves)



def get_minmax_move(gs, valid_moves):
    global next_move
    next_move = None
    minmax(gs, valid_moves, DEPTH, gs.white_to_move)
    return next_move


def get_negamax_move(gs, valid_moves, queue, DEPTH):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    negamax(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1, DEPTH)
    queue.put(next_move)


def minmax(gs, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return evaluate_board(gs.board)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = minmax(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = minmax(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score


def negamax(gs, valid_moves, depth, alpha, beta, color, DEPTH):
    global next_move
    if depth == 0:
        return color * evaluation_function(gs)

    ordered_moves = sorted(valid_moves, key=lambda m:gs.move_value(m), reverse=True)

    max_score = -CHECKMATE
    for move in ordered_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -negamax(gs, next_moves, depth - 1, -beta, -alpha, -color, DEPTH)

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()

        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    return max_score


def evaluate_board(board):
    points = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                points += piece_points[square[1]]
            elif square[0] == 'b':
                points -= piece_points[square[1]]
    return points


def evaluation_function(gs):
    piece_tables = {
        'p': [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 5, 5, 5, 5, 5, 5, 5],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [0, 0, 0, 2, 2, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [1, -1, -1, 0, 0, -1, -1, 1],
            [1, 2, 2, -2, -2, 2, 2, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],

        'R': [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0.5, 1, 1, 1, 1, 1, 1, 0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [0.5, 1, 1, 1, 1, 1, 1, 0.5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],

        'N': [
            [-5, -4, -3, -3, -3, -3, -4, -5],
            [-4, -2, 0, 0, 0, 0, -2, -4],
            [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
            [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
            [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
            [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
            [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
            [-5, -4, -3, -3, -3, -3, -4, -5]
        ],

        'B': [
            [-2, -1, -1, -1, -1, -1, -1, -2],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
            [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
            [-1, 0, 1, 1, 1, 1, 0, -1],
            [-1, 1, 1, 1, 1, 1, 1, -1],
            [-1, 0.5, 0, 0, 0, 0, 0.5, -1],
            [-2, -1, -1, -1, -1, -1, -1, -2]
        ],

        'Q': [
            [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
            [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
            [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
            [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
            [-1, 0, 0.5, 0, 0, 0, 0, -1],
            [-2, -1, -1, -0.5, -0.5, -1, -1, -2]
        ],

        'K': [
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-2, -3, -3, -4, -4, -3, -3, -2],
            [-1, -2, -2, -2, -2, -2, -2, -1],
            [2, 2, 0, 0, 0, 0, 2, 2],
            [2, 3, 1, 0, 0, 1, 3, 2]
        ],

    }

    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    else:
        points = 0
        for row in range(8):
            for col in range(8):
                square = gs.board[row][col]
                if square[0] == 'w':
                    points += piece_points[square[1]]
                elif square[0] == 'b':
                    points -= piece_points[square[1]]
                if square[1] == '-':
                    positional_pts = 0
                else:
                    if square[0] == 'w':
                        table = piece_tables[square[1]]
                        positional_pts = table[row][col] * 10
                    else:
                        table = piece_tables[square[1]]
                        positional_pts = table[7 - row][col] * 10
                if square[0] == 'w':
                    points += positional_pts
                elif square[0] == 'b':
                    points -= positional_pts
        return points
