import requests
import time

# Flask server endpoint
API_URL = "http://localhost:5000/submit_job"
USER_ID = "user1"  # Specify the user to test rate limiting

def make_requests(user_id, num_requests):
    headers = {"User-ID": user_id}  # Include user ID in headers
    for i in range(num_requests):
        response = requests.post(API_URL, headers=headers)
        if response.status_code == 200:
            print(f"Request {i + 1}: SUCCESS - {response.json()}")
        elif response.status_code == 429:  # HTTP 429 Too Many Requests
            print(f"Request {i + 1}: RATE LIMIT EXCEEDED - {response.text}")
        else:
            print(f"Request {i + 1}: FAILED - Status Code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    num_requests = 15  # Number of requests to make
    print(f"Sending {num_requests} requests for user '{USER_ID}' to test rate limiting...")
    make_requests(USER_ID, num_requests)
