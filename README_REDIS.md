# Bkhelo Backend with Redis

This backend has been rewritten to use **Quart** (async Flask) and **Redis** for persistent storage.

## Features

- **Persistent Storage**: Game states and chat messages are stored in Redis
- **Async Support**: Built with Quart for better performance
- **Fallback**: Falls back to in-memory storage for local development
- **Real-time**: HTTP polling for game updates and chat

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Redis

#### Local Development
```bash
# Using Docker (recommended)
docker run -d -p 6379:6379 --name redis redis:alpine

# Or install Redis locally
# macOS: brew install redis && brew services start redis
# Ubuntu: sudo apt install redis-server
```

#### Production (Cloud Redis)
- **Redis Cloud**: https://redis.com/try-free/
- **AWS ElastiCache**: Redis service on AWS
- **Railway**: https://railway.app (supports Redis)
- **Render**: https://render.com (Redis addon)

### 3. Environment Variables

Create a `.env` file in the project root with your Redis configuration:

**Option 1: Individual Redis settings**
```env
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=your-password
```

**Option 2: Full Redis URL**
```env
REDIS_URL=redis://username:password@host:port/db
```

**For local development (no auth)**
```env
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 4. Local Development

```bash
# Run locally (will use memory fallback if Redis not available)
python api/index.py
```

### 5. Deploy

The app can be deployed to any platform that supports Python and Redis:
- **Railway**: Supports both Python apps and Redis
- **Render**: Web service + Redis addon
- **Heroku**: With Redis addon
- **AWS/GCP/Azure**: With managed Redis service

## API Endpoints

### Game Management
- `POST /create_game` - Create a new game
- `POST /join_game` - Join an existing game
- `GET /game_state/<code>` - Get current game state
- `POST /make_move` - Make a move in the game

### Chat
- `POST /send_message` - Send a chat message
- `GET /get_messages/<code>` - Get chat messages for a game

### Utility
- `GET /` - Health check
- `GET /test` - Test API and Redis connection

## Storage Structure

### Games
- Key: `game:<code>`
- Value: `{"type": "tic-tac-toe", "state": {...}}`

### Messages
- Key: `messages:<code>` 
- Value: `[{"player": "...", "message": "...", "timestamp": "..."}]`

## Migration from Flask

The API has been migrated from Flask to Quart with the following changes:

1. **Async/Await**: All route handlers are now async
2. **Persistent Storage**: Game state persists across server restarts
3. **Better Error Handling**: Graceful fallback to memory storage
4. **Performance**: Async operations for better scalability

## Testing Redis Connection

Run the test script to verify Redis setup:

```bash
python test_redis.py
```

This will test basic Redis operations and report if everything is working correctly.