import pygame as p
from Chess import ChessBuddyEngine, ChessBuddyMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessBuddyEngine.GameState()
    valid_moves = gs.getValidMoves()
    move_made = False
    animate = False
    loadImages()
    running = True
    sq_selected = ()
    player_clicks = [] #keeps list of player clicks
    game_over = False

    player_one = True #true for human is white, false for AI is white
    player_two = False # same but for black



    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse events
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sq_selected == (row, col): #user clicks same square to deselect piece
                        sq_selected = ()  #deselect square
                        player_clicks = [] #clear playerclicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        move = ChessBuddyEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.getChessNotation())
                        if move in valid_moves:
                            gs.makeMove(move)
                            move_made = True
                            animate = True
                            sq_selected = ()
                            player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == p.K_r:
                    gs = ChessBuddyEngine.GameState()
                    valid_moves = gs.getValidMoves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        if not game_over and not human_turn:
            AI_move = ChessBuddyMoveFinder.findBestMoveMinMax(gs, valid_moves)
            #AI_move = ChessBuddyMoveFinder.findBestMove(gs, valid_moves)
            if AI_move is None:
                AI_move = ChessBuddyMoveFinder.findRandomMove(valid_moves)
            gs.makeMove(AI_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animateMove(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.getValidMoves()
            move_made = False
            animate = False

        drawGameState(screen, gs, valid_moves, sq_selected)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            game_over = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            #highlight possible moves
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))

def drawGameState(screen, gs, valid_moves, sq_selected):
    drawBoard(screen)
    highlightSquares(screen, gs, valid_moves, sq_selected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    framesPerSquare = 3
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.start_row + dR*frame/frameCount, move.start_col + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase piece moved
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)

        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color('Gray'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Black'))
    screen.blit(text_object, text_location.move(2,2))


if __name__ == "__main__":
    main()
