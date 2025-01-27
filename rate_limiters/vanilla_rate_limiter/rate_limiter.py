from functools import wraps
from flask import request, jsonify
from .redis_client import get_redis_value, set_redis_value, increment_redis_value, exists_in_redis

# Configurations
DEFAULT_EXPIRY = 60  # 1 minute

def rate_limiter_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get("User-ID")
        if not user_id:
            return jsonify({"error": "User ID not provided"}), 400

        # Fetch user type
        user_type = get_redis_value(f"User_Usertype_map:{user_id}")
        if not user_type:
            return jsonify({"error": "User type not found"}), 400

        # Fetch max allowed requests for the user type
        max_requests = get_redis_value(f"Usertype_Maxnumrequests_map:{user_type}")
        if not max_requests:
            return jsonify({"error": "Max requests not configured for user type"}), 400
        max_requests = int(max_requests)

        # Check or update User_Requestcount_map
        request_count_key = f"User_Requestcount_map:{user_id}"
        if exists_in_redis(request_count_key):
            current_count = int(get_redis_value(request_count_key))
            if current_count < max_requests:
                increment_redis_value(request_count_key)
                return func(*args, **kwargs)
            else:
                return jsonify({"error": "Rate limit exceeded"}), 429
        else:
            if max_requests > 0:
                set_redis_value(request_count_key, 1, DEFAULT_EXPIRY)
                return func(*args, **kwargs)

    return wrapper
