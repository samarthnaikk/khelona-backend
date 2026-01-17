# Khelona Backend - Technical Documentation

## Table of Contents
1. [Application Overview](#application-overview)
2. [Architecture](#architecture)
3. [Main Entry Point](#main-entry-point)
4. [Storage Layer](#storage-layer)
5. [API Endpoints](#api-endpoints)
6. [Game Modules](#game-modules)
7. [Helper Functions](#helper-functions)
8. [Data Structures](#data-structures)

---

## Application Overview

Khelona is a real-time multiplayer game backend built with Flask. The application serves as the backend API for a 2-player Tic Tac Toe web game where players can create games, join via game codes, and play in real-time.

### Technology Stack
- **Framework**: Flask 2.3.3
- **Storage**: Redis (with in-memory fallback)
- **Deployment**: Vercel-compatible (Python serverless functions)
- **CORS**: Flask-CORS for cross-origin requests

### Key Features
- Game creation with unique codes
- Player matching via game codes
- Real-time game state management
- Chat messaging system
- Persistent storage with Redis
- Automatic game expiration (30-minute TTL)
- Graceful fallback to in-memory storage for local development

---

## Architecture

### Application Structure
```
khelona-backend/
├── api/
│   ├── index.py              # Main application entry point
│   └── games/
│       ├── __init__.py       # Game registry and handlers
│       └── tic_tac_toe.py   # Tic Tac Toe game logic
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment configuration
└── test_redis.py            # Redis connection test script
```

### Request Flow
1. Client sends HTTP request to Flask endpoint
2. Flask route handler processes request
3. Game logic executed via game module
4. State stored/retrieved from Redis (or memory fallback)
5. Response returned to client with updated game state

### Storage Architecture
- **Primary**: Redis with 30-minute TTL on all game data
- **Fallback**: In-memory dictionary for local development
- **Keys**: Prefixed for namespacing (`game:`, `messages:`)

---

## Main Entry Point

### File: `api/index.py`

The main application file that initializes Flask, configures storage, and defines all HTTP endpoints.

#### Application Initialization

**Flask App Setup**
- Creates Flask application instance
- Configures CORS with allowed origins from environment variables
- Loads environment configuration via `python-dotenv`

**Storage Initialization**
- Attempts to connect to Redis using configuration from environment
- Falls back to in-memory storage if Redis unavailable
- Sets global flags (`REDIS_AVAILABLE`, `redis_client`)

**Configuration Sources**
- Environment variables via `.env` file
- Redis URL or individual Redis credentials (host, port, username, password)
- CORS origins (`ORIGIN_1`, `ORIGIN_2`)

#### Server Execution
When run directly (`if __name__ == '__main__'`):
- Starts Flask development server on `0.0.0.0:5001`
- Enables debug mode for local development
- For production, exports the Flask app for WSGI servers

---

## Storage Layer

### Redis Configuration

**Connection Methods**

1. **Full Redis URL** (preferred):
   ```python
   redis_url = os.getenv('REDIS_URL')
   redis_client = redis.from_url(redis_url, decode_responses=True)
   ```

2. **Individual Credentials**:
   ```python
   redis_host = os.getenv('REDIS_HOST', 'localhost')
   redis_port = int(os.getenv('REDIS_PORT', 6379))
   redis_username = os.getenv('REDIS_USERNAME')
   redis_password = os.getenv('REDIS_PASSWORD')
   ```

**Key Prefixes**
- `GAME_PREFIX = "game:"` - For game state data
- `MESSAGES_PREFIX = "messages:"` - For chat messages

**TTL Settings**
- `GAME_TTL = 30 * 60` (30 minutes) - Game data expiration
- `MESSAGES_TTL = 30 * 60` (30 minutes) - Message data expiration

### Storage Helper Functions

#### `get_game(code)`
**Purpose**: Retrieve game data from storage

**Parameters**:
- `code` (string): Unique game identifier

**Returns**:
- Game data dictionary if found
- `None` if game doesn't exist

**Behavior**:
- Attempts Redis lookup with key `game:{code}`
- Falls back to memory store if Redis unavailable
- Returns parsed JSON data from Redis
- Handles exceptions and returns `None` on error

---

#### `set_game(code, game_data)`
**Purpose**: Store or update game data

**Parameters**:
- `code` (string): Unique game identifier
- `game_data` (dict): Complete game state object

**Returns**:
- `True` on success
- `False` on failure

**Side Effects**:
- Stores data in Redis with 30-minute TTL
- Stores data in memory fallback if Redis unavailable
- Serializes dictionary to JSON for Redis storage

---

#### `get_messages(code)`
**Purpose**: Retrieve chat messages for a game

**Parameters**:
- `code` (string): Unique game identifier

**Returns**:
- List of message dictionaries
- Empty list `[]` if no messages exist

**Behavior**:
- Looks up messages with key `messages:{code}`
- Returns parsed JSON array from Redis
- Falls back to memory store

---

#### `add_message(code, message_data)`
**Purpose**: Append a message to a game's chat

**Parameters**:
- `code` (string): Unique game identifier
- `message_data` (dict): Message object with player, message, timestamp

**Returns**:
- `True` on success
- `False` on failure

**Side Effects**:
- Retrieves existing messages
- Appends new message to list
- Stores updated list with 30-minute TTL

---

#### `extend_game_ttl(code)`
**Purpose**: Reset TTL to 30 minutes on game activity

**Parameters**:
- `code` (string): Unique game identifier

**Returns**:
- `True` on success
- `False` on failure

**Side Effects**:
- Extends TTL for both game data and messages
- Only operates when Redis is available
- Called automatically on game state checks and moves

---

### Utility Functions

#### `generate_code(length=6)`
**Purpose**: Generate random alphanumeric game codes

**Parameters**:
- `length` (int, optional): Code length, default 6

**Returns**:
- String of uppercase letters and digits

**Behavior**:
- Uses `random.choices()` with uppercase ASCII and digits
- Example output: `"AB12CD"`, `"XYZ789"`

---

## API Endpoints

### Health Check & Testing

#### `GET /`
**Purpose**: Verify backend service is running

**Parameters**: None

**Returns**:
```json
{
  "message": "Backend is running with Redis!",
  "status": "success"
}
```

**Status Codes**:
- `200 OK`: Service is running

---

#### `GET /test`
**Purpose**: Comprehensive API and storage test

**Parameters**: None

**Returns**:
```json
{
  "message": "API is working with Flask and Redis!",
  "status": "success",
  "games_module": "working",
  "test_game_created": true,
  "redis_status": "working",
  "storage_type": "redis"
}
```

**Behavior**:
- Tests game module by creating test game
- Tests Redis connection with ping and basic operations
- Returns detailed status of all components
- Cleans up test data from Redis

**Status Codes**:
- `200 OK`: All tests passed or partial success

---

### Game Management

#### `POST /create_game`
**Purpose**: Create a new game and return unique game code

**Request Body**: None (or empty JSON)

**Returns**:
```json
{
  "code": "ABC123"
}
```

**Behavior**:
1. Generates random 6-character code
2. Checks for code collision and regenerates if needed
3. Creates new Tic Tac Toe game state
4. Stores game in Redis/memory with game type
5. Returns generated code to client

**Status Codes**:
- `200 OK`: Game created successfully
- `500 Internal Server Error`: Game creation or storage failed

**Side Effects**:
- Creates new entry in storage with key `game:{code}`
- Sets 30-minute TTL on game data

---

#### `POST /join_game`
**Purpose**: Add a player to an existing game

**Request Body**:
```json
{
  "code": "ABC123",
  "player": "PlayerName"
}
```

**Returns**:
```json
{
  "success": true,
  "player_index": 1,
  "players": ["Player1", "Player2"]
}
```

**Behavior**:
1. Validates game code exists
2. Checks game isn't full (max 2 players)
3. Adds player to game state
4. Returns player index (0 or 1) and updated player list
5. Extends game TTL

**Status Codes**:
- `200 OK`: Player joined successfully
- `400 Bad Request`: Invalid or full game code
- `500 Internal Server Error`: Failed to update game

**Side Effects**:
- Modifies game state in storage
- Extends game TTL to 30 minutes

---

#### `GET /game_state/<code>`
**Purpose**: Retrieve current state of a game

**Parameters**:
- `code` (path parameter): Game code

**Returns**:
```json
{
  "state": {
    "players": ["Player1", "Player2"],
    "board": ["X", "O", "", "", "", "", "", "", ""],
    "turn": 0,
    "winner": null,
    "game_over": false,
    "winning_line": []
  }
}
```

**Behavior**:
1. Looks up game by code
2. Returns full game state if found
3. Extends game TTL on access

**Status Codes**:
- `200 OK`: Game state returned
- `404 Not Found`: Game code doesn't exist

**Side Effects**:
- Extends game TTL to 30 minutes

---

#### `POST /make_move`
**Purpose**: Execute a player's move in the game

**Request Body**:
```json
{
  "code": "ABC123",
  "index": 4,
  "player": "PlayerName"
}
```

**Returns**:
```json
{
  "success": true,
  "state": {
    "players": ["Player1", "Player2"],
    "board": ["X", "O", "", "", "X", "", "", "", ""],
    "turn": 1,
    "winner": null,
    "game_over": false,
    "winning_line": []
  }
}
```

**Behavior**:
1. Validates game exists and player is in game
2. Verifies it's the player's turn
3. Checks game isn't over
4. Delegates move handling to game module
5. Updates game state in storage
6. Returns success and updated state
7. Extends game TTL

**Status Codes**:
- `200 OK`: Move executed successfully
- `400 Bad Request`: Invalid move, wrong turn, or invalid request
- `500 Internal Server Error`: Failed to update game

**Side Effects**:
- Modifies game board state
- Updates turn indicator
- May set game_over and winner
- Extends game TTL to 30 minutes

---

### Chat System

#### `POST /send_message`
**Purpose**: Send a chat message in a game

**Request Body**:
```json
{
  "code": "ABC123",
  "player": "PlayerName",
  "message": "Good game!"
}
```

**Returns**:
```json
{
  "success": true
}
```

**Behavior**:
1. Validates game and player
2. Creates message object with timestamp
3. Appends to game's message list
4. Extends game TTL

**Status Codes**:
- `200 OK`: Message sent successfully
- `400 Bad Request`: Invalid game or player
- `500 Internal Server Error`: Failed to save message

**Side Effects**:
- Adds message to storage under `messages:{code}`
- Extends game TTL to 30 minutes

---

#### `GET /get_messages/<code>`
**Purpose**: Retrieve all chat messages for a game

**Parameters**:
- `code` (path parameter): Game code

**Returns**:
```json
{
  "messages": [
    {
      "player": "Player1",
      "message": "Hello!",
      "timestamp": "14:30"
    },
    {
      "player": "Player2",
      "message": "Hi there!",
      "timestamp": "14:31"
    }
  ]
}
```

**Behavior**:
1. Validates game exists
2. Retrieves all messages for the game
3. Returns messages in chronological order

**Status Codes**:
- `200 OK`: Messages returned (may be empty array)
- `404 Not Found`: Game doesn't exist

---

## Game Modules

### File: `api/games/__init__.py`

#### Game Registry System

**`GAME_HANDLERS` Dictionary**
- Maps game type strings to handler functions
- Structure:
  ```python
  {
    'game-type': {
      'create': create_function,
      'handle_move': move_function
    }
  }
  ```
- Currently supports: `'tic-tac-toe'`

---

#### `create_game(game_type)`
**Purpose**: Factory function to create new game instances

**Parameters**:
- `game_type` (string): Type of game to create (e.g., 'tic-tac-toe')

**Returns**:
- New game state dictionary for the specified type
- `None` if game type not recognized

**Behavior**:
- Looks up game type in `GAME_HANDLERS`
- Calls the corresponding create function
- Returns initialized game state

---

#### `handle_game_move(game_type, game_state, player_index, move_data)`
**Purpose**: Route move handling to appropriate game logic

**Parameters**:
- `game_type` (string): Type of game
- `game_state` (dict): Current game state
- `player_index` (int): Player making the move (0 or 1)
- `move_data` (any): Move-specific data (e.g., board index)

**Returns**:
- Tuple: `(success: bool, updated_state: dict)`

**Behavior**:
- Looks up game type in handlers
- Delegates to game-specific move function
- Returns success status and modified state
- Returns `(False, game_state)` if game type unknown

---

### File: `api/games/tic_tac_toe.py`

#### `check_winner(board)`
**Purpose**: Determine if there's a winner or tie

**Parameters**:
- `board` (list): 9-element list representing the game board

**Returns**:
- Tuple: `(winner, winning_line)`
  - `winner`: `'X'`, `'O'`, `'tie'`, or `None`
  - `winning_line`: List of winning cell indices, or empty list

**Behavior**:
1. Checks all rows (3 lines)
2. Checks all columns (3 lines)
3. Checks both diagonals (2 lines)
4. Returns winner and winning line if found
5. Checks for tie (all cells filled)
6. Returns `(None, [])` if game continues

**Winning Line Patterns**:
- Rows: `[0,1,2]`, `[3,4,5]`, `[6,7,8]`
- Columns: `[0,3,6]`, `[1,4,7]`, `[2,5,8]`
- Diagonals: `[0,4,8]`, `[2,4,6]`

---

#### `create_tic_tac_toe_game()`
**Purpose**: Initialize a new Tic Tac Toe game state

**Parameters**: None

**Returns**:
```python
{
  'players': [],           # List of player names
  'board': ['']*9,         # 9 empty strings
  'turn': 0,               # Current turn (0 or 1)
  'winner': None,          # Winner identifier or None
  'game_over': False,      # Game completion flag
  'winning_line': []       # Winning cell indices
}
```

**Behavior**:
- Creates empty game state
- Board is represented as list of 9 elements
- Turn alternates between 0 and 1

---

#### `handle_tic_tac_toe_move(game, player_index, move_index)`
**Purpose**: Process a player's move in Tic Tac Toe

**Parameters**:
- `game` (dict): Current game state
- `player_index` (int): Player making move (0 for 'X', 1 for 'O')
- `move_index` (int): Board position (0-8)

**Returns**:
- Tuple: `(success: bool, updated_game: dict)`

**Behavior**:
1. Validates move (game not over, cell empty)
2. Places 'X' (player 0) or 'O' (player 1) at move_index
3. Checks for winner using `check_winner()`
4. If winner found:
   - Sets `game_over = True`
   - Sets `winner` and `winning_line`
5. If no winner:
   - Switches turn to other player
6. Returns `(True, updated_game)` on success
7. Returns `(False, game)` on invalid move

**Side Effects**:
- Modifies game dictionary in-place
- Updates board, turn, game_over, winner, winning_line

---

## Helper Functions

### General Utilities

#### `generate_code(length=6)`
See [Utility Functions](#utility-functions) section above.

---

## Data Structures

### Game Data Structure (Storage)
```python
{
  'type': 'tic-tac-toe',  # Game type identifier
  'state': {              # Game-specific state
    # ... varies by game type
  }
}
```

### Tic Tac Toe Game State
```python
{
  'players': ['Player1', 'Player2'],  # Player names (0-2 players)
  'board': ['X', 'O', '', '', 'X', '', '', '', ''],  # 9 cells
  'turn': 0,                          # Current turn (0 or 1)
  'winner': None,                     # 'X', 'O', 'tie', or None
  'game_over': False,                 # Boolean
  'winning_line': [0, 1, 2]          # Winning cell indices or []
}
```

### Message Structure
```python
{
  'player': 'PlayerName',      # Player who sent message
  'message': 'Message text',   # Message content
  'timestamp': '14:30'         # Time in HH:MM format
}
```

### Storage Keys
- **Game Data**: `game:{code}` → JSON string of game data
- **Messages**: `messages:{code}` → JSON array of messages

---

## Environment Variables

### Required for Production
- `REDIS_URL` - Full Redis connection URL (preferred method)
  - Format: `redis://username:password@host:port/db`

**OR**

- `REDIS_HOST` - Redis server hostname
- `REDIS_PORT` - Redis server port (default: 6379)
- `REDIS_USERNAME` - Redis username (optional)
- `REDIS_PASSWORD` - Redis password (optional)

### CORS Configuration
- `ORIGIN_1` - First allowed origin for CORS
- `ORIGIN_2` - Second allowed origin for CORS

### Optional
- `PORT` - Server port for local development (default: 5001)

---

## Error Handling

### General Approach
- All endpoints wrapped in try-except blocks
- Errors logged to console with `print()`
- HTTP error responses include error messages
- Storage operations return boolean success indicators

### Fallback Behavior
- Redis unavailable → automatic fallback to in-memory storage
- Invalid game codes → 404 or 400 responses
- Invalid moves → 400 Bad Request responses
- Storage failures → 500 Internal Server Error responses

### Automatic Cleanup
- Games expire after 30 minutes of inactivity
- TTL automatically extended on any game activity
- Redis handles cleanup automatically
- Memory fallback has no automatic cleanup (process lifetime)

---

## Deployment

### Vercel Configuration
File: `vercel.json`

```json
{
  "version": 2,
  "builds": [{
    "src": "api/index.py",
    "use": "@vercel/python"
  }],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/index.py" },
    { "src": "/(.*)", "dest": "/api/index.py" }
  ]
}
```

- All routes handled by `api/index.py`
- Uses Vercel's Python runtime
- Serverless function deployment model

### Production Requirements
- Python 3.7+
- Redis instance (cloud or managed)
- Environment variables configured
- CORS origins set appropriately

---

## Testing

### Manual Testing
1. Run `python test_redis.py` to verify Redis connection
2. Use `GET /test` endpoint for comprehensive health check
3. Test full game flow:
   - Create game via `POST /create_game`
   - Join game via `POST /join_game`
   - Make moves via `POST /make_move`
   - Check state via `GET /game_state/<code>`

### Local Development
```bash
# Start server
python api/index.py

# Server runs on http://0.0.0.0:5001
# Will use memory fallback if Redis not available
```

---

## Extension Points

### Adding New Games
1. Create game logic file in `api/games/`
2. Implement `create_<game>_game()` function
3. Implement `handle_<game>_move()` function
4. Register in `GAME_HANDLERS` dictionary in `api/games/__init__.py`
5. No changes needed to main application code

### Example Structure for New Game
```python
# api/games/my_game.py
def create_my_game_game():
    return {
        'players': [],
        'custom_state': {},
        'turn': 0,
        'game_over': False
    }

def handle_my_game_move(game, player_index, move_data):
    # Implement game logic
    return True, updated_game

# api/games/__init__.py
from .my_game import create_my_game_game, handle_my_game_move

GAME_HANDLERS = {
    'tic-tac-toe': {...},
    'my-game': {
        'create': create_my_game_game,
        'handle_move': handle_my_game_move
    }
}
```
