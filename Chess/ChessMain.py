import pygame as p
from multiprocessing import Process, Queue
from Chess import ChessEngine
from Chess import ChessAi


# global variables
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
COLORS = [p.Color("white"), p.Color("dark gray")]
IMAGES = {}


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.GameState()
    valid_moves = game_state.get_valid_moves()
    move_made = False
    animate = False
    load_images()
    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False
    player_w, player_b, difficulty_w, difficulty_b = show_menu(screen, clock)
    ai_thinking = False
    move_finder_process = None
    move_undone = False

    while running:
        human_turn = (game_state.white_to_move and player_w) or (not game_state.white_to_move and player_b)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2 and human_turn:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        print(move)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    game_state.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_q:
                    game_state.resign = True

        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                print("thinking...")
                return_queue = Queue()
                move_finder_process = Process(target=ChessAi.get_negamax_move,
                                              args=(game_state, valid_moves, return_queue, difficulty_w if not player_w else difficulty_b))
                move_finder_process.start()
            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    game_state.make_move(ChessAi.get_random_move(valid_moves))
                else:
                    game_state.make_move(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False

        draw_gamestate(screen, game_state, valid_moves, sq_selected, game_state.move_log)
        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                draw_text(screen, "Black Wins!")
            else:
                draw_text(screen, "White Wins!")
        elif game_state.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")
        elif game_state.resign:
            game_over = True
            if game_state.white_to_move:
                draw_text(screen, "Black Wins!")
            else:
                draw_text(screen, "White Wins!")

        clock.tick(MAX_FPS)
        p.display.flip()


def mouse_events():
    pass


# highlights square clicked on, all valid moves from that square, and last move made
def highlight_square(screen, game_state, valid_moves, sq_selected, move_log):
    if sq_selected != ():
        row, col = sq_selected
        if game_state.board[row][col][0] == ('w' if game_state.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('yellow'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            s.fill(p.Color('light green'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))
    if len(move_log) == 0:
        return
    else:
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(50)
        s.fill(p.Color('dark blue'))
        last_move = move_log[-1]
        screen.blit(s, (last_move.start_col * SQ_SIZE, last_move.start_row * SQ_SIZE))
        screen.blit(s, (last_move.end_col * SQ_SIZE, last_move.end_row * SQ_SIZE))


# draws current game state
def draw_gamestate(screen, game_state, valid_moves, sq_selected, move_log):
    draw_board(screen)
    highlight_square(screen, game_state, valid_moves, sq_selected, move_log)
    draw_pieces(screen, game_state.board)


# draws squares helps draw_gamestate
def draw_board(screen):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = COLORS[((i + j) % 2)]
            p.draw.rect(screen, color, p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# draws pieces on squares helps draw_gamestate
def draw_pieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# animates the move
def animate_move(move, screen, board, clock):
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_sq = 2
    frame_count = (abs(dR) + abs(dC)) * frames_per_sq
    for frame in range(frame_count + 1):
        r, c = (move.start_row + dR * frame / frame_count, move.start_col + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = COLORS[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


# draw win and stalemate statements
def draw_text(screen, text):
    font = p.font.SysFont("Bookman Old Style", 32, True, False)
    text_obj = font.render(text, 0, p.Color("black"))
    text_loc = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_obj.get_width() / 2,
                                                HEIGHT / 2 - text_obj.get_height() / 2)
    screen.blit(text_obj, text_loc)


def show_menu(screen, clock):
    font = p.font.SysFont("Bookman Old Style", 16, True, False)
    player_w, player_b = False, False
    selected_option = None

    while selected_option is None:
        screen.fill(p.Color("white"))
        text_1 = font.render("1>> Human vs Human", True, p.Color("black"))
        text_2 = font.render("2>> Easy White AI vs Human", True, p.Color("black"))
        text_3 = font.render("3>> Hard White AI vs Human", True, p.Color("black"))
        text_4 = font.render("4>> Human vs Easy Black AI", True, p.Color("black"))
        text_5 = font.render("5>> Human vs Hard Black AI", True, p.Color("black"))
        screen.blit(text_1, (WIDTH / 2 - text_1.get_width() / 2, HEIGHT / 3 + (text_1.get_height() + 10)))
        screen.blit(text_2, (WIDTH / 2 - text_2.get_width() / 2, HEIGHT / 3 + 2*(text_2.get_height() + 10)))
        screen.blit(text_3, (WIDTH / 2 - text_3.get_width() / 2, HEIGHT / 3 + 3*(text_3.get_height() + 10)))
        screen.blit(text_4, (WIDTH / 2 - text_4.get_width() / 2, HEIGHT / 3 + 4*(text_4.get_height() + 10)))
        screen.blit(text_5, (WIDTH / 2 - text_5.get_width() / 2, HEIGHT / 3 + 5*(text_5.get_height() + 10)))

        p.display.flip()
        clock.tick(30)

        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.key == p.K_1:
                    player_w = True
                    player_b = True
                    difficulty_w = 0
                    difficulty_b = 0
                    selected_option = "White: Human"
                elif e.key == p.K_2:
                    player_w = False
                    player_b = True
                    difficulty_w = 2
                    difficulty_b = 0
                    selected_option = "White: AI"
                elif e.key == p.K_3:
                    player_w = False
                    player_b = True
                    difficulty_w = 3
                    difficulty_b = 0
                    selected_option = "Black: Human"
                elif e.key == p.K_4:
                    player_w = True
                    player_b = False
                    difficulty_w = 0
                    difficulty_b = 2
                    selected_option = "Black: AI"
                elif e.key == p.K_5:
                    player_w = True
                    player_b = False
                    difficulty_w = 0
                    difficulty_b = 3
                    selected_option = "Black: AI"
            elif e.type == p.QUIT:
                p.quit()

    return player_w, player_b, difficulty_w, difficulty_b



if __name__ == "__main__":
    main()
