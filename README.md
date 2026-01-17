# Khelona Backend

A real-time multiplayer game backend API for 2-player Tic Tac Toe. Players can create games, join using unique codes, and play in real-time with chat support.

**Play the game**: [https://khelona.samarthnaikk.me](https://khelona.samarthnaikk.me)

## Overview

Khelona backend is a Flask-based REST API that provides:
- **Game Management**: Create and join games with unique codes
- **Real-time Gameplay**: Turn-based game state synchronization
- **Chat System**: In-game messaging between players
- **Persistent Storage**: Redis-backed storage with automatic fallback
- **Auto-expiration**: Games automatically expire after 30 minutes of inactivity

### Technology Stack
- **Framework**: Flask 2.3.3 with Flask-CORS
- **Storage**: Redis (with in-memory fallback for local development)
- **Deployment**: Vercel-compatible serverless functions
- **Language**: Python 3.7+

## Quick Start

### Prerequisites
- Python 3.7 or higher
- Redis (optional for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/samarthnaikk/khelona-backend.git
   cd khelona-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional for local dev)
   
   Create a `.env` file in the project root:
   ```env
   # For local development without Redis, you can skip this
   # The app will automatically use in-memory storage
   
   # Option 1: Redis URL (recommended)
   REDIS_URL=redis://username:password@host:port/db
   
   # Option 2: Individual Redis settings
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_USERNAME=default
   REDIS_PASSWORD=your-password
   
   # CORS configuration
   ORIGIN_1=http://localhost:3000
   ORIGIN_2=https://yourdomain.com
   ```

5. **Run the application**
   ```bash
   python api/index.py
   ```
   
   The server will start on `http://0.0.0.0:5001`

## Configuration

### Redis Setup

#### Local Development (Optional)
The application automatically falls back to in-memory storage if Redis is not available, making it easy to run locally without Redis.

To use Redis locally:
```bash
# Using Docker (recommended)
docker run -d -p 6379:6379 --name redis redis:alpine

# OR install Redis locally
# macOS: brew install redis && brew services start redis
# Ubuntu: sudo apt install redis-server
```

#### Production (Required)
For production deployment, Redis is recommended for persistent storage. Options include:
- [Redis Cloud](https://redis.com/try-free/) - Free tier available
- [Railway](https://railway.app) - Supports Redis addon
- [Render](https://render.com) - Redis addon available
- AWS ElastiCache, Google Cloud Memorystore, or Azure Cache for Redis

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REDIS_URL` | Complete Redis connection URL | Production |
| `REDIS_HOST` | Redis server hostname | Production (alt) |
| `REDIS_PORT` | Redis server port (default: 6379) | Production (alt) |
| `REDIS_USERNAME` | Redis username | Optional |
| `REDIS_PASSWORD` | Redis password | Production |
| `ORIGIN_1` | First allowed CORS origin | Production |
| `ORIGIN_2` | Second allowed CORS origin | Production |

## Usage

### Health Check
```bash
curl http://localhost:5001/
```

### Create a Game
```bash
curl -X POST http://localhost:5001/create_game
# Returns: {"code": "ABC123"}
```

### Join a Game
```bash
curl -X POST http://localhost:5001/join_game \
  -H "Content-Type: application/json" \
  -d '{"code": "ABC123", "player": "PlayerName"}'
```

### Get Game State
```bash
curl http://localhost:5001/game_state/ABC123
```

### Make a Move
```bash
curl -X POST http://localhost:5001/make_move \
  -H "Content-Type: application/json" \
  -d '{"code": "ABC123", "player": "PlayerName", "index": 4}'
```

For complete API documentation, see [documentation.md](documentation.md).

## Project Structure

```
khelona-backend/
├── api/
│   ├── index.py              # Main Flask application and API endpoints
│   └── games/
│       ├── __init__.py       # Game registry and handler routing
│       └── tic_tac_toe.py    # Tic Tac Toe game logic
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment configuration
├── test_redis.py            # Redis connection test utility
├── documentation.md         # Complete technical documentation
└── README.md               # This file
```

## API Endpoints

### Game Management
- `POST /create_game` - Create a new game, returns unique code
- `POST /join_game` - Join an existing game with code
- `GET /game_state/<code>` - Get current state of a game
- `POST /make_move` - Make a move in the game

### Chat
- `POST /send_message` - Send a chat message in a game
- `GET /get_messages/<code>` - Retrieve all messages for a game

### Utility
- `GET /` - Health check endpoint
- `GET /test` - Comprehensive API and Redis connection test

For detailed endpoint documentation including request/response formats and behaviors, see [documentation.md](documentation.md).

## Development

### Running Tests
Test Redis connection:
```bash
python test_redis.py
```

Test API health:
```bash
curl http://localhost:5001/test
```

### Local Development Mode
The application automatically detects when Redis is unavailable and uses in-memory storage, making local development easy without external dependencies.

## Deployment

### Vercel (Recommended)
The application is configured for Vercel serverless deployment:

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel`
3. Configure environment variables in Vercel dashboard
4. Set up Redis instance (Redis Cloud, Railway, etc.)

### Other Platforms
The application can be deployed to any platform supporting Python WSGI applications:
- **Railway**: Supports Python + Redis addon
- **Render**: Web service + Redis addon
- **Heroku**: With Redis addon
- **AWS/GCP/Azure**: With managed Redis service

Ensure environment variables are configured and a Redis instance is available.

## Game Features

### Tic Tac Toe
- 2-player turn-based gameplay
- Real-time move synchronization
- Automatic win detection (rows, columns, diagonals)
- Tie game detection
- Winning line highlighting

### Chat System
- In-game messaging between players
- Message timestamps
- Persistent chat history per game

### Automatic Cleanup
- Games expire after 30 minutes of inactivity
- TTL automatically refreshed on game activity
- No manual cleanup required

## Technical Documentation

For comprehensive technical details including:
- Complete architecture overview
- Detailed function documentation
- Data structures and storage schemas
- Error handling and fallback behavior
- Extension points for adding new games

See [documentation.md](documentation.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See [LICENSE](LICENSE) for details.
