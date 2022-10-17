# -*- coding: utf-8 -*-

import datetime as time
import json

from clients import opensky
from clients import twitter

def alert(data):
    if len(data[0]) > 0 and len(data[1]) > 0:
                
        count = "{0}".format(len(data[0]))
        risk = "LOW"

        text = "[WAR-DETECTION] We detected " + count + " private planes flying from the Eastern Bloc to West. 🚩"
        
        twitter_client = twitter.TwitterClient()
        client = twitter_client.auth()
        twitter_client.post(client, text)
        
    else:
        return 0

  
try:
    now = time.datetime.now()
    
    opensky_client = opensky.OpenskyClient()
    collection = opensky_client.detect()
    
    # print(collection[0])
    
    if len(collection[0]) > 1:
        alert(collection)
    
except Exception as ex:
    print(ex)