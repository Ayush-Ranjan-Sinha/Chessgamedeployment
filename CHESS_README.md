# Two-Player Chess Game

A fully functional two-player chess game built with Python and Pygame.

## Features

- Complete chess implementation with all standard pieces
- Two-player local gameplay
- Visual board with piece movement highlighting
- Check and checkmate detection
- Stalemate detection
- Pawn promotion (automatically promotes to Queen)
- Valid move highlighting
- Turn-based gameplay
- Game reset functionality

## Installation

1. Make sure you have Python 3.6 or higher installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python chess_game.py
   ```

2. Game Controls:
   - **Left Click**: Select a piece or make a move
   - **Click on a piece**: Select it and see valid moves highlighted in green
   - **Click on a highlighted square**: Move the selected piece there
   - **Click on the same piece again**: Deselect it
   - **R key**: Restart the game (only available when game is over)

3. Game Rules:
   - White always goes first
   - Players alternate turns
   - Select your piece by clicking on it
   - Valid moves will be highlighted in green
   - Selected piece will be highlighted in blue
   - The game automatically detects check, checkmate, and stalemate
   - Pawns automatically promote to Queens when reaching the opposite end

## Game Components

- **chess_game.py**: Main game file with pygame interface
- **chess_board.py**: Board logic and game state management
- **chess_pieces.py**: Individual piece classes with movement rules
- **requirements.txt**: Python dependencies

## Game Display

- The board uses a brown checkered pattern
- Pieces are displayed using Unicode chess symbols
- Current player is shown at the top left
- Game over messages appear at the top center
- Restart instructions appear when the game ends

## Technical Features

- Object-oriented design with separate classes for pieces and board
- Proper move validation for all piece types
- Check detection prevents illegal moves
- Checkmate and stalemate detection
- Clean separation of game logic and display code

## Piece Movement

- **Pawn**: Moves forward one square, captures diagonally, two squares from starting position
- **Rook**: Moves horizontally and vertically any number of squares
- **Bishop**: Moves diagonally any number of squares
- **Knight**: Moves in an L-shape (2+1 squares)
- **Queen**: Combines rook and bishop movements
- **King**: Moves one square in any direction

Enjoy playing chess!
