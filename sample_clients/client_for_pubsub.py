import requests
import redis
import time
import random
from loguru import logger

# Configurations
FLASK_SERVER_URL = "http://127.0.0.1:5000/submit_job"
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Redis client
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

if redis_client.ping() is False:
    assert False, "Redis connection failed"

# Helper functions
def clear_redis():
    """Clear all test-related Redis keys."""
    redis_client.delete("User_Requestcount_map")
    redis_client.delete("User_Usertype_map")
    redis_client.delete("Usertype_Maxnumrequests_map")

def setup_redis_data(user_data, usertype_data):
    """
    Set up test data in Redis.
    - user_data: Dictionary mapping user_id to user_type.
    - usertype_data: Dictionary mapping user_type to max requests.
    
    Note :
        All the values are primitives , hence just key-value pairs can be used.
    
    """
    # Store user_id -> user_type
    for user_id, user_type in user_data.items():
        redis_client.set(f"User_Usertype_map:{user_id}", user_type)

    # Store user_type -> max_requests
    for user_type, max_requests in usertype_data.items():
        redis_client.set(f"Usertype_Maxnumrequests_map:{user_type}", max_requests)

def send_request(user_id):
    """Send a POST request to the Flask server with the specified user_id."""
    headers = {"User-ID": user_id}
    response = requests.post(FLASK_SERVER_URL, headers=headers)
    return response.status_code, response.json()

def get_user_stats(user_ids):
    
    # Check Redis data
    for user_id in user_ids:
        request_count = redis_client.get(f"User_Requestcount_map:{user_id}")
        if request_count:
            logger.info(f"Final request count for {user_id}: {request_count}")
        else:
            logger.info(f"No request count found for {user_id}")
    

# Test cases
def test_rate_limiter():
    """Test the rate limiter functionality."""
    clear_redis()

    # Test setup
    user_data = {"user1": "free", "user2": "premium", "user3": "free"}
    usertype_data = {"free": 2, "premium": 5}
    setup_redis_data(user_data, usertype_data)
    # Simulate requests
    user_ids = list(user_data.keys())
    for i in range(20):  # Simulate 20 requests
        user_id = random.choice(user_ids)
        if i==10:
            # Increase the max requests for user type "premium" to 10
            redis_client.set(f"Usertype_Maxnumrequests_map:free", 5)
        status_code, response = send_request(user_id)
        print(f"User: {user_id}, Status Code: {status_code}, Response: {response}")
        time.sleep(random.uniform(1, 5))  # Simulate random delay between requests
    get_user_stats(user_ids)
    redis_client.set(f"Usertype_Maxnumrequests_map:free", 2)
    time.sleep(65)
    get_user_stats(user_ids)
    clear_redis()

if __name__ == "__main__":
    test_rate_limiter()
