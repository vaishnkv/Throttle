import redis

# Singleton Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# def get_redis_value(key):
#     return redis_client.get(key)

# def set_redis_value(key, value, expiry=None):
#     if expiry:
#         redis_client.setex(key, expiry, value)
#     else:
#         redis_client.set(key, value)

# def increment_redis_value(key):
#     return redis_client.incr(key)

# def exists_in_redis(key):
#     return redis_client.exists(key)


def get_redis_value(key):
    return redis_client.get(key)

def set_redis_value(key, value, expiry=None):
    if expiry:
        redis_client.setex(key, expiry, value)
    else:
        redis_client.set(key, value)

def increment_redis_value(key):
    return redis_client.incr(key)

def exists_in_redis(key):
    return redis_client.exists(key)

def get_redis_hash_value(hash_key, field):
    return redis_client.hget(hash_key, field)

def set_redis_hash_value(hash_key, field, value):
    redis_client.hset(hash_key, field, value)

def expire_redis_key(key, expiry):
    redis_client.expire(key, expiry)