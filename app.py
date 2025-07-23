from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import random
import string
from online_chess_board import OnlineChessBoard  # Your provided file
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

games = {}
players = {}


def generate_game_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game/<game_code>')
def game(game_code):
    game_code = game_code.upper()
    print(f"DEBUG: Accessing game page for code: {game_code}")
    print(f"DEBUG: Active games: {list(games.keys())}")
    
    if game_code not in games:
        print(f"DEBUG: Game {game_code} not found, redirecting to home")
        return redirect(url_for('index'))
    
    return render_template('game.html', game_code=game_code)


@socketio.on('create_game')
def handle_create_game(data=None):
    timer = 300  # default 5 min
    if data and 'timer' in data:
        try:
            timer = int(data['timer'])
        except Exception:
            timer = 300
    game_code = generate_game_code()
    while game_code in games:
        game_code = generate_game_code()
    
    games[game_code] = {
        'board': OnlineChessBoard(),
        'players': {},
        'current_player': 'white',
        'game_started': False,
        'game_over': False,
        'winner': None,
        'last_activity': time.time(),
        'timer': timer,
        'remaining_time': {
            'white': timer,
            'black': timer
        },
        'last_move_time': None
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
        'ready': False,
        'last_seen': time.time()
    }
    
    join_room(game_code)
    
    print(f"DEBUG: Game created with code: {game_code}, timer: {timer}")
    
    emit('game_created', {
        'game_code': game_code,
        'player_color': 'white',
        'player_id': player_id
    })


@socketio.on('join_game')
def handle_join_game(data):
    game_code = data['game_code'].upper()
    
    if game_code not in games:
        emit('error', {'message': 'Game not found'})
        return
    
    game = games[game_code]
    
    player_id = data.get('player_id')
    if player_id and player_id in game['players']:
        color = game['players'][player_id]['color']
        game['players'][player_id]['sid'] = request.sid
        game['players'][player_id]['last_seen'] = time.time()
        players[request.sid] = {
            'game_code': game_code,
            'player_id': player_id,
            'color': color
        }
        print(f"DEBUG: Player {player_id} rejoined as {color}")
    else:
        if len(game['players']) >= 2:
            emit('error', {'message': 'Game is full'})
            return
        
        player_id = str(uuid.uuid4())
        color = 'black' if len(game['players']) == 1 else 'white'
        
        game['players'][player_id] = {
            'sid': request.sid,
            'color': color,
            'ready': False,
            'last_seen': time.time()
        }
        players[request.sid] = {
            'game_code': game_code,
            'player_id': player_id,
            'color': color
        }
        print(f"DEBUG: New player {player_id} joined as {color}")
    
    join_room(game_code)
    game['last_activity'] = time.time()
    
    emit('game_joined', {
        'game_code': game_code,
        'player_color': color,
        'player_id': player_id
    })
    
    socketio.emit('player_joined', {
        'players_count': len(game['players']),
        'can_start': len(game['players']) == 2
    }, room=game_code)
    
    if len(game['players']) == 2:
        socketio.emit('both_players_connected', {
            'players_count': len(game['players']),
            'can_start': True
        }, room=game_code)


@socketio.on('get_game_state')
def handle_get_game_state(data):
    game_code = data.get('game_code', '').upper()
    player_id = data.get('player_id')
    
    if not player_id:
        print(f"DEBUG: get_game_state failed - Player ID required")
        emit('error', {'message': 'Player ID required'})
        return
    
    if game_code not in games:
        print(f"DEBUG: get_game_state failed - Game {game_code} not found")
        emit('error', {'message': 'Game not found'})
        return
    
    game = games[game_code]
    
    if player_id not in game['players']:
        print(f"DEBUG: get_game_state failed - Not authorized for player {player_id} in {game_code}")
        emit('error', {'message': 'Not authorized for this game'})
        return
    
    color = game['players'][player_id]['color']
    game['players'][player_id]['sid'] = request.sid
    game['players'][player_id]['last_seen'] = time.time()
    players[request.sid] = {
        'game_code': game_code,
        'player_id': player_id,
        'color': color
    }
    
    join_room(game_code)
    
    player_status = {
        'white': 'You' if color == 'white' else 'Opponent' if 'white' in [p['color'] for p in game['players'].values()] else 'Waiting...',
        'black': 'You' if color == 'black' else 'Opponent' if 'black' in [p['color'] for p in game['players'].values()] else 'Waiting...'
    }
    
    board_state = game['board'].get_board_state()
    emit('game_state', {
        'board_state': board_state['board'],
        'white_king': board_state['white_king'],
        'black_king': board_state['black_king'],
        'white_in_check': board_state['white_in_check'],
        'black_in_check': board_state['black_in_check'],
        'player_color': color,
        'game_started': game['game_started'],
        'current_player': game['current_player'],
        'players': player_status,
        'timer': game['timer'],
        'remaining_time': game['remaining_time'],
        'captured': board_state['captured'],
        'material_diff': board_state['material_diff']
    })
    print(f"DEBUG: Sent game state to player {player_id} in {game_code}")


@socketio.on('player_ready')
def handle_player_ready(data):
    print(f"DEBUG: Received player_ready from sid: {request.sid}")
    if request.sid not in players:
        print(f"DEBUG: player_ready failed - SID not in players")
        return
    
    player_info = players[request.sid]
    game_code = player_info['game_code']
    player_id = player_info['player_id']
    
    if game_code not in games:
        print(f"DEBUG: player_ready failed - Game {game_code} not found")
        return
    
    game = games[game_code]
    if player_id in game['players']:
        game['players'][player_id]['ready'] = True
        print(f"DEBUG: Player {player_id} marked as ready in {game_code}")
    
    ready_status = {pid: p['ready'] for pid, p in game['players'].items()}
    print(f"DEBUG: Current ready statuses in {game_code}: {ready_status}")
    
    all_ready = all(p['ready'] for p in game['players'].values()) and len(game['players']) == 2
    if all_ready:
        game['game_started'] = True
        game['last_move_time'] = time.time()
        board_state = game['board'].get_board_state()
        socketio.emit('game_started', {
            'board_state': board_state['board'],
            'white_king': board_state['white_king'],
            'black_king': board_state['black_king'],
            'white_in_check': board_state['white_in_check'],
            'black_in_check': board_state['black_in_check'],
            'current_player': game['current_player'],
            'timer': game['timer'],
            'remaining_time': game['remaining_time'],
            'captured': board_state['captured'],
            'material_diff': board_state['material_diff']
        }, room=game_code)
        print(f"DEBUG: Game {game_code} started - both players ready")
    else:
        print(f"DEBUG: Not all ready yet in {game_code} - waiting for other player")
        socketio.emit('message', {'message': 'Waiting for other player to ready up', 'type': 'info'}, room=game_code)


@socketio.on('make_move')
def handle_make_move(data):
    print(f"DEBUG: Received make_move from sid: {request.sid} - data: {data}")
    if request.sid not in players:
        print("DEBUG: make_move failed - SID not in players")
        return
    
    player_info = players[request.sid]
    game_code = player_info['game_code']
    player_color = player_info['color']
    
    if game_code not in games:
        print(f"DEBUG: make_move failed - Game {game_code} not found")
        return
    
    game = games[game_code]
    if game['current_player'] != player_color or game['game_over']:
        print(f"DEBUG: Invalid move - not {player_color}'s turn or game over")
        emit('invalid_move', {'message': 'Not your turn or game over'})
        return
    
    from_pos = data['from']
    to_pos = data['to']
    # Timer logic
    now = time.time()
    if game['last_move_time']:
        elapsed = now - game['last_move_time']
        color = player_color
        game['remaining_time'][color] -= int(elapsed)
        if game['remaining_time'][color] <= 0:
            game['remaining_time'][color] = 0
            game['game_over'] = True
            game['winner'] = 'black' if color == 'white' else 'white'
            board_state = game['board'].get_board_state()
            socketio.emit('move_made', {
                'board_state': board_state['board'],
                'white_king': board_state['white_king'],
                'black_king': board_state['black_king'],
                'white_in_check': board_state['white_in_check'],
                'black_in_check': board_state['black_in_check'],
                'current_player': game['current_player'],
                'game_over': game['game_over'],
                'winner': game['winner'],
                'timer': game['timer'],
                'remaining_time': game['remaining_time'],
                'captured': board_state['captured'],
                'material_diff': board_state['material_diff']
            }, room=game_code)
            return
    game['last_move_time'] = now
    # Removed promotion from call - your class handles it internally
    print(f"DEBUG: Attempting move from {from_pos} to {to_pos} by {player_color}")
    success = game['board'].make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    
    if success:
        print(f"DEBUG: Move successful in {game_code}")
        game['current_player'] = 'black' if game['current_player'] == 'white' else 'white'
        
        if game['board'].is_checkmate(game['current_player']):
            game['game_over'] = True
            game['winner'] = player_color
            print(f"DEBUG: Checkmate - {player_color} wins in {game_code}")
        elif game['board'].is_stalemate(game['current_player']):
            game['game_over'] = True
            game['winner'] = None
            print(f"DEBUG: Stalemate in {game_code}")
        
        board_state = game['board'].get_board_state()
        socketio.emit('move_made', {
            'board_state': board_state['board'],
            'white_king': board_state['white_king'],
            'black_king': board_state['black_king'],
            'white_in_check': board_state['white_in_check'],
            'black_in_check': board_state['black_in_check'],
            'current_player': game['current_player'],
            'game_over': game['game_over'],
            'winner': game['winner'],
            'timer': game['timer'],
            'remaining_time': game['remaining_time'],
            'captured': board_state['captured'],
            'material_diff': board_state['material_diff']
        }, room=game_code)
        print(f"DEBUG: Broadcasted move_made to {game_code}")
    else:
        print(f"DEBUG: Move failed in {game_code} - invalid move (check validation or path blocked?)")
        emit('invalid_move', {'message': 'Invalid move'})


@socketio.on('get_valid_moves')
def handle_get_valid_moves(data):
    print(f"DEBUG: Received get_valid_moves from sid: {request.sid} - position: {data['position']}")
    if request.sid not in players:
        print("DEBUG: get_valid_moves failed - SID not in players")
        return
    
    player_info = players[request.sid]
    game_code = player_info['game_code']
    
    if game_code not in games:
        print(f"DEBUG: get_valid_moves failed - Game {game_code} not found")
        return
    
    game = games[game_code]
    pos = data['position']
    
    valid_moves = game['board'].get_valid_moves(pos[0], pos[1])
    print(f"DEBUG: Valid moves for {pos} in {game_code}: {valid_moves}")
    
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
    game['remaining_time'] = {'white': game['timer'], 'black': game['timer']}
    game['last_move_time'] = None
    
    for player in game['players'].values():
        player['ready'] = False
    
    board_state = game['board'].get_board_state()
    socketio.emit('game_reset', {
        'board_state': board_state['board'],
        'white_king': board_state['white_king'],
        'black_king': board_state['black_king'],
        'white_in_check': board_state['white_in_check'],
        'black_in_check': board_state['black_in_check'],
        'current_player': game['current_player'],
        'timer': game['timer'],
        'remaining_time': game['remaining_time'],
        'captured': board_state['captured'],
        'material_diff': board_state['material_diff']
    }, room=game_code)


@socketio.on('disconnect')
def handle_disconnect():
    print(f"DEBUG: Player disconnected with sid: {request.sid}")
    if request.sid in players:
        player_info = players[request.sid]
        game_code = player_info['game_code']
        player_id = player_info['player_id']
        
        if game_code in games:
            if player_id in games[game_code]['players']:
                games[game_code]['players'][player_id]['sid'] = None
                games[game_code]['players'][player_id]['last_seen'] = time.time()
            
            socketio.emit('player_disconnected', {
                'players_count': len([p for p in games[game_code]['players'].values() if p['sid'] is not None])
            }, room=game_code)
        
        del players[request.sid]
        leave_room(game_code)
        
        def cleanup_game():
            if game_code in games and all(p['sid'] is None for p in games[game_code]['players'].values()) and time.time() - games[game_code]['last_activity'] > 300:
                del games[game_code]
                print(f"DEBUG: Cleaned up inactive game {game_code}")
        
        socketio.start_background_task(cleanup_game)


# Add a background task to check timers every second and end the game if a timer reaches zero.
def timer_check_task():
    while True:
        time.sleep(1)
        for game_code, game in list(games.items()):
            if not game.get('game_started') or game.get('game_over'):
                continue
            now = time.time()
            if game['last_move_time']:
                turn = game['current_player']
                elapsed = int(now - game['last_move_time'])
                remaining = game['remaining_time'][turn] - elapsed
                if remaining <= 0:
                    game['remaining_time'][turn] = 0
                    game['game_over'] = True
                    game['winner'] = 'black' if turn == 'white' else 'white'
                    board_state = game['board'].get_board_state()
                    socketio.emit('move_made', {
                        'board_state': board_state['board'],
                        'white_king': board_state['white_king'],
                        'black_king': board_state['black_king'],
                        'white_in_check': board_state['white_in_check'],
                        'black_in_check': board_state['black_in_check'],
                        'current_player': game['current_player'],
                        'game_over': game['game_over'],
                        'winner': game['winner'],
                        'timer': game['timer'],
                        'remaining_time': game['remaining_time'],
                        'captured': board_state['captured'],
                        'material_diff': board_state['material_diff']
                    }, room=game_code)
                    game['last_move_time'] = None
                else:
                    game['remaining_time'][turn] = remaining

# Start the timer check task in the background
threading.Thread(target=timer_check_task, daemon=True).start()


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
