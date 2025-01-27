# Throttle

This project implements **fixed-window rate limiters** using Redis to manage request limits for users based on their subscription type. It provides three variants with varying caching mechanisms:

1. **Vanilla Rate Limiter**: No caching; ensures consistent data by always querying Redis.
2. **Periodic Pooling + RAM Caching Rate Limiter**: Combines lazy caching with periodic synchronization from Redis.
3. **Subscription + RAM Caching Rate Limiter**: Uses Redis Pub/Sub to proactively update local caches in real-time.

---

## Assumptions
- The objective is to **rate limit a service** with one operational endpoint.
- User types can be one of the following: `normal_user`, `premium_user`, or `admin`.
- **Max allowed requests** for user types are not changed frequently, resulting in reasonably low configuration load.
- Any user can make **a minimum of 0 requests**.
- The service is under **reasonably high load**, with multiple replicas of the server behind a load balancer.  
  - This necessitates the use of a centrally accessible database (Redis) for maintaining the `Request_count` instead of storing it as a Python dictionary in memory.

---

## Configuration Store: Redis

### Schemas
1. **`User_Requestcount_map`**  
   - Tracks the live number of requests received from each user.  
   - Each key (user ID) has an expiry of **1 minute**.
   
2. **`User_Usertype_map`**  
   - Maps each user ID to their corresponding user type (e.g., `normal_user`, `premium_user`, `admin`).

3. **`Usertype_Maxnumrequests_map`**  
   - Maps each user type to its respective **maximum allowed requests**.

---

## Flask Server

- A dummy Flask-based HTTP server is implemented with one endpoint:
  - **Endpoint:** `/submit_job`  
    Decorated with a `Rate_limiter_check` function, which implements the rate limiter before executing the core logic.

---

## Features
- Rate limiting using a **fixed-window** approach.
- Redis-backed live request tracking with a flexible schema.
- Modular implementation of rate limiter variants:
  1. Vanilla Rate Limiter: No caching, strict consistency.
  2. Periodic Pooling + RAM Caching: Lazy caching with periodic syncs.
  3. Subscription + RAM Caching: Real-time updates using Redis Pub/Sub.

---

## Project Structure

.
├── rate_limiters
│   ├── __init__.py
│   ├── caches
│   │   ├── fixed_len_cache_with_deletion_opt.py
│   │   ├── fixed_len_cache_with_no_deletion.py
│   │   └── fixed_len_cache_with_priority_promotion.py
│   ├── pooling_rate_limiter
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── rate_limiter.py
│   │   └── redis_client.py
│   ├── pubsub_rate_limiter
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── rate_limiter.py
│   │   └── redis_client.py
│   └── vanilla_rate_limiter
│       ├── __init__.py
│       ├── rate_limiter.py
│       └── redis_client.py
├── sample_clients
│   ├── client_for_data_ingestion.py
│   ├── client_for_no_cache.py
│   ├── client_for_pooling.py
│   └── client_for_pubsub.py
└── server.py

