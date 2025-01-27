from flask import Flask, jsonify


RATE_LIMITER_TYPE = "PUBSUB-BASED" # "VANILLA" , "POOLING-BASED" or "PUBSUB-BASED"

if RATE_LIMITER_TYPE=="VANILLA":
    from rate_limiters.vanilla_rate_limiter.rate_limiter import rate_limiter_check
elif RATE_LIMITER_TYPE=="POOLING-BASED":
    from rate_limiters.pooling_rate_limiter.rate_limiter import PeriodicRateLimiter
    rate_limiter = PeriodicRateLimiter()
    rate_limiter_check = rate_limiter.rate_limiter_check()  # Get the decorator
elif RATE_LIMITER_TYPE=="PUBSUB-BASED":
    from rate_limiters.pubsub_rate_limiter.rate_limiter import SubscriptionRateLimiter
    rate_limiter = SubscriptionRateLimiter(max_cache_size=100)
    rate_limiter_check = rate_limiter.rate_limiter_check()  # Get the decorator
else:
    assert False, "Invalid RATE_LIMITER_TYPE"


app = Flask(__name__)

@app.route("/submit_job", methods=["POST"])
@rate_limiter_check
def submit_job():
    return jsonify({"message": "Job submitted successfully!"}), 200

if __name__ == "__main__":
    app.run(host="localhost",port=5000, debug=True)