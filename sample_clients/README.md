
---

### Clients Folder: `sample_clients/README.md`

```markdown
# Sample Clients

This folder contains client scripts to test the three different rate limiter implementations. Each script simulates requests to the Flask server with varying configurations.

## Clients
### 1. `client_for_no_cache.py`
- Tests the **Vanilla Rate Limiter**.
- Sends requests without using any local cache.
- Verifies the strict consistency provided by querying Redis for every request.

### 2. `client_for_pooling.py`
- Tests the **Periodic Pooling + RAM Caching Rate Limiter**.
- Simulates lazy caching with periodic updates from Redis.
- Demonstrates the balance between performance and consistency.

### 3. `client_for_pubsub.py`
- Tests the **Subscription + RAM Caching Rate Limiter**.
- Simulates real-time updates using Redis Pub/Sub.
- Demonstrates reduced latency for high-frequency request scenarios.

### 4. `client_for_data_ingestion.py`
- Populates Redis with sample data for testing.
- Adds:
  - User-to-user type mappings (`User_Usertype_map`).
  - User type-to-max request limits (`Usertype_Maxnumrequests_map`).

## Prerequisites
1. Ensure the Flask server is running:
   ```bash
   python server.py
