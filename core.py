import datetime as time
import json

from clients import twitter
from clients import opensky
from clients import google

def watch():
    now = time.datetime.now()
    
    # Save data in storage (spreadsheet)
    gspread = google.GoogleSpreadsheet()
    
    # Get data from opensky
    opensky_client = opensky.OpenskyClient()
    collection = opensky_client.detect()
    
    num = len(collection[0])
    
    # Get last planes count for calculate risk
    last_planes_count = gspread.last_planes_count()
    
    # Post data to storage spreadsheet
    gspread.post(num)
    
    if str(num) > last_planes_count:
        alert(num, last_planes_count)
    
def alert(num, last_planes_count):
    count = "{0}".format(num)
    risk = calculate_risk(num)

    text = "[WAR-DETECTION] Detected " + count + " private planes flying from the Eastern Bloc to West. 🚩" + " (Yesterday there were " + last_planes_count + " planes) https://docs.google.com/spreadsheets/d/10ZeOiZoSw1cZEHwoXG1auJ6ovWI5PhyvrtlhUrOalrM"
    
    # Send data to Twitter
    twitter_client = twitter.TwitterClient()
    client = twitter_client.auth()
    twitter_client.post(client, text)
    
def calculate_risk(count):
    answear = "LOW"
    
    if count >= 500:
        answear = "HIGH"
        
    return answear