# Redis Cache

This directory contains a Docker Compose configuration for running Redis 7 with persistence and production-ready settings.

## Quick Start

### Start Redis

```bash
docker-compose up -d
```

### Stop Redis

```bash
docker-compose down
```

### Stop and Remove Data

```bash
docker-compose down -v
```

## Configuration

### Default Settings

- **Port**: `6379`
- **Password**: `redis_password` (change this in production!)
- **Max Memory**: `256mb`
- **Eviction Policy**: `allkeys-lru` (Least Recently Used)
- **Persistence**: AOF (Append Only File) with `everysec` fsync

### Environment Variables

Override the default password:

```bash
export REDIS_PASSWORD=your_secure_password
docker-compose up -d
```

Or create a `.env` file:

```env
REDIS_PASSWORD=your_secure_password
```

## Features

### Persistence

Redis is configured with AOF (Append Only File) persistence:
- `appendonly yes`: Enable AOF
- `appendfsync everysec`: Sync to disk every second (balance between performance and durability)

### Memory Management

- **Max Memory**: 256MB (adjust based on your needs)
- **Eviction Policy**: `allkeys-lru` - Removes least recently used keys when memory limit is reached

### Health Check

The service includes a health check that runs every 10 seconds.

## Usage

### Connect with redis-cli

```bash
# Connect to Redis
docker exec -it redis_cache redis-cli -a redis_password

# Test connection
docker exec -it redis_cache redis-cli -a redis_password PING
```

### Python Client Example

```python
import redis

# Connect to Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    password='redis_password',
    decode_responses=True
)

# Test connection
r.ping()

# Set and get values
r.set('key', 'value')
print(r.get('key'))

# Set with expiration (60 seconds)
r.setex('temp_key', 60, 'temporary_value')

# Hash operations
r.hset('user:1', mapping={'name': 'John', 'age': '30'})
print(r.hgetall('user:1'))

# List operations
r.lpush('queue', 'task1', 'task2')
print(r.lrange('queue', 0, -1))
```

### Common Commands

```bash
# Set a key
docker exec -it redis_cache redis-cli -a redis_password SET mykey "Hello Redis"

# Get a key
docker exec -it redis_cache redis-cli -a redis_password GET mykey

# Set with expiration (seconds)
docker exec -it redis_cache redis-cli -a redis_password SETEX tempkey 60 "expires in 60 seconds"

# Check if key exists
docker exec -it redis_cache redis-cli -a redis_password EXISTS mykey

# Delete a key
docker exec -it redis_cache redis-cli -a redis_password DEL mykey

# Get all keys (use cautiously in production)
docker exec -it redis_cache redis-cli -a redis_password KEYS "*"

# Get database info
docker exec -it redis_cache redis-cli -a redis_password INFO

# Monitor commands in real-time
docker exec -it redis_cache redis-cli -a redis_password MONITOR
```

## Use Cases

### Caching

```python
import redis
import json
from datetime import timedelta

r = redis.Redis(host='localhost', port=6379, password='redis_password')

# Cache API response
def get_user_data(user_id):
    cache_key = f"user:{user_id}"

    # Try to get from cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # If not in cache, fetch from database
    user_data = fetch_from_database(user_id)

    # Store in cache for 1 hour
    r.setex(cache_key, timedelta(hours=1), json.dumps(user_data))

    return user_data
```

### Rate Limiting

```python
def check_rate_limit(user_id, max_requests=10, window_seconds=60):
    key = f"rate_limit:{user_id}"

    current = r.get(key)

    if current is None:
        # First request
        r.setex(key, window_seconds, 1)
        return True

    if int(current) >= max_requests:
        return False

    r.incr(key)
    return True
```

### Session Management

```python
def create_session(session_id, user_data, expiration=3600):
    session_key = f"session:{session_id}"
    r.setex(session_key, expiration, json.dumps(user_data))

def get_session(session_id):
    session_key = f"session:{session_id}"
    data = r.get(session_key)
    return json.loads(data) if data else None
```

### Queue/Task Management

```python
# Producer
def add_task(task_data):
    r.lpush('task_queue', json.dumps(task_data))

# Consumer
def process_tasks():
    while True:
        task = r.brpop('task_queue', timeout=1)
        if task:
            _, task_data = task
            process_task(json.loads(task_data))
```

## Monitoring

### Check Memory Usage

```bash
docker exec -it redis_cache redis-cli -a redis_password INFO memory
```

### Check Statistics

```bash
docker exec -it redis_cache redis-cli -a redis_password INFO stats
```

### View Slow Queries

```bash
docker exec -it redis_cache redis-cli -a redis_password SLOWLOG get 10
```

## Backup and Restore

### Manual Backup

```bash
# Trigger save
docker exec -it redis_cache redis-cli -a redis_password BGSAVE

# Copy dump file
docker cp redis_cache:/data/dump.rdb ./backup/
```

### Restore from Backup

```bash
# Stop Redis
docker-compose down

# Replace data file
docker cp ./backup/dump.rdb redis_cache:/data/

# Start Redis
docker-compose up -d
```

## Security Considerations

1. **Change default password** in production
2. **Bind to localhost** if Redis is only accessed locally
3. **Use TLS** for encrypted connections in production
4. **Rename dangerous commands** (CONFIG, FLUSHALL, etc.)
5. **Enable protected mode** for production environments

## Troubleshooting

### Check logs

```bash
docker-compose logs -f redis
```

### Restart service

```bash
docker-compose restart redis
```

### Clear all data

```bash
docker exec -it redis_cache redis-cli -a redis_password FLUSHALL
```

### Reset and start fresh

```bash
docker-compose down -v
docker-compose up -d
```

## Resources

- [Redis Documentation](https://redis.io/documentation)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- [Redis Commands Reference](https://redis.io/commands)
- [Redis Best Practices](https://redis.io/topics/best-practices)
