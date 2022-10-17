import os
import tweepy

from dotenv import load_dotenv

load_dotenv()

class TwitterClient():
    def auth(self):
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(
            os.getenv('consumer_key'), os.getenv('consumer_secret')
        )
        
        auth.set_access_token(
            os.getenv('access_token'), os.getenv('access_secret')
        )
        
        client = tweepy.API(auth)

        return client
    
    
    def post(self, client, data):
        if not client or not data:
            return 0
        
        # Post twitt
        client.update_status(data)
        print("Post was sended to Twitter")