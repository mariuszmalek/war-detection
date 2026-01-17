import os
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv()

# Setup authentication
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_SECRET")

auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

# Define the endpoint URL
url = "https://api.twitter.com/2/tweets"

# Define the payload
payload = {"text": "Hello World! This is a test tweet from my bot."}

# Make the request
print(f"Attempting to post to {url}...")
try:
    response = requests.post(url, auth=auth, json=payload)
    
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    print(f"Response Headers: {response.headers}")
    
except Exception as e:
    print(f"Error: {e}")
