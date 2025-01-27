import redis

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Sample data for ingestion
user_data = {
    "user1": "basic",
    "user2": "premium",
    "user3": "enterprise",
    "user4": "basic",
    "user5": "basic",
    "user6": "basic",
    "user7": "basic",
    "user8": "basic",
}

usertype_max_requests = {
    "basic": 10,      # Max 10 requests per minute
    "premium": 50,    # Max 50 requests per minute
    "enterprise": 100 # Max 100 requests per minute
}

def ingest_data_to_redis():
    # Populate User_Usertype_map
    for user_id, user_type in user_data.items():
        redis_client.set(f"User_Usertype_map:{user_id}", user_type)
        print(f"Set User_Usertype_map:{user_id} -> {user_type}")
    
    # Populate Usertype_Maxnumrequests_map
    for user_type, max_requests in usertype_max_requests.items():
        redis_client.set(f"Usertype_Maxnumrequests_map:{user_type}", max_requests)
        print(f"Set Usertype_Maxnumrequests_map:{user_type} -> {max_requests}")
    
    # Initialize User_Requestcount_map with some dummy values
    for user_id in user_data.keys():
        redis_client.setex(f"User_Requestcount_map:{user_id}", 60, 0)
        print(f"Set User_Requestcount_map:{user_id} -> 0 (with 1-minute expiry)")

if __name__ == "__main__":
    ingest_data_to_redis()
    print("Data ingestion complete!")
