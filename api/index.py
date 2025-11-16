from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import json
import datetime
import os
from dotenv import load_dotenv
import asyncio

try:
    from .games import create_game, handle_game_move
except ImportError:
    from games import create_game, handle_game_move

load_dotenv()

# Try to import Redis, fallback to in-memory storage for local dev
try:
    import redis
    
    redis_url = os.getenv('REDIS_URL')
    
    if redis_url:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        print("✓ Redis available")
    else:
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_username = os.getenv('REDIS_USERNAME')
        redis_password = os.getenv('REDIS_PASSWORD')
        
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            username=redis_username,
            password=redis_password,
            decode_responses=True
        )
        print("✓ Redis available")
    
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis_client = None
    print("✗ Redis not available, using in-memory storage")
except Exception as e:
    REDIS_AVAILABLE = False
    redis_client = None
    print(f"✗ Redis configuration error: {e}, using in-memory storage")

# Fallback in-memory storage for local development
_memory_store = {}

# Redis key prefixes
GAME_PREFIX = "game:"
MESSAGES_PREFIX = "messages:"

# TTL settings (in seconds)
GAME_TTL = 30 * 60  # 30 minutes
MESSAGES_TTL = 30 * 60  # 30 minutes

app = Flask(__name__)

# Configure CORS for backend API
CORS(app, 
     origins = [str(os.getenv('ORIGIN_1')),str(os.getenv('ORIGIN_2'))],  # Allow all origins for now, restrict in production
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Helper functions for Redis operations with fallback
def get_game(code):
    """Get game data from Redis or memory fallback"""
    try:
        if REDIS_AVAILABLE:
            game_data = redis_client.get(f"{GAME_PREFIX}{code}")
            return json.loads(game_data) if game_data else None
        else:
            # Use memory fallback
            return _memory_store.get(f"{GAME_PREFIX}{code}")
    except Exception as e:
        print(f"Error getting game {code}: {e}")
        return None

def set_game(code, game_data):
    """Set game data in Redis or memory fallback with 30 min TTL"""
    try:
        if REDIS_AVAILABLE:
            redis_client.setex(f"{GAME_PREFIX}{code}", GAME_TTL, json.dumps(game_data))
        else:
            # Use memory fallback (no TTL for memory)
            _memory_store[f"{GAME_PREFIX}{code}"] = game_data
        return True
    except Exception as e:
        print(f"Error setting game {code}: {e}")
        return False

def get_messages(code):
    """Get messages for a game from Redis or memory fallback"""
    try:
        if REDIS_AVAILABLE:
            messages_data = redis_client.get(f"{MESSAGES_PREFIX}{code}")
            return json.loads(messages_data) if messages_data else []
        else:
            # Use memory fallback
            return _memory_store.get(f"{MESSAGES_PREFIX}{code}", [])
    except Exception as e:
        print(f"Error getting messages for {code}: {e}")
        return []

def add_message(code, message_data):
    """Add a message to a game in Redis or memory fallback with 30 min TTL"""
    try:
        messages = get_messages(code)
        messages.append(message_data)
        if REDIS_AVAILABLE:
            redis_client.setex(f"{MESSAGES_PREFIX}{code}", MESSAGES_TTL, json.dumps(messages))
        else:
            # Use memory fallback (no TTL for memory)
            _memory_store[f"{MESSAGES_PREFIX}{code}"] = messages
        return True
    except Exception as e:
        print(f"Error adding message to {code}: {e}")
        return False

def extend_game_ttl(code):
    """Extend TTL for a game when there's activity (resets to 30 minutes)"""
    try:
        if REDIS_AVAILABLE:
            # Extend TTL for both game and messages
            redis_client.expire(f"{GAME_PREFIX}{code}", GAME_TTL)
            redis_client.expire(f"{MESSAGES_PREFIX}{code}", MESSAGES_TTL)
        return True
    except Exception as e:
        print(f"Error extending TTL for game {code}: {e}")
        return False

# Test route
@app.route('/', methods=['GET'])
def home():
    try:
        return jsonify({
            'message': 'Backend is running with Redis!',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'message': 'Backend reachable but error occurred',
            'status': 'error',
            'error': str(e)
        })

@app.route('/test', methods=['GET'])
def test():
    try:
        # Test if games module is working
        test_game = create_game('tic-tac-toe')
        
        # Test Redis connection
        redis_status = "not_available"
        if REDIS_AVAILABLE:
            try:
                # Try a simple Redis operation
                redis_client.ping()
                set_game("TEST", {"test": True})
                retrieved = get_game("TEST")
                if retrieved and retrieved.get("test"):
                    redis_status = "working"
                    # Clean up test data
                    redis_client.delete(f"{GAME_PREFIX}TEST")
                else:
                    redis_status = "connection_failed"
            except Exception as redis_error:
                redis_status = f"error: {str(redis_error)}"
        
        return jsonify({
            'message': 'API is working with Flask and Redis!', 
            'status': 'success',
            'games_module': 'working',
            'test_game_created': bool(test_game),
            'redis_status': redis_status,
            'storage_type': 'redis' if REDIS_AVAILABLE else 'memory-fallback'
        })
    except Exception as e:
        return jsonify({
            'message': 'API working but has issues',
            'status': 'partial',
            'error': str(e),
            'redis_status': 'error',
            'storage_type': 'memory-fallback'
        })

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/create_game', methods=['POST'])
def create_game_endpoint():
    try:
        print("Creating game...")
        code = generate_code()
        
        # Check if code already exists in Redis
        existing_game = get_game(code)
        while existing_game is not None:
            code = generate_code()
            existing_game = get_game(code)
        
        print(f"Generated code: {code}")
        # Default to tic-tac-toe for now, can be extended to accept game type
        try:
            game_state = create_game('tic-tac-toe')
            print(f"Game state created: {game_state}")
        except Exception as game_error:
            print(f"Error creating game state: {game_error}")
            return jsonify({'error': f'Game creation failed: {str(game_error)}'}), 500
            
        game_data = {'type': 'tic-tac-toe', 'state': game_state}
        success = set_game(code, game_data)
        
        if not success:
            return jsonify({'error': 'Failed to save game to storage'}), 500
        
        print(f"Created game with code: {code}")
        return jsonify({'code': code})
    except Exception as e:
        print(f"Error creating game: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# HTTP-based endpoints for Vercel compatibility with KV storage
@app.route('/join_game', methods=['POST'])
def join_game_http():
    try:
        data = request.get_json()
        code = data.get('code')
        player = data.get('player')
        
        game_data = get_game(code)
        if not game_data or len(game_data['state']['players']) >= 2:
            return jsonify({'error': 'Invalid or full game code'}), 400
        
        game_data['state']['players'].append(player)
        player_index = len(game_data['state']['players']) - 1
        
        success = set_game(code, game_data)
        if not success:
            return jsonify({'error': 'Failed to update game'}), 500
        
        # Extend TTL since there's activity
        extend_game_ttl(code)
        
        return jsonify({
            'success': True,
            'player_index': player_index,
            'players': game_data['state']['players']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/game_state/<code>', methods=['GET'])
def get_game_state_endpoint(code):
    game_data = get_game(code)
    if game_data:
        # Extend TTL since there's activity (checking game state)
        extend_game_ttl(code)
        return jsonify({'state': game_data['state']})
    return jsonify({'error': 'Game not found'}), 404

@app.route('/make_move', methods=['POST'])
def make_move_http():
    try:
        data = request.get_json()
        code = data.get('code')
        idx = data.get('index')
        player = data.get('player')
        
        game_data = get_game(code)
        if not game_data or idx is None or player not in game_data['state']['players']:
            return jsonify({'error': 'Invalid request'}), 400
        
        game_state = game_data['state']
        game_type = game_data['type']
        
        try:
            player_index = game_state['players'].index(player)
        except ValueError:
            return jsonify({'error': 'Player not found'}), 400
        
        if game_state['turn'] != player_index or game_state['game_over']:
            return jsonify({'error': 'Not your turn'}), 400
        
        success, updated_state = handle_game_move(game_type, game_state, player_index, idx)
        
        if success:
            game_data['state'] = updated_state
            success = set_game(code, game_data)
            if not success:
                return jsonify({'error': 'Failed to update game'}), 500
            
            # Extend TTL since there's activity
            extend_game_ttl(code)
            
            return jsonify({'success': True, 'state': updated_state})
        else:
            return jsonify({'error': 'Invalid move'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message_http():
    try:
        data = request.get_json()
        code = data.get('code')
        player = data.get('player')
        message = data.get('message')
        
        game_data = get_game(code)
        if not game_data or player not in game_data['state']['players']:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Add the message with timestamp
        message_data = {
            'player': player,
            'message': message,
            'timestamp': datetime.datetime.now().strftime('%H:%M')
        }
        
        success = add_message(code, message_data)
        if not success:
            return jsonify({'error': 'Failed to save message'}), 500
        
        # Extend TTL since there's activity
        extend_game_ttl(code)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_messages/<code>', methods=['GET'])
def get_messages_endpoint(code):
    game_data = get_game(code)
    if game_data:
        messages = get_messages(code)
        return jsonify({'messages': messages})
    return jsonify({'error': 'Game not found'}), 404

# For deployment - export the Quart app
# ASGI servers will handle the interface automatically
app = app

if __name__ == '__main__':
    # Local development
    app.run(host='0.0.0.0', port=5001, debug=True)
