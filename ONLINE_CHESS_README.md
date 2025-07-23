# Online Multiplayer Chess Game

A fully functional online multiplayer chess game built with Flask, Socket.IO, and JavaScript. Two players can connect from anywhere in the world using a shared game code.

## Features

### 🎮 Game Features
- **Online Multiplayer**: Play with anyone, anywhere
- **Room-based System**: Share a 6-character game code to connect
- **Real-time Gameplay**: Instant move synchronization via WebSockets
- **Complete Chess Rules**: All standard chess pieces and rules implemented
- **Check & Checkmate Detection**: Proper game state validation
- **Stalemate Detection**: Handles draw conditions
- **Pawn Promotion**: Automatically promotes pawns to queens
- **Move Validation**: Prevents illegal moves and check situations

### 🌐 Web Features
- **Responsive Design**: Works on desktop and mobile devices
- **Beautiful UI**: Clean, modern interface with smooth animations
- **Visual Feedback**: Highlighted valid moves and selected pieces
- **Game State Display**: Current player, game status, and player info
- **Real-time Updates**: Live connection status and game events
- **Game Management**: Reset games and handle disconnections

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python app.py
```

### 3. Open in Browser
Navigate to `http://localhost:5000` in your web browser

### 4. Play Chess!
- **Create Game**: Click "Create New Game" to get a 6-character code
- **Join Game**: Enter the code to join an existing game
- **Share Code**: Send the game code to your opponent
- **Play**: Once both players join and click "Ready", the game starts!

## How to Play

### Creating a Game
1. Go to the homepage
2. Click "Create New Game"
3. Share the 6-character code with your opponent
4. Wait for them to join
5. Click "Ready" when both players are connected

### Joining a Game
1. Get the game code from your opponent
2. Enter it in the "Join Game" field
3. Click "Join Game"
4. Click "Ready" when both players are connected

### Playing the Game
- **Your Turn**: Click on your piece to select it
- **Valid Moves**: Green highlights show where you can move
- **Make Move**: Click on a highlighted square to move there
- **Turn Indicator**: Current player is highlighted in green
- **Game Status**: Shows whose turn it is or if the game is over

## Game Controls

### During Game
- **Select Piece**: Click on any of your pieces
- **Move Piece**: Click on a green highlighted square
- **Deselect**: Click the same piece again or click elsewhere
- **Reset Game**: Click "Reset Game" to start over (both players must be ready again)

### Navigation
- **Back to Home**: Return to the main menu
- **Browser Back**: Use browser back button to leave game

## Technical Architecture

### Backend (Python/Flask)
- **Flask**: Web framework for serving pages and handling HTTP requests
- **Socket.IO**: Real-time bidirectional communication
- **Game Logic**: Complete chess engine with move validation
- **Room Management**: Handles multiple concurrent games

### Frontend (HTML/CSS/JavaScript)
- **Socket.IO Client**: Real-time communication with server
- **Interactive Board**: Click-based piece selection and movement
- **Responsive Design**: Works on all screen sizes
- **Visual Feedback**: Animations and highlighting for better UX

### Game State Management
- **Server-side Validation**: All moves validated on the server
- **Real-time Sync**: Game state synchronized across all clients
- **Connection Handling**: Graceful handling of disconnections
- **Game Persistence**: Games persist until both players leave

## File Structure

```
├── app.py                      # Flask server and Socket.IO handlers
├── online_chess_board.py       # Chess board logic for web version
├── chess_pieces.py             # Chess piece classes and movement rules
├── templates/
│   ├── index.html             # Homepage for creating/joining games
│   └── game.html              # Game page with interactive board
├── requirements.txt           # Python dependencies
└── README files...
```

## Deployment Options

### Local Network
Run the server and access it from any device on your local network:
```bash
python app.py
# Access via http://YOUR_IP:5000
```

### Public Deployment
Deploy to platforms like:
- **Heroku**: Easy deployment with git integration
- **PythonAnywhere**: Simple Python hosting
- **DigitalOcean**: VPS hosting with more control
- **AWS/GCP**: Cloud platforms for scalability

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Features in Detail

### Real-time Communication
- **WebSocket Connection**: Instant bidirectional communication
- **Room-based Architecture**: Players join specific game rooms
- **Event-driven Updates**: Board state, moves, and game events
- **Connection Management**: Handles joins, leaves, and disconnections

### Game State Management
- **Server Authority**: All game logic runs on the server
- **Move Validation**: Prevents cheating and invalid moves
- **Turn Management**: Enforces proper turn-based gameplay
- **Game Over Detection**: Checkmate, stalemate, and draw conditions

### User Experience
- **Intuitive Controls**: Simple click-to-move interface
- **Visual Feedback**: Clear indicators for selected pieces and valid moves
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Error Handling**: User-friendly error messages and recovery

## Security Considerations

- **Server-side Validation**: All moves validated on the server
- **Room Isolation**: Players can only affect their own game
- **Input Sanitization**: Game codes and moves are validated
- **Connection Security**: WebSocket connections with CORS protection

## Troubleshooting

### Common Issues
1. **Connection Failed**: Check if server is running and port is open
2. **Game Code Invalid**: Ensure code is exactly 6 characters
3. **Opponent Not Joining**: Check if game code was shared correctly
4. **Moves Not Working**: Ensure it's your turn and move is valid

### Port Issues
If port 5000 is already in use, modify the last line in `app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

## Future Enhancements

- **Spectator Mode**: Allow others to watch games
- **Game History**: Save and replay games
- **Timer Support**: Add chess clocks
- **Rating System**: Track player ratings
- **Tournament Mode**: Bracket-style tournaments
- **Custom Themes**: Different board and piece styles

## Contributing

Feel free to fork the project and submit pull requests for:
- Bug fixes
- New features
- UI improvements
- Performance optimizations
- Documentation updates

## License

This project is open source and available under the MIT License.

---

**Enjoy playing online chess!** 🎯♟️

For questions or support, please check the code comments or create an issue in the repository.
