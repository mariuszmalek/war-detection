import tweepy

class TwitterClient():
    def auth(self):
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        client = tweepy.API(auth)

        return client
    
    
    def post(self, client, data):
        if not client or not data:
            return 0
        
        # Post twitt
        client.update_status(data)
        print("Post was sended to Twitter")