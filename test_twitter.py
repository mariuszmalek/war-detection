import os
from clients.twitter import TwitterClient

def test_integration():
    print("Testing Twitter Integration...")
    
    # Check if env vars are present
    required_vars = ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_SECRET']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please ensure .env contains: CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET")
        return

    print("✅ Environment variables found.")
    
    try:
        client = TwitterClient()
        print("✅ TwitterClient initialized.")
        
        # Skip get_me() check as it's not available in Free Tier
        # Send a real test tweet
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tweet_text = f"Test WarDetection Bot Integration\nTimestamp: {timestamp}\n✅ System Online"
        
        print(f"Attempting to post: \n{tweet_text}")
        response = client.post(tweet_text)
        
        if response and response.data:
            print(f"✅ Tweet sent successfully! ID: {response.data['id']}")
        else:
            print("❌ Tweet failed (no response data).")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == "__main__":
    test_integration()
