# -*- coding: utf-8 -*-
import schedule
import time
import core

def job():
    try:
        core.watch()
    except Exception as e:
        print(f"Error in job: {e}")

# Run every 5 minutes to respect API limits and accumulation window
schedule.every(5).minutes.do(job)

print("War Detection System Started...")
print("Monitoring Eastern Bloc airspace for private jet exit events.")

# Run once immediately on startup
job()

while True:
    schedule.run_pending()
    time.sleep(1)
