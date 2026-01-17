import datetime
import json
import os
import math
from clients import twitter
from clients import opensky

# Configuration
HISTORY_FILE = "flight_history.json"
ALERT_THRESHOLD = 5  # Number of flights to trigger alert
TIME_WINDOW_HOURS = 48

# Eastern Bloc Countries Approximation (Simplified Bounding Boxes)
# Format: (lat_min, lat_max, lon_min, lon_max)
# Ordered to handle overlaps (smaller/enclosed regions first)
REGIONS = {
    "Czechia": (48.5, 51.0, 12.1, 18.8),
    "Slovakia": (47.7, 49.6, 16.8, 22.6),
    "Hungary": (45.7, 48.6, 16.1, 22.9),
    "Serbia": (42.2, 46.2, 18.8, 23.0),
    "Bulgaria": (41.2, 44.2, 22.3, 28.6),
    "Romania": (43.6, 48.3, 20.2, 29.7),
    "Baltics": (53.9, 59.8, 20.9, 28.2), # Lithuania, Latvia, Estonia combined
    "Poland": (49.0, 54.8, 14.1, 24.1)  # Largest box last
}

SAFE_DESTINATIONS = ["Switzerland", "UAE", "UK", "USA"]

def watch():
    print(f"[{datetime.datetime.now()}] Starting scan...")
    
    # 1. Get potential private jets from OpenSky
    opensky_client = opensky.OpenskyClient()
    planes = opensky_client.detect()
    
    print(f"Detected {len(planes)} potential private jets in the broad region.")
    
    # 2. Filter for Exit Events
    exit_events = []
    current_time = datetime.datetime.now().timestamp()
    
    for plane in planes:
        country = get_origin_country(plane["latitude"], plane["longitude"])
        if country:
            # Check if heading towards safe countries (West or South-East)
            # West (UK, USA, Switzerland): ~220-320 degrees
            # South-East (UAE): ~110-160 degrees
            track = plane["true_track"]
            is_exit_heading = (220 <= track <= 320) or (110 <= track <= 160)
            
            # Additional check: Must be airborne and moving
            is_flying = not plane["on_ground"] and plane["velocity"] > 50
            
            if is_exit_heading and is_flying:
                event = {
                    "icao24": plane["icao24"],
                    "callsign": plane["callsign"],
                    "country": country,
                    "timestamp": current_time,
                    "track": track,
                    "lat": plane["latitude"],
                    "lon": plane["longitude"]
                }
                exit_events.append(event)
                print(f"  -> Exit Event Detected: {plane['callsign']} leaving {country} (Track: {track})")

    # 3. Update History and Calculate Score
    history = load_history()
    
    # Add new unique events (deduplicate by icao24 within last hour to avoid spamming same flight)
    # We only add if this icao24 hasn't been seen in the last hour
    recent_icaos = {e["icao24"] for e in history if current_time - e["timestamp"] < 3600}
    
    new_events_count = 0
    for event in exit_events:
        if event["icao24"] not in recent_icaos:
            history.append(event)
            recent_icaos.add(event["icao24"]) # Add to local set to prevent dupes in this very loop
            new_events_count += 1
    
    # Prune old history
    cutoff_time = current_time - (TIME_WINDOW_HOURS * 3600)
    history = [e for e in history if e["timestamp"] > cutoff_time]
    
    save_history(history)
    
    # 4. Scoring and Alerting
    threat_score = len(history)
    print(f"Current Threat Score (48h): {threat_score} (New events: {new_events_count})")
    
    if threat_score > ALERT_THRESHOLD and new_events_count > 0:
        # Only alert if we added new events that pushed us over or sustained the high level
        # To avoid repeating alerts every minute, we could store "last_alert_time"
        # For now, we alert if we found something new and the score is high.
        
        # Determine dominant countries
        countries = [e["country"] for e in history]
        most_active_country = max(set(countries), key=countries.count) if countries else "Eastern Bloc"
        
        send_alert(threat_score, most_active_country, new_events_count)

def get_origin_country(lat, lon):
    for country, (lat_min, lat_max, lon_min, lon_max) in REGIONS.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return country
    return None

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def send_alert(score, country, new_count):
    text = (
        f"⚠️ Early Warning Signal Detected\n\n"
        f"In the last {TIME_WINDOW_HOURS}h we detected an unusual spike in private jet departures from [{country}].\n\n"
        f"Threat Score: {score} (Cluster detected).\n"
        f"Multiple aircraft linked to high-net-worth individuals departed towards Safe Zones.\n\n"
        f"This is not a confirmation, but a data anomaly."
    )
    
    print("--------------------------------------------------")
    print("SENDING TWITTER ALERT:")
    print(text)
    print("--------------------------------------------------")
    
    try:
        twitter_client = twitter.TwitterClient()
        client = twitter_client.auth()
        if client:
             twitter_client.post(client, text)
    except Exception as e:
        print(f"Failed to send tweet: {e}")
