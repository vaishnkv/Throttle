# Subscription + RAM Caching Rate Limiter

This module implements a **proactive caching mechanism** using Redis Pub/Sub for real-time cache updates. It ensures high performance and reduced inconsistencies.

## Features
- RAM caching for:
  - User-to-user type mapping.
  - User type-to-max request mapping.
- Real-time cache updates via Redis Pub/Sub.
- Combines lazy caching with proactive updates for reduced latency and improved accuracy.

## Workflow
1. Extract `user_id` from the request.
2. Check `user_id` in `User_Requestcount_map` in Redis:
   - If it exists:
     - Fetch `user_type` from RAM cache (`User_Usertype_dict`) or Redis.
     - Fetch `max_allowed_requests` from RAM cache (`Usertype_Maxnumrequests_dict`) or Redis.
     - Compare the request count with the max allowed requests:
       - If within limits, increment the count and allow the request.
       - Otherwise, reject the request with a "Rate Limit Exceeded" status.
   - If it doesn't exist:
     - Add an entry to `User_Requestcount_map` for `user_id` with an initial count of `1` and a 1-minute expiry.
     - Allow the request.
3. A background thread listens to Redis channels for updates and modifies the local cache accordingly.

## Files
- `rate_limiter.py`: Core logic for the rate limiter.
- `cache.py`: RAM caching implementation using a combination of Python `dict` and a doubly linked list.
- `redis_client.py`: Handles both Redis interactions and Pub/Sub subscriptions.

## Usage
Import the module and use the `Rate_limiter_check` decorator for your Flask endpoints.

```python
from pubsub_rate_limiter.rate_limiter import Rate_limiter_check

@app.route('/submit_job', methods=['POST'])
@Rate_limiter_check
def submit_job():
    # Core logic here
    return "Job submitted successfully!"
