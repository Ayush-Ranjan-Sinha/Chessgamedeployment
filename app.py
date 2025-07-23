from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import random
import string
from online_chess_board import OnlineChessBoard

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active games
games = {}
players = {}

def generate_game_code():
    """Generate a unique 6-character game code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<game_code>')
def game(game_code):
    game_code = game_code.upper()
    print(f"DEBUG: Accessing game page for code: {game_code}")
    print(f"DEBUG: Active games: {list(games.keys())}")
    return render_template('game.html', game_code=game_code)

@socketio.on('create_game')
def handle_create_game():
    game_code = generate_game_code()
    while game_code in games:
        game_code = generate_game_code()
    
    games[game_code] = {
        'board': OnlineChessBoard(),
        'players': {},
        'current_player': 'white',
        'game_started': False,
        'game_over': False,
        'winner': None
    }
    
    player_id = str(uuid.uuid4())
    players[request.sid] = {
        'game_code': game_code,
        'player_id': player_id,
        'color': 'white'
    }
    
    games[game_code]['players'][player_id] = {
        'sid': request.sid,
        'color': 'white',
        'ready': False
    }
    
    join_room(game_code)
    
    print(f"DEBUG: Game created with code: {game_code}")
    print(f"DEBUG: Active games: {list(games.keys())}")
    
    emit('game_created', {
        'game_code': game_code,
        'player_color': 'white',
        'player_id': player_id
    })

@socketio.on('join_game')
def handle_join_game(data):
    game_code = data['game_code'].upper()
    
    print(f"DEBUG: Trying to join game: {game_code}")
    print(f"DEBUG: Active games: {list(games.keys())}")
    
    if game_code not in games:
        print(f"DEBUG: Game {game_code} not found!")
        emit('error', {'message': 'Game not found'})
        return
    
    game = games[game_code]
    
    # Check if this session is already in the game
    existing_player = None
    for pid, player in game['players'].items():
        if player['sid'] == request.sid:
            existing_player = pid
            break
    
    if existing_player:
        # Player is rejoining, update their session
        player_id = existing_player
        color = game['players'][player_id]['color']
        print(f"DEBUG: Player {player_id} rejoining as {color}")
    else:
        # New player joining
        if len(game['players']) >= 2:
            emit('error', {'message': 'Game is full'})
            return
        
        player_id = str(uuid.uuid4())
        color = 'black' if len(game['players']) == 1 else 'white'
        
        game['players'][player_id] = {
            'sid': request.sid,
            'color': color,
            'ready': False
        }
    
    print(f"DEBUG: Assigning player {player_id} color {color}")
    print(f"DEBUG: Game {game_code} currently has {len(game['players'])} players")
    
    players[request.sid] = {
        'game_code': game_code,
        'player_id': player_id,
        'color': color
    }
    
    # Update the player's session ID in the game
    game['players'][player_id]['sid'] = request.sid
    
    join_room(game_code)
    
    print(f"DEBUG: Player {player_id} joined game {game_code} as {color}")
    print(f"DEBUG: Game {game_code} now has {len(game['players'])} players")
    
    emit('game_joined', {
        'game_code': game_code,
        'player_color': color,
        'player_id': player_id
    })
    
    # Notify all players in the room about the new player
    socketio.emit('player_joined', {
        'players_count': len(game['players']),
        'can_start': len(game['players']) == 2
    }, room=game_code)
    
    # Send current game state to the joining player
    if len(game['players']) == 2:
        # Both players are now connected, send full game state
        socketio.emit('both_players_connected', {
            'players_count': len(game['players']),
            'can_start': True
        }, room=game_code)

@socketio.on('player_ready')
def handle_player_ready(data):
    if request.sid not in players:
        return
    
    player_info = players[request.sid]
    game_code = player_info['game_code']
    player_id = player_info['player_id']
    
    if game_code not in games:
        return
    
    game = games[game_code]
    game['players'][player_id]['ready'] = True
    
    # Check if both players are ready
    all_ready = all(player['ready'] for player in game['players'].values())
    
    if all_ready and len(game['players']) == 2:
        game['game_started'] = True
        
        # Send initial game state
        board_state = game['board'].get_board_state()
        socketio.emit('game_started', {
            'board_state': board_state,
            'current_player': game['current_player']
        }, room=game_code)

@socketio.on('make_move')
def handle_make_move(data):
    if request.sid not in players:
        return
    
    player_info = players[request.sid]
    game_code = player_info['game_code']
    player_color = player_info['color']
    
    if game_code not in games:
        return
    
    game = games[game_code]
    
    # Check if it's the player's turn
    if game['current_player'] != player_color or game['game_over']:
        return
    
    from_pos = data['from']
    to_pos = data['to']
    
    # Make the move
    success = game['board'].make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    
    if success:
        # Switch players
        game['current_player'] = 'black' if game['current_player'] == 'white' else 'white'
        
        # Check for game over conditions
        if game['board'].is_checkmate(game['current_player']):
            game['game_over'] = True
            game['winner'] = player_color
        elif game['board'].is_stalemate(game['current_player']):
            game['game_over'] = True
            game['winner'] = None
        
        # Send updated game state
        board_state = game['board'].get_board_state()
        socketio.emit('move_made', {
            'board_state': board_state,
            'current_player': game['current_player'],
            'game_over': game['game_over'],
            'winner': game['winner']
        }, room=game_code)
    else:
        emit('invalid_move', {'message': 'Invalid move'})

@socketio.on('get_valid_moves')
def handle_get_valid_moves(data):
    if request.sid not in players:
        return
    
    player_info = players[request.sid]
    game_code = player_info['game_code']
    
    if game_code not in games:
        return
    
    game = games[game_code]
    pos = data['position']
    
    valid_moves = game['board'].get_valid_moves(pos[0], pos[1])
    
    emit('valid_moves', {
        'position': pos,
        'moves': valid_moves
    })

@socketio.on('reset_game')
def handle_reset_game():
    if request.sid not in players:
        return
    
    player_info = players[request.sid]
    game_code = player_info['game_code']
    
    if game_code not in games:
        return
    
    game = games[game_code]
    game['board'] = OnlineChessBoard()
    game['current_player'] = 'white'
    game['game_over'] = False
    game['winner'] = None
    
    # Reset player ready status
    for player in game['players'].values():
        player['ready'] = False
    
    board_state = game['board'].get_board_state()
    socketio.emit('game_reset', {
        'board_state': board_state,
        'current_player': game['current_player']
    }, room=game_code)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"DEBUG: Player disconnected with sid: {request.sid}")
    if request.sid in players:
        player_info = players[request.sid]
        game_code = player_info['game_code']
        player_id = player_info['player_id']
        
        print(f"DEBUG: Player {player_id} disconnected from game {game_code}")
        
        # Don't immediately remove the player or clean up the game
        # This allows for page navigation without destroying the game
        # Only clean up after a longer timeout or explicit leave
        
        # Notify remaining players about potential disconnection
        if game_code in games:
            socketio.emit('player_disconnected', {
                'players_count': len(games[game_code]['players'])
            }, room=game_code)
        
        # Remove from players dict but keep game intact
        del players[request.sid]
        leave_room(game_code)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
