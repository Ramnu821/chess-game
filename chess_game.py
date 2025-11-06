import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
BOARD_SIZE = 8
SQUARE_SIZE = (WINDOW_SIZE - 40) // BOARD_SIZE  # Slightly smaller for border
BORDER_SIZE = 20  # Border width
LIGHT_SQUARE = (240, 217, 181)   # Light brown/beige
DARK_SQUARE = (181, 136, 99)     # Dark brown
BORDER_COLOR = (121, 72, 57)     # Darker brown border
HIGHLIGHT = (255, 246, 127)      # Soft yellow highlight
GOLD = (218, 165, 32)
MOVE_HIGHLIGHT = (144, 238, 144)  # Light green for possible moves
CAPTURE_HIGHLIGHT = (255, 160, 160)  # Light red for possible captures

# Board coordinates style
COORD_COLOR = (80, 45, 33)  # Dark brown for coordinates
COORD_SIZE = 15

def create_icon():
    # Create a surface for the icon (32x32 is a common size for icons)
    icon_surface = pygame.Surface((32, 32))
    icon_surface.fill((255, 255, 255))  # White background
    
    # Draw a crown shape
    points = [(16, 5),   # Top middle point
             (24, 15),   # Right point
             (20, 20),   # Right inner
             (16, 15),   # Middle inner
             (12, 20),   # Left inner
             (8, 15),    # Left point
             (16, 5)]    # Back to top
    
    # Draw crown outline
    pygame.draw.polygon(icon_surface, GOLD, points)
    pygame.draw.rect(icon_surface, GOLD, (8, 20, 16, 7))  # Base of crown
    
    # Add some details
    pygame.draw.circle(icon_surface, (255, 0, 0), (16, 12), 2)  # Center jewel
    pygame.draw.circle(icon_surface, (0, 0, 255), (10, 15), 2)  # Left jewel
    pygame.draw.circle(icon_surface, (0, 255, 0), (22, 15), 2)  # Right jewel
    
    return icon_surface

# Initialize the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Chess Game')
pygame.display.set_icon(create_icon())

class ChessPiece:
    def __init__(self, color, piece_type, position):
        self.color = color
        self.piece_type = piece_type
        self.position = position
        self.has_moved = False

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_piece = None
        self.current_player = 'white'
        self.ai_playing = True  # Enable AI opponent
        self.setup_board()

    def setup_board(self):
        # Setup pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        
        # Set up white pieces
        for i in range(BOARD_SIZE):
            self.board[1][i] = ChessPiece('white', 'pawn', (1, i))
            self.board[0][i] = ChessPiece('white', piece_order[i], (0, i))

        # Set up black pieces
        for i in range(BOARD_SIZE):
            self.board[6][i] = ChessPiece('black', 'pawn', (6, i))
            self.board[7][i] = ChessPiece('black', piece_order[i], (7, i))

    def get_piece(self, pos):
        row, col = pos
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

    def move_piece(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        piece = self.board[start_row][start_col]
        if piece and piece.color == self.current_player:
            # Basic move validation
            if self.is_valid_move(start_pos, end_pos):
                self.board[end_row][end_col] = piece
                self.board[start_row][start_col] = None
                piece.position = end_pos
                piece.has_moved = True
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                return True
        return False

    def is_path_clear(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        row_step = 0 if start_row == end_row else (end_row - start_row) // abs(end_row - start_row)
        col_step = 0 if start_col == end_col else (end_col - start_col) // abs(end_col - start_col)
        
        current_row = start_row + row_step
        current_col = start_col + col_step
        
        while (current_row, current_col) != (end_row, end_col):
            if self.get_piece((current_row, current_col)) is not None:
                return False
            current_row += row_step
            current_col += col_step
            
        return True

    def is_valid_move(self, start_pos, end_pos):
        piece = self.get_piece(start_pos)
        if not piece:
            return False

        end_piece = self.get_piece(end_pos)
        if end_piece and end_piece.color == piece.color:
            return False

        # Basic movement validation for each piece type
        valid_move = False
        if piece.piece_type == 'pawn':
            valid_move = self.is_valid_pawn_move(start_pos, end_pos)
        elif piece.piece_type == 'rook':
            valid_move = self.is_valid_rook_move(start_pos, end_pos)
        elif piece.piece_type == 'knight':
            valid_move = self.is_valid_knight_move(start_pos, end_pos)
        elif piece.piece_type == 'bishop':
            valid_move = self.is_valid_bishop_move(start_pos, end_pos)
        elif piece.piece_type == 'queen':
            valid_move = self.is_valid_queen_move(start_pos, end_pos)
        elif piece.piece_type == 'king':
            valid_move = self.is_valid_king_move(start_pos, end_pos)

        if not valid_move:
            return False

        # Check if path is clear (except for knights which can jump)
        if piece.piece_type != 'knight':
            return self.is_path_clear(start_pos, end_pos)
            
        return True

    def is_valid_pawn_move(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.get_piece(start_pos)
        
        direction = 1 if piece.color == 'white' else -1
        if start_col == end_col:  # Moving forward
            if end_row == start_row + direction:  # Moving one square
                return self.get_piece(end_pos) is None
            elif not piece.has_moved and end_row == start_row + 2 * direction:  # First move, two squares
                return (self.get_piece((start_row + direction, start_col)) is None and 
                       self.get_piece(end_pos) is None)
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction:  # Capturing
            return self.get_piece(end_pos) is not None
        return False

    def is_valid_rook_move(self, start_pos, end_pos):
        # Rook must move either horizontally or vertically
        return start_pos[0] == end_pos[0] or start_pos[1] == end_pos[1]

    def is_valid_knight_move(self, start_pos, end_pos):
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def is_valid_bishop_move(self, start_pos, end_pos):
        # Bishop must move diagonally
        return abs(start_pos[0] - end_pos[0]) == abs(start_pos[1] - end_pos[1])

    def is_valid_queen_move(self, start_pos, end_pos):
        # Queen can move like a rook or bishop
        return (self.is_valid_rook_move(start_pos, end_pos) or 
                self.is_valid_bishop_move(start_pos, end_pos))

    def is_valid_king_move(self, start_pos, end_pos):
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return row_diff <= 1 and col_diff <= 1

    def get_all_valid_moves(self, color):
        moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    start_pos = (row, col)
                    moves.extend(self.get_valid_moves_for_piece(start_pos))
        return moves

    def get_valid_moves_for_piece(self, start_pos):
        moves = []
        piece = self.get_piece(start_pos)
        if not piece:
            return moves

        for end_row in range(BOARD_SIZE):
            for end_col in range(BOARD_SIZE):
                end_pos = (end_row, end_col)
                if self.is_valid_move(start_pos, end_pos):
                    moves.append((start_pos, end_pos))
        return moves

    def evaluate_board(self):
        piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3,
            'rook': 5,
            'queen': 9,
            'king': 100
        }
        
        score = 0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    value = piece_values[piece.piece_type]
                    if piece.color == 'white':
                        score += value
                    else:
                        score -= value
        return score

    def make_ai_move(self):
        if not self.ai_playing or self.current_player == 'white':
            return False

        # Get all valid moves for black pieces
        valid_moves = self.get_all_valid_moves('black')
        if not valid_moves:
            return False

        # Evaluate each move
        best_move = None
        best_score = float('inf')  # We want to minimize the score (white's advantage)
        
        for start_pos, end_pos in valid_moves:
            # Temporarily make the move
            temp_piece = self.board[end_pos[0]][end_pos[1]]
            self.board[end_pos[0]][end_pos[1]] = self.board[start_pos[0]][start_pos[1]]
            self.board[start_pos[0]][start_pos[1]] = None

            # Evaluate the resulting position
            score = self.evaluate_board()

            # Undo the move
            self.board[start_pos[0]][start_pos[1]] = self.board[end_pos[0]][end_pos[1]]
            self.board[end_pos[0]][end_pos[1]] = temp_piece

            # Update best move if this is better
            if score < best_score:
                best_score = score
                best_move = (start_pos, end_pos)

        # Make the best move found
        if best_move:
            start_pos, end_pos = best_move
            self.move_piece(start_pos, end_pos)
            return True
        return False

def draw_piece(screen, piece, center_x, center_y, square_size):
    piece_color = (30, 30, 30) if piece.color == 'black' else (230, 230, 230)
    outline_color = (0, 0, 0) if piece.color == 'black' else (180, 180, 180)
    size = square_size // 2
    
    if piece.piece_type == 'pawn':
        # Draw pawn (simple chess piece shape)
        pygame.draw.circle(screen, piece_color, (center_x, center_y - size//4), size//3)
        points = [
            (center_x - size//3, center_y + size//4),
            (center_x + size//3, center_y + size//4),
            (center_x, center_y - size//4)
        ]
        pygame.draw.polygon(screen, piece_color, points)
        pygame.draw.lines(screen, outline_color, True, points, 2)
        
    elif piece.piece_type == 'rook':
        # Draw rook (castle tower)
        rect = pygame.Rect(center_x - size//3, center_y - size//2, 2*size//3, size)
        pygame.draw.rect(screen, piece_color, rect)
        pygame.draw.rect(screen, outline_color, rect, 2)
        # Battlements
        for i in range(3):
            x = center_x - size//3 + (i * size//3)
            pygame.draw.rect(screen, piece_color, (x, center_y - size//2 - size//6, size//4, size//6))
            pygame.draw.rect(screen, outline_color, (x, center_y - size//2 - size//6, size//4, size//6), 2)
            
    elif piece.piece_type == 'knight':
        # Draw knight (horse head)
        points = [
            (center_x - size//3, center_y + size//3),
            (center_x - size//6, center_y - size//3),
            (center_x, center_y - size//2),
            (center_x + size//4, center_y - size//4),
            (center_x + size//3, center_y),
            (center_x + size//3, center_y + size//3)
        ]
        pygame.draw.polygon(screen, piece_color, points)
        pygame.draw.lines(screen, outline_color, True, points, 2)
        # Eye
        pygame.draw.circle(screen, outline_color, (center_x + size//8, center_y - size//4), 2)
        
    elif piece.piece_type == 'bishop':
        # Draw bishop (pointed hat)
        points = [
            (center_x - size//3, center_y + size//3),
            (center_x, center_y - size//2),
            (center_x + size//3, center_y + size//3)
        ]
        pygame.draw.polygon(screen, piece_color, points)
        pygame.draw.lines(screen, outline_color, True, points, 2)
        # Cross
        pygame.draw.line(screen, outline_color, 
                        (center_x, center_y - size//2),
                        (center_x, center_y - size//2 + size//4), 3)
        pygame.draw.line(screen, outline_color,
                        (center_x - size//6, center_y - size//2 + size//8),
                        (center_x + size//6, center_y - size//2 + size//8), 3)
        
    elif piece.piece_type == 'queen':
        # Draw queen (crown with points)
        points = [
            (center_x - size//2, center_y + size//3),
            (center_x - size//3, center_y - size//6),
            (center_x - size//6, center_y + size//6),
            (center_x, center_y - size//3),
            (center_x + size//6, center_y + size//6),
            (center_x + size//3, center_y - size//6),
            (center_x + size//2, center_y + size//3)
        ]
        pygame.draw.polygon(screen, piece_color, points)
        pygame.draw.lines(screen, outline_color, True, points, 2)
        # Crown jewels
        for i in range(-2, 3):
            x = center_x + i * (size//6)
            y = center_y + abs(i) * (size//8)
            pygame.draw.circle(screen, (218, 165, 32), (x, y), 3)  # Gold dots
            
    elif piece.piece_type == 'king':
        # Draw king (crown with cross)
        points = [
            (center_x - size//2, center_y + size//3),
            (center_x - size//3, center_y),
            (center_x, center_y - size//2),
            (center_x + size//3, center_y),
            (center_x + size//2, center_y + size//3)
        ]
        pygame.draw.polygon(screen, piece_color, points)
        pygame.draw.lines(screen, outline_color, True, points, 2)
        # Cross
        pygame.draw.line(screen, outline_color,
                        (center_x, center_y - size//2),
                        (center_x, center_y - size//2 + size//3), 4)
        pygame.draw.line(screen, outline_color,
                        (center_x - size//6, center_y - size//2 + size//6),
                        (center_x + size//6, center_y - size//2 + size//6), 4)

def draw_board(screen, board, selected_pos=None):
    # Draw the border
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WINDOW_SIZE, WINDOW_SIZE))
    
    # Draw the chess board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            if (row, col) == selected_pos:
                color = HIGHLIGHT
            
            # Calculate position with border offset
            x = BORDER_SIZE + col * SQUARE_SIZE
            y = BORDER_SIZE + row * SQUARE_SIZE
            
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            
            # Draw coordinates
            if col == 0:  # Draw row numbers on the left
                font = pygame.font.Font(None, COORD_SIZE)
                text = font.render(str(8 - row), True, COORD_COLOR)
                screen.blit(text, (5, y + SQUARE_SIZE//2 - COORD_SIZE//3))
                
            if row == 7:  # Draw column letters at the bottom
                font = pygame.font.Font(None, COORD_SIZE)
                text = font.render(chr(97 + col), True, COORD_COLOR)  # 'a' through 'h'
                screen.blit(text, (x + SQUARE_SIZE//2 - COORD_SIZE//4, 
                                 WINDOW_SIZE - BORDER_SIZE + 5))

    # Draw possible moves if a piece is selected
    if selected_pos is not None:
        valid_moves = board.get_valid_moves_for_piece(selected_pos)
        for start_pos, end_pos in valid_moves:
            end_row, end_col = end_pos
            center_x = BORDER_SIZE + end_col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = BORDER_SIZE + end_row * SQUARE_SIZE + SQUARE_SIZE // 2
            
            # Determine if it's a capture move
            end_piece = board.get_piece(end_pos)
            if end_piece:
                # Draw red circle for capture moves
                pygame.draw.circle(screen, CAPTURE_HIGHLIGHT, (center_x, center_y), SQUARE_SIZE // 3)
                pygame.draw.circle(screen, (200, 0, 0), (center_x, center_y), SQUARE_SIZE // 3, 2)
            else:
                # Draw green circle for normal moves
                pygame.draw.circle(screen, MOVE_HIGHLIGHT, (center_x, center_y), SQUARE_SIZE // 4)
                pygame.draw.circle(screen, (0, 150, 0), (center_x, center_y), SQUARE_SIZE // 4, 2)

    # Draw the pieces
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board.get_piece((row, col))
            if piece:
                center_x = BORDER_SIZE + col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = BORDER_SIZE + row * SQUARE_SIZE + SQUARE_SIZE // 2
                draw_piece(screen, piece, center_x, center_y, SQUARE_SIZE)

def main():
    board = ChessBoard()
    selected_pos = None
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and board.current_player == 'white':
                x, y = pygame.mouse.get_pos()
                # Adjust for border
                x = x - BORDER_SIZE
                y = y - BORDER_SIZE
                # Check if click is within the board
                if 0 <= x < BOARD_SIZE * SQUARE_SIZE and 0 <= y < BOARD_SIZE * SQUARE_SIZE:
                    clicked_pos = (y // SQUARE_SIZE, x // SQUARE_SIZE)
                
                if selected_pos is None:
                    piece = board.get_piece(clicked_pos)
                    if piece and piece.color == board.current_player:
                        selected_pos = clicked_pos
                else:
                    if board.move_piece(selected_pos, clicked_pos):
                        print(f"Player moved from {selected_pos} to {clicked_pos}")
                        # AI will make its move after a short delay
                        pygame.time.wait(500)  # Wait 500ms before AI moves
                        if board.make_ai_move():
                            print("AI made its move")
                    selected_pos = None

        screen.fill((255, 255, 255))
        draw_board(screen, board, selected_pos)
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

if __name__ == "__main__":
    main()