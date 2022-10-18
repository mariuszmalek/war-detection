# -*- coding: utf-8 -*-
import schedule
import time
import core

def job():
    print("I'm watching planes...")
    core.watch()
 
schedule.every(1).minutes.do(job)
    
while True:
    schedule.run_pending()
    time.sleep(1)