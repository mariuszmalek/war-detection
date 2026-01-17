import os
from clients.twitter import TwitterClient

def test_integration():
    print("Testing Twitter Integration...")
    
    # Check if env vars are present
    required_vars = ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_TOKEN', 'ACCESS_SECRET']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please fill in .env file.")
        return

    print("✅ Environment variables found.")
    
    try:
        client = TwitterClient()
        print("✅ TwitterClient initialized.")
        
        # We don't want to actually post spam, so we might just check credentials if possible.
        # tweepy.Client.get_me() is a good check.
        user = client.client.get_me()
        if user.data:
            print(f"✅ Authentication successful! Logged in as: {user.data.name} (@{user.data.username})")
        else:
            print("❌ Authentication failed (get_me returned no data).")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == "__main__":
    test_integration()
