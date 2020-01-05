import redis

from global_config import redis_password, redis_host,redis_port

redis_session = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password,
                               encoding='utf8', decode_responses=True, db=0)