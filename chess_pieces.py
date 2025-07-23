class ChessPiece:
    def __init__(self, color, piece_type, row, col):
        self.color = color
        self.piece_type = piece_type
        self.row = row
        self.col = col
        self.has_moved = False
    
    def move_to(self, row, col):
        """Move the piece to a new position"""
        self.row = row
        self.col = col
        self.has_moved = True
    
    def is_valid_move(self, to_row, to_col, board):
        """Check if a move is valid for this piece"""
        # This will be overridden by subclasses
        return False
    
    def get_possible_moves(self, board):
        """Get all possible moves for this piece"""
        moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col, board):
                    moves.append((row, col))
        return moves

class Pawn(ChessPiece):
    def __init__(self, color, row, col):
        super().__init__(color, 'pawn', row, col)
    
    def is_valid_move(self, to_row, to_col, board):
        from_row, from_col = self.row, self.col
        
        # Can't move to the same square
        if to_row == from_row and to_col == from_col:
            return False
        
        # Can't move off the board
        if to_row < 0 or to_row > 7 or to_col < 0 or to_col > 7:
            return False
        
        direction = -1 if self.color == 'white' else 1
        
        # Forward move
        if from_col == to_col:
            # One square forward
            if to_row == from_row + direction:
                return board.get_piece(to_row, to_col) is None
            # Two squares forward from starting position
            elif to_row == from_row + 2 * direction and not self.has_moved:
                return (board.get_piece(to_row, to_col) is None and 
                        board.get_piece(from_row + direction, from_col) is None)
        
        # Diagonal capture
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target_piece = board.get_piece(to_row, to_col)
            return target_piece is not None and target_piece.color != self.color
        
        return False

class Rook(ChessPiece):
    def __init__(self, color, row, col):
        super().__init__(color, 'rook', row, col)
    
    def is_valid_move(self, to_row, to_col, board):
        from_row, from_col = self.row, self.col
        
        # Can't move to the same square
        if to_row == from_row and to_col == from_col:
            return False
        
        # Can't move off the board
        if to_row < 0 or to_row > 7 or to_col < 0 or to_col > 7:
            return False
        
        # Must move horizontally or vertically
        if from_row != to_row and from_col != to_col:
            return False
        
        # Check for pieces in the path
        if from_row == to_row:  # Horizontal move
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if board.get_piece(from_row, col) is not None:
                    return False
        else:  # Vertical move
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if board.get_piece(row, from_col) is not None:
                    return False
        
        # Check destination
        target_piece = board.get_piece(to_row, to_col)
        return target_piece is None or target_piece.color != self.color

class Bishop(ChessPiece):
    def __init__(self, color, row, col):
        super().__init__(color, 'bishop', row, col)
    
    def is_valid_move(self, to_row, to_col, board):
        from_row, from_col = self.row, self.col
        
        # Can't move to the same square
        if to_row == from_row and to_col == from_col:
            return False
        
        # Can't move off the board
        if to_row < 0 or to_row > 7 or to_col < 0 or to_col > 7:
            return False
        
        # Must move diagonally
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False
        
        # Check for pieces in the path
        row_direction = 1 if to_row > from_row else -1
        col_direction = 1 if to_col > from_col else -1
        
        steps = abs(to_row - from_row)
        for i in range(1, steps):
            check_row = from_row + i * row_direction
            check_col = from_col + i * col_direction
            if board.get_piece(check_row, check_col) is not None:
                return False
        
        # Check destination
        target_piece = board.get_piece(to_row, to_col)
        return target_piece is None or target_piece.color != self.color

class Knight(ChessPiece):
    def __init__(self, color, row, col):
        super().__init__(color, 'knight', row, col)
    
    def is_valid_move(self, to_row, to_col, board):
        from_row, from_col = self.row, self.col
        
        # Can't move to the same square
        if to_row == from_row and to_col == from_col:
            return False
        
        # Can't move off the board
        if to_row < 0 or to_row > 7 or to_col < 0 or to_col > 7:
            return False
        
        # Knight moves in L-shape
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if not ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)):
            return False
        
        # Check destination
        target_piece = board.get_piece(to_row, to_col)
        return target_piece is None or target_piece.color != self.color

class Queen(ChessPiece):
    def __init__(self, color, row, col):
        super().__init__(color, 'queen', row, col)
    
    def is_valid_move(self, to_row, to_col, board):
        from_row, from_col = self.row, self.col
        
        # Can't move to the same square
        if to_row == from_row and to_col == from_col:
            return False
        
        # Can't move off the board
        if to_row < 0 or to_row > 7 or to_col < 0 or to_col > 7:
            return False
        
        # Queen moves like rook or bishop
        is_horizontal = from_row == to_row
        is_vertical = from_col == to_col
        is_diagonal = abs(from_row - to_row) == abs(from_col - to_col)
        
        if not (is_horizontal or is_vertical or is_diagonal):
            return False
        
        # Check for pieces in the path
        if is_horizontal:
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if board.get_piece(from_row, col) is not None:
                    return False
        elif is_vertical:
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if board.get_piece(row, from_col) is not None:
                    return False
        else:  # Diagonal
            row_direction = 1 if to_row > from_row else -1
            col_direction = 1 if to_col > from_col else -1
            
            steps = abs(to_row - from_row)
            for i in range(1, steps):
                check_row = from_row + i * row_direction
                check_col = from_col + i * col_direction
                if board.get_piece(check_row, check_col) is not None:
                    return False
        
        # Check destination
        target_piece = board.get_piece(to_row, to_col)
        return target_piece is None or target_piece.color != self.color

class King(ChessPiece):
    def __init__(self, color, row, col):
        super().__init__(color, 'king', row, col)
    
    def is_valid_move(self, to_row, to_col, board):
        from_row, from_col = self.row, self.col
        
        # Can't move to the same square
        if to_row == from_row and to_col == from_col:
            return False
        
        # Can't move off the board
        if to_row < 0 or to_row > 7 or to_col < 0 or to_col > 7:
            return False
        
        # King moves one square in any direction
        if abs(to_row - from_row) > 1 or abs(to_col - from_col) > 1:
            return False
        
        # Check destination
        target_piece = board.get_piece(to_row, to_col)
        return target_piece is None or target_piece.color != self.color
