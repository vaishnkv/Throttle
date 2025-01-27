import threading
import time
from functools import wraps
from .cache import Cache
from .redis_client import (
    increment_redis_value,
    exists_in_redis,
    set_redis_value,
    get_redis_value
)
from loguru import logger

# Configurations
DEFAULT_EXPIRY = 60  # 1 minute


class PeriodicRateLimiter:
    def __init__(self, max_cache_size=100, pooling_interval=10):
        self.user_usertype_cache = Cache(max_cache_size)
        self.usertype_maxrequests_cache = Cache(max_cache_size)
        self.pooling_interval = pooling_interval
        self.start_periodic_pooling()

    def start_periodic_pooling(self):
        def update_cache():
            while True:
                for key in list(self.user_usertype_cache.dict.keys()):
                    usertype = get_redis_value(f"User_Usertype_map:{key}")
                    if usertype!=self.user_usertype_cache.get(key): # push only if there is a change
                        self.user_usertype_cache.push(key, usertype)
                        logger.info(f"User type updated for user_id: {key}")

                for key in list(self.usertype_maxrequests_cache.dict.keys()):
                    max_requests = get_redis_value(f"Usertype_Maxnumrequests_map:{key}")
                    if max_requests!=self.usertype_maxrequests_cache.get(key): # push only if there is a change
                        self.usertype_maxrequests_cache.push(key, max_requests)
                        logger.info(f"Max requests updated for user_type: {key}")

                time.sleep(self.pooling_interval)

        thread = threading.Thread(target=update_cache, daemon=True)
        thread.start()

    def check_rate_limit(self, user_id):

        usertype = self.user_usertype_cache.get(user_id)
        
        if not usertype:
            usertype = get_redis_value(f"User_Usertype_map:{user_id}")
            logger.info(f"Cache Miss marked for the User_Usertype_map ,for the user_id {user_id}")
            if usertype:
                self.user_usertype_cache.push(user_id, usertype)
                logger.info(f"Updated the RAM cache for the User_Usertype_map ,for the user_id {user_id}")
            else:
                logger.info(f"User type not found for user_id: {user_id} , inconsistency error")
                return False

        max_requests = self.usertype_maxrequests_cache.get(usertype)
        if not max_requests:
            max_requests = get_redis_value(f"Usertype_Maxnumrequests_map:{usertype}")
            logger.info(f"Cache Miss marked for the Usertype_Maxnumrequests_map ,for the usertype {usertype}")
            if max_requests:
                self.usertype_maxrequests_cache.push(usertype, int(max_requests))
                logger.info(f"Updated the RAM cache for the Usertype_Maxnumrequests_map ,for the usertype {usertype}, with {int(max_requests)}")
            else:
                logger.info(f"Max requests is not found for user_type: {usertype} , inconsistency error")
                return False
        
        if not exists_in_redis(f"User_Requestcount_map:{user_id}"):
            if int(max_requests)>0:
                set_redis_value(f"User_Requestcount_map:{user_id}",1,DEFAULT_EXPIRY)
                logger.info(f"updated the the User_Requestcount_map for the user_id {user_id}")
                return True
        else:
            request_count = int(get_redis_value(f"User_Requestcount_map:{user_id}"))
            logger.info(f"Request count for user_id: {user_id} is {request_count}")
            if request_count < int(max_requests):
                logger.info(f"Processing the request as {request_count} < {max_requests}")
                increment_redis_value(f"User_Requestcount_map:{user_id}")
                return True
        return False

    def rate_limiter_check(self):
        """Decorator for rate limiting."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                from flask import request, jsonify

                user_id = request.headers.get("User-ID")
                if not user_id:
                    return jsonify({"error": "User-ID header missing"}), 400

                if not self.check_rate_limit(user_id):
                    return jsonify({"error": "Rate limit exceeded"}), 429

                return func(*args, **kwargs)

            return wrapper
        return decorator

