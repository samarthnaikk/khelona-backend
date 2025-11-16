#!/usr/bin/env python3
"""
Test script for Redis connection
Run this locally to test Redis setup: python test_redis.py
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    import redis.asyncio as redis
    
    # Check if we have individual Redis config or full URL
    redis_url = os.getenv('REDIS_URL')
    
    if redis_url:
        # Use full Redis URL
        redis_client = redis.from_url(redis_url, decode_responses=True)
        print(f"Redis client configured with URL: {redis_url}")
    else:
        # Use individual config parameters
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
        print(f"Redis client configured with host: {redis_host}:{redis_port}")
    
    REDIS_AVAILABLE = True
except ImportError:
    redis_client = None
    REDIS_AVAILABLE = False
    print("redis not installed")
except Exception as e:
    redis_client = None
    REDIS_AVAILABLE = False
    print(f"Redis configuration error: {e}")

async def test_redis():
    if not REDIS_AVAILABLE:
        print("✗ Redis is not available or not installed")
        print("To install Redis: pip install redis")
        print("To run Redis locally: docker run -p 6379:6379 redis")
        print("Or set REDIS_URL environment variable for remote Redis")
        return False
        
    try:
        # Test basic set/get
        test_key = "test:game"
        test_data = {"type": "tic-tac-toe", "state": {"players": []}}
        
        print("Testing Redis connection...")
        
        # Test connection
        await redis_client.ping()
        print("✓ Redis connection successful")
        
        # Set data
        await redis_client.set(test_key, json.dumps(test_data))
        print(f"✓ Set data to key: {test_key}")
        
        # Get data
        retrieved = await redis_client.get(test_key)
        if retrieved:
            parsed_data = json.loads(retrieved)
            print(f"✓ Retrieved data: {parsed_data}")
        else:
            print("✗ Failed to retrieve data")
            return False
        
        # Clean up
        await redis_client.delete(test_key)
        print(f"✓ Cleaned up test key: {test_key}")
        
        print("✓ Redis test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Redis test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_redis())