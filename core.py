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
    
    num = len(collection[0])
    
    if num > 1:
        gspread.post(num)
        # alert(num)
    
def alert(num):
    count = "{0}".format(num)
    risk = calculate_risk(num)

    text = "[WAR-DETECTION] Detected " + count + " private planes flying from the Eastern Bloc to West. 🚩" + " https://docs.google.com/spreadsheets/d/10ZeOiZoSw1cZEHwoXG1auJ6ovWI5PhyvrtlhUrOalrM"
    
    twitter_client = twitter.TwitterClient()
    client = twitter_client.auth()
    twitter_client.post(client, text)

    
def calculate_risk(count):
    answear = "LOW"
    
    if count >= 500:
        answear = "HIGH"
        
    return answear