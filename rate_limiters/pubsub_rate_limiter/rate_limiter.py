import threading
from flask import request, jsonify
from functools import wraps
from loguru import logger
from .cache import Cache
from .redis_client import get_redis_value, set_redis_value, increment_redis_value, exists_in_redis
import redis

DEFAULT_EXPIRY = 60  # 1 minute

class SubscriptionRateLimiter:
    def __init__(self, max_cache_size=100):
        self.user_usertype_cache = Cache(max_cache_size)
        self.usertype_maxrequests_cache = Cache(max_cache_size)
        self.redis_subscriber = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        self.start_subscription_thread()

    def start_subscription_thread(self):
        def listen_for_updates():
            pubsub = self.redis_subscriber.pubsub()
            pubsub.psubscribe("__keyspace@0__:User_Usertype_map:*", "__keyspace@0__:Usertype_Maxnumrequests_map:*")
            for message in pubsub.listen():
                # logger.info(f"Received message: {message}")
                if message["type"] == "pmessage":
                    event = message["data"]
                    key = message["channel"].split(":",1)[-1]
                    if event == "set":
                        # logger.info(message["channel"])
                        # logger.info(f"Handling cache update for key: {message['channel'].split(':')}")
                        # logger.info(f"Handling cache update for key: {key}")
                        self.handle_cache_update(key)

        thread = threading.Thread(target=listen_for_updates, daemon=True)
        thread.start()

    def handle_cache_update(self, key):
        """Update the cache when notified by Redis."""
        if key.startswith("User_Usertype_map:"):
            user_id = key.split(":")[-1]
            usertype = get_redis_value(key)
            if usertype:
                self.user_usertype_cache.push(user_id, usertype)
                logger.info(f"User type cache updated for user_id: {user_id} to {usertype}")
        elif key.startswith("Usertype_Maxnumrequests_map:"):
            usertype = key.split(":")[-1]
            max_requests = get_redis_value(key)
            if max_requests:
                self.usertype_maxrequests_cache.push(usertype, int(max_requests))
                logger.info(f"Max requests cache updated for usertype: {usertype} to {max_requests}")

    def check_rate_limit(self, user_id):
        """Check if a user is within the rate limit."""
        usertype = self.user_usertype_cache.get(user_id)
        if not usertype:
            usertype = get_redis_value(f"User_Usertype_map:{user_id}")
            if usertype:
                self.user_usertype_cache.push(user_id, usertype)
            else:
                return False

        max_requests = self.usertype_maxrequests_cache.get(usertype)
        if not max_requests:
            max_requests = get_redis_value(f"Usertype_Maxnumrequests_map:{usertype}")
            if max_requests:
                self.usertype_maxrequests_cache.push(usertype, int(max_requests))
            else:
                return False

        if not exists_in_redis(f"User_Requestcount_map:{user_id}"):
            set_redis_value(f"User_Requestcount_map:{user_id}", 1, DEFAULT_EXPIRY)
            return True
        else:
            request_count = int(get_redis_value(f"User_Requestcount_map:{user_id}"))
            if request_count < int(max_requests):
                increment_redis_value(f"User_Requestcount_map:{user_id}")
                return True
        return False

    def rate_limiter_check(self):
        """Decorator to apply rate limiting."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_id = request.headers.get("User-ID")
                if not user_id:
                    return jsonify({"error": "User-ID header missing"}), 400

                if not self.check_rate_limit(user_id):
                    return jsonify({"error": "Rate limit exceeded"}), 429

                return func(*args, **kwargs)
            return wrapper
        return decorator
