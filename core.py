import datetime as time
import json

from clients import twitter
from clients import opensky
from clients import google

def watch():
    now = time.datetime.now()
    
    opensky_client = opensky.OpenskyClient()
    gspread = google.GoogleSpreadsheet()

    collection = opensky_client.detect()
    
    # print(collection[0])
    
    gspread.post()
    
    if len(collection[0]) > 1:
        alert(collection)
    
def alert(data):
    if len(data[0]) > 0 and len(data[1]) > 0:
                
        num = len(data[0])
        count = "{0}".format(num)
        risk = calculate_risk(num)

        text = "[WAR-DETECTION] Detected " + count + " private planes flying from the Eastern Bloc to West. 🚩" + " https://docs.google.com/spreadsheets/d/10ZeOiZoSw1cZEHwoXG1auJ6ovWI5PhyvrtlhUrOalrM"
        
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