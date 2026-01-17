import os
import tweepy

from dotenv import load_dotenv

load_dotenv()

class TwitterClient():
    def __init__(self):
        # Authenticate to Twitter using API v2 (Client)
        # This requires Consumer Keys and Access Tokens (OAuth 1.0a User Context)
        # or Bearer Token (OAuth 2.0 App-Only) - for posting we usually need User Context.
        self.client = tweepy.Client(
            consumer_key=os.getenv('CONSUMER_KEY'),
            consumer_secret=os.getenv('CONSUMER_SECRET'),
            access_token=os.getenv('ACCESS_TOKEN'),
            access_token_secret=os.getenv('ACCESS_SECRET')
        )
    
    def post(self, text):
        if not text:
            print("No text to post.")
            return None
        
        try:
            # Post tweet using v2 API
            response = self.client.create_tweet(text=text)
            print(f"Post sent to Twitter. ID: {response.data['id']}")
            return response
        except Exception as e:
            print(f"Error posting to Twitter: {e}")
            return None
