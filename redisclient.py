import redis
from config import redis_server, redis_port

Redis = redis.Redis(
	host=redis_server,
	port=redis_port
)
