import os
import tweepy

from dotenv import load_dotenv

load_dotenv()

class TwitterClient():
    def auth(self):
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(
            os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET')
        )
        
        auth.set_access_token(
            os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_SECRET')
        )
        
        client = tweepy.API(auth)

        return client
    
    
    def post(self, client, data):
        if not client or not data:
            return 0
        
        # Post twitt
        client.update_status(data)
        print("Post was sended to Twitter")