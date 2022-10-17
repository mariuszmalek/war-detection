import datetime as time
import json

from clients import twitter
from clients import opensky

def watch():
    now = time.datetime.now()
    
    opensky_client = opensky.OpenskyClient()
    collection = opensky_client.detect()
    
    # print(collection[0])
    
    if len(collection[0]) > 1:
        alert(collection)
    
def alert(data):
    if len(data[0]) > 0 and len(data[1]) > 0:
                
        num = len(data[0])
        count = "{0}".format(num)
        risk = calculate_risk(num)

        text = "[WAR-DETECTION] Detected " + count + " private planes flying from the Eastern Bloc to West. 🚩"
        
        twitter_client = twitter.TwitterClient()
        client = twitter_client.auth()
        twitter_client.post(client, text)
        
    else:
        return 0
    
def calculate_risk(count):
    answear = "LOW"
    
    if count >= 500:
        answear = "HIGH"
        
    return answear