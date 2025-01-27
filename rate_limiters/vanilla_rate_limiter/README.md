# Vanilla Rate Limiter

This module implements a **fixed-window rate-limiting system** without caching. It ensures consistent behavior by interacting directly with Redis for each request.

## Features
- No RAM caching for request counts or user details.
- Strict reliance on Redis for live request counts and configurations.
- Simple and predictable behavior.

## Workflow
1. Extract `user_id` from the request.
2. Check if `user_id` exists in `User_Requestcount_map` in Redis:
   - If it exists:
     - Retrieve the user type from `User_Usertype_map`.
     - Get the max allowed requests for the user type from `Usertype_Maxnumrequests_map`.
     - Compare the user's request count with the max allowed requests:
       - If within limits, increment the count and allow the request.
       - Otherwise, reject the request with a "Rate Limit Exceeded" status.
   - If it doesn't exist:
     - Add an entry to `User_Requestcount_map` for `user_id` with an initial count of `1` and a 1-minute expiry.
     - Allow the request.

## Files
- `rate_limiter.py`: Core logic for the vanilla rate limiter.
- `redis_client.py`: Handles interactions with Redis.

## Usage
Import the module and use the `Rate_limiter_check` decorator for your Flask endpoints.

```python
from vanilla_rate_limiter.rate_limiter import Rate_limiter_check

@app.route('/submit_job', methods=['POST'])
@Rate_limiter_check
def submit_job():
    # Core logic here
    return "Job submitted successfully!"
