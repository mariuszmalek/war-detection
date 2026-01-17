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
        
        # Initialize API v1.1 interface as fallback
        auth = tweepy.OAuth1UserHandler(
            os.getenv('CONSUMER_KEY'),
            os.getenv('CONSUMER_SECRET'),
            os.getenv('ACCESS_TOKEN'),
            os.getenv('ACCESS_SECRET')
        )
        self.api_v1 = tweepy.API(auth)
    
    def post(self, text):
        if not text:
            print("No text to post.")
            return None
        
        try:
            # Try posting using v2 API first
            print("Attempting to post with API v2...")
            response = self.client.create_tweet(text=text)
            print(f"Post sent to Twitter (v2). ID: {response.data['id']}")
            return response
        except tweepy.errors.Forbidden as e:
            print(f"⛔️ 403 Forbidden (v2): {e}")
            if "403 Forbidden" in str(e) or "401 Unauthorized" in str(e):
                 print("Trying fallback to API v1.1...")
                 try:
                     response = self.api_v1.update_status(status=text)
                     print(f"Post sent to Twitter (v1.1). ID: {response.id}")
                     return response
                 except Exception as e_v1:
                     print(f"Error posting to Twitter (v1.1): {e_v1}")
            
            print("To oznacza brak uprawnień 'Write' dla Twoich tokenów.")
            print("👉 Wejdź na Twitter Developer Portal -> Settings -> User authentication settings.")
            print("👉 Zmień App permissions na 'Read and write'.")
            print("👉 WAŻNE: Wróć do 'Keys and tokens' i WYGENERUJ NOWE Access Token i Secret.")
            print("👉 Zaktualizuj plik .env nowymi tokenami.")
            return None
        except Exception as e:
            print(f"Error posting to Twitter (v2): {e}")
            if "402 Payment Required" in str(e):
                print("⚠️ 402 Payment Required - Trying fallback to API v1.1...")
                try:
                    response = self.api_v1.update_status(status=text)
                    print(f"Post sent to Twitter (v1.1). ID: {response.id}")
                    return response
                except Exception as e_v1:
                    print(f"Error posting to Twitter (v1.1): {e_v1}")
            return None
