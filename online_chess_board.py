from chess_pieces import *

class OnlineChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.white_king = None
        self.black_king = None
        self.setup_board()
    
    def setup_board(self):
        """Initialize the chess board with pieces in starting positions"""
        # Place pawns
        for col in range(8):
            self.board[1][col] = Pawn('black', 1, col)
            self.board[6][col] = Pawn('white', 6, col)
        
        # Place rooks
        self.board[0][0] = Rook('black', 0, 0)
        self.board[0][7] = Rook('black', 0, 7)
        self.board[7][0] = Rook('white', 7, 0)
        self.board[7][7] = Rook('white', 7, 7)
        
        # Place knights
        self.board[0][1] = Knight('black', 0, 1)
        self.board[0][6] = Knight('black', 0, 6)
        self.board[7][1] = Knight('white', 7, 1)
        self.board[7][6] = Knight('white', 7, 6)
        
        # Place bishops
        self.board[0][2] = Bishop('black', 0, 2)
        self.board[0][5] = Bishop('black', 0, 5)
        self.board[7][2] = Bishop('white', 7, 2)
        self.board[7][5] = Bishop('white', 7, 5)
        
        # Place queens
        self.board[0][3] = Queen('black', 0, 3)
        self.board[7][3] = Queen('white', 7, 3)
        
        # Place kings
        self.black_king = King('black', 0, 4)
        self.white_king = King('white', 7, 4)
        self.board[0][4] = self.black_king
        self.board[7][4] = self.white_king
    
    def get_piece(self, row, col):
        """Get the piece at the given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        """Set a piece at the given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
            if piece:
                piece.row = row
                piece.col = col
    
    def remove_piece(self, row, col):
        """Remove a piece from the given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = None
    
    def get_valid_moves(self, row, col):
        """Get all valid moves for a piece at the given position"""
        piece = self.get_piece(row, col)
        if not piece:
            return []
        
        valid_moves = []
        for to_row in range(8):
            for to_col in range(8):
                if piece.is_valid_move(to_row, to_col, self):
                    # Check if move would put own king in check
                    if not self.would_move_cause_check(row, col, to_row, to_col, piece.color):
                        valid_moves.append((to_row, to_col))
        
        return valid_moves
    
    def make_move(self, from_row, from_col, to_row, to_col):
        """Make a move on the board"""
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False
        
        # Check if the move is valid
        if not piece.is_valid_move(to_row, to_col, self):
            return False
        
        # Check if move would put own king in check
        if self.would_move_cause_check(from_row, from_col, to_row, to_col, piece.color):
            return False
        
        # Make the move
        captured_piece = self.get_piece(to_row, to_col)
        self.set_piece(to_row, to_col, piece)
        self.remove_piece(from_row, from_col)
        piece.move_to(to_row, to_col)
        
        # Handle pawn promotion
        if isinstance(piece, Pawn):
            if (piece.color == 'white' and to_row == 0) or (piece.color == 'black' and to_row == 7):
                # Promote to queen for simplicity
                new_queen = Queen(piece.color, to_row, to_col)
                new_queen.has_moved = True
                self.set_piece(to_row, to_col, new_queen)
        
        return True
    
    def is_square_attacked(self, row, col, by_color):
        """Check if a square is attacked by pieces of the given color"""
        for check_row in range(8):
            for check_col in range(8):
                piece = self.get_piece(check_row, check_col)
                if piece and piece.color == by_color:
                    if piece.is_valid_move(row, col, self):
                        return True
        return False
    
    def is_in_check(self, color):
        """Check if the king of the given color is in check"""
        king = self.white_king if color == 'white' else self.black_king
        opponent_color = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(king.row, king.col, opponent_color)
    
    def would_move_cause_check(self, from_row, from_col, to_row, to_col, color):
        """Check if a move would put the player's own king in check"""
        # Make a temporary move
        piece = self.get_piece(from_row, from_col)
        captured_piece = self.get_piece(to_row, to_col)
        
        # Simulate the move
        self.set_piece(to_row, to_col, piece)
        self.remove_piece(from_row, from_col)
        piece.row = to_row
        piece.col = to_col
        
        # Check if king is in check after the move
        in_check = self.is_in_check(color)
        
        # Undo the move
        self.set_piece(from_row, from_col, piece)
        self.set_piece(to_row, to_col, captured_piece)
        piece.row = from_row
        piece.col = from_col
        
        return in_check
    
    def get_all_valid_moves(self, color):
        """Get all valid moves for all pieces of the given color"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    valid_moves = self.get_valid_moves(row, col)
                    for move in valid_moves:
                        moves.append(((row, col), move))
        return moves
    
    def is_checkmate(self, color):
        """Check if the given color is in checkmate"""
        if not self.is_in_check(color):
            return False
        
        # If in check, see if there are any valid moves
        return len(self.get_all_valid_moves(color)) == 0
    
    def is_stalemate(self, color):
        """Check if the given color is in stalemate"""
        if self.is_in_check(color):
            return False
        
        # If not in check, see if there are any valid moves
        return len(self.get_all_valid_moves(color)) == 0
    
    def get_board_state(self):
        """Return the current state of the board for broadcasting, including check status and king positions"""
        board_state = []
        for row in self.board:
            board_state.append([{'piece_type': piece.__class__.__name__.lower() if piece else None,
                                 'color': piece.color if piece else None} for piece in row])
        # Add check status and king positions
        state = {
            'board': board_state,
            'white_king': {'row': self.white_king.row, 'col': self.white_king.col} if self.white_king else None,
            'black_king': {'row': self.black_king.row, 'col': self.black_king.col} if self.black_king else None,
            'white_in_check': self.is_in_check('white'),
            'black_in_check': self.is_in_check('black')
        }
        return state
    
    def copy(self):
        """Create a copy of the board"""
        new_board = OnlineChessBoard()
        new_board.board = [[None for _ in range(8)] for _ in range(8)]
        
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    # Create a new piece of the same type
                    piece_type = piece.__class__
                    new_piece = piece_type(piece.color, row, col)
                    new_piece.has_moved = piece.has_moved
                    new_board.set_piece(row, col, new_piece)
                    
                    # Update king references
                    if isinstance(new_piece, King):
                        if new_piece.color == 'white':
                            new_board.white_king = new_piece
                        else:
                            new_board.black_king = new_piece
        
        return new_board

