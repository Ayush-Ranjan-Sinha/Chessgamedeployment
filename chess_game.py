import pygame
import sys
from chess_board import ChessBoard
from chess_pieces import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_SIZE = 512
BOARD_OFFSET_X = (WINDOW_WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (255, 255, 0, 128)
VALID_MOVE_COLOR = (0, 255, 0, 128)
SELECTED_COLOR = (0, 0, 255, 128)

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = ChessBoard()
        self.selected_square = None
        self.valid_moves = []
        self.current_player = 'white'
        self.game_over = False
        self.winner = None
        
    def get_square_from_pos(self, pos):
        """Convert mouse position to board square coordinates"""
        x, y = pos
        if (BOARD_OFFSET_X <= x <= BOARD_OFFSET_X + BOARD_SIZE and 
            BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + BOARD_SIZE):
            col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
            row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
            return (row, col)
        return None
    
    def get_pos_from_square(self, square):
        """Convert board square to pixel position"""
        row, col = square
        x = BOARD_OFFSET_X + col * SQUARE_SIZE
        y = BOARD_OFFSET_Y + row * SQUARE_SIZE
        return (x, y)
    
    def draw_board(self):
        """Draw the chess board"""
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                x = BOARD_OFFSET_X + col * SQUARE_SIZE
                y = BOARD_OFFSET_Y + row * SQUARE_SIZE
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_pieces(self):
        """Draw all pieces on the board"""
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                    y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
                    self.draw_piece(piece, x, y)
    
    def draw_piece(self, piece, x, y):
        """Draw a single piece"""
        font = pygame.font.Font(None, 48)
        piece_symbols = {
            'king': '♔' if piece.color == 'white' else '♚',
            'queen': '♕' if piece.color == 'white' else '♛',
            'rook': '♖' if piece.color == 'white' else '♜',
            'bishop': '♗' if piece.color == 'white' else '♝',
            'knight': '♘' if piece.color == 'white' else '♞',
            'pawn': '♙' if piece.color == 'white' else '♟'
        }
        
        symbol = piece_symbols.get(piece.piece_type, '?')
        text = font.render(symbol, True, BLACK)
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)
    
    def draw_highlights(self):
        """Draw highlights for selected square and valid moves"""
        # Highlight selected square
        if self.selected_square:
            x, y = self.get_pos_from_square(self.selected_square)
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            highlight_surface.set_alpha(128)
            highlight_surface.fill(SELECTED_COLOR[:3])
            self.screen.blit(highlight_surface, (x, y))
        
        # Highlight valid moves
        for move in self.valid_moves:
            x, y = self.get_pos_from_square(move)
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            highlight_surface.set_alpha(128)
            highlight_surface.fill(VALID_MOVE_COLOR[:3])
            self.screen.blit(highlight_surface, (x, y))
    
    def draw_ui(self):
        """Draw game UI elements"""
        font = pygame.font.Font(None, 36)
        
        # Current player
        player_text = f"Current Player: {self.current_player.title()}"
        text_surface = font.render(player_text, True, BLACK)
        self.screen.blit(text_surface, (10, 10))
        
        # Game over message
        if self.game_over:
            if self.winner:
                winner_text = f"{self.winner.title()} Wins!"
            else:
                winner_text = "Game Over!"
            text_surface = font.render(winner_text, True, BLACK)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.screen.blit(text_surface, text_rect)
    
    def handle_click(self, pos):
        """Handle mouse clicks on the board"""
        if self.game_over:
            return
            
        square = self.get_square_from_pos(pos)
        if not square:
            return
        
        row, col = square
        
        # If no square is selected, select this square if it has a piece of current player
        if self.selected_square is None:
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.current_player:
                self.selected_square = square
                self.valid_moves = self.board.get_valid_moves(row, col)
        
        # If a square is already selected
        else:
            # If clicking on the same square, deselect it
            if square == self.selected_square:
                self.selected_square = None
                self.valid_moves = []
            
            # If clicking on a valid move, make the move
            elif square in self.valid_moves:
                old_row, old_col = self.selected_square
                success = self.board.make_move(old_row, old_col, row, col)
                
                if success:
                    # Switch players
                    self.current_player = 'black' if self.current_player == 'white' else 'white'
                    
                    # Check for game over conditions
                    if self.board.is_checkmate(self.current_player):
                        self.game_over = True
                        self.winner = 'black' if self.current_player == 'white' else 'white'
                    elif self.board.is_stalemate(self.current_player):
                        self.game_over = True
                        self.winner = None
                
                self.selected_square = None
                self.valid_moves = []
            
            # If clicking on another piece of the same color, select it
            else:
                piece = self.board.get_piece(row, col)
                if piece and piece.color == self.current_player:
                    self.selected_square = square
                    self.valid_moves = self.board.get_valid_moves(row, col)
                else:
                    self.selected_square = None
                    self.valid_moves = []
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        # Reset game
                        self.board = ChessBoard()
                        self.selected_square = None
                        self.valid_moves = []
                        self.current_player = 'white'
                        self.game_over = False
                        self.winner = None
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_board()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_ui()
            
            # Show restart instruction when game is over
            if self.game_over:
                font = pygame.font.Font(None, 24)
                restart_text = "Press R to restart"
                text_surface = font.render(restart_text, True, BLACK)
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 80))
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
