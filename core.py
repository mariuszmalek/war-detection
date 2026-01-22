import datetime
import json
import os
import math
import base64
import reverse_geocoder as rg
import redis
import gspread
from google.oauth2.service_account import Credentials
from clients import twitter
from clients import opensky

# Configuration
HISTORY_FILE = "flight_history.json"
ALERT_THRESHOLD = 5  # Number of flights to trigger alert
TIME_WINDOW_HOURS = 48
GSHEET_NAME = "WarDetection_History"

# Safe Countries (ISO Codes) for reference, though we track departures mainly
SAFE_COUNTRY_CODES = ["CH", "AE", "GB", "US", "SG"] 

def get_redis_client():
    # Vercel KV uses KV_URL, standard Redis uses REDIS_URL
    redis_url = os.environ.get("KV_URL") or os.environ.get("REDIS_URL")
    if redis_url:
        try:
            # Use SSL if using rediss:// (Vercel KV usually does)
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
    return None

def get_gsheet_client():
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if not creds_json:
        return None
    
    try:
        # Handle base64 encoded credentials (common for env vars)
        try:
            creds_dict = json.loads(base64.b64decode(creds_json).decode())
        except:
            # Fallback to plain json string
            creds_dict = json.loads(creds_json)
            
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Failed to connect to Google Sheets: {e}")
        return None

def watch():
    print(f"[{datetime.datetime.now()}] Starting GLOBAL scan...")
    
    # 1. Get potential private jets from OpenSky (Global)
    opensky_client = opensky.OpenskyClient()
    planes = opensky_client.detect()
    
    print(f"Detected {len(planes)} potential private jets globally.")
    
    if not planes:
        return

    # 2. Geolocate Planes
    # Extract coordinates for batch processing
    coords = [(p["latitude"], p["longitude"]) for p in planes]
    
    # rg.search returns list of dicts: [{'lat':..., 'lon':..., 'cc': 'PL', ...}]
    # This might take a moment on first run
    results = rg.search(coords)
    
    exit_events = []
    current_time = datetime.datetime.now().timestamp()
    
    for plane, geo_info in zip(planes, results):
        country_code = geo_info.get('cc', 'Unknown')
        
        # Filter: We are looking for departures FROM risky areas TO safe areas?
        # OR just general spikes in departures from ANY country.
        # Given "Global" scope, we assume any spike is interesting.
        
        # Basic check: Must be airborne and moving
        # Handle cases where velocity might be None
        velocity = plane["velocity"] if plane["velocity"] is not None else 0
        is_flying = not plane["on_ground"] and velocity > 50
        
        if is_flying and country_code != 'Unknown':
            event = {
                "icao24": plane["icao24"],
                "callsign": plane["callsign"],
                "country": country_code,
                "timestamp": current_time,
                "lat": plane["latitude"],
                "lon": plane["longitude"]
            }
            exit_events.append(event)
            # print(f"  -> Tracking: {plane['callsign']} over {country_code}")

    # 3. Update History
    history = load_history()
    
    # Deduplicate: Add only if icao24 not seen in last hour
    recent_icaos = {e["icao24"] for e in history if current_time - e["timestamp"] < 3600}
    
    new_events = []
    for event in exit_events:
        if event["icao24"] not in recent_icaos:
            history.append(event)
            recent_icaos.add(event["icao24"])
            new_events.append(event)
    
    # Prune old history
    cutoff_time = current_time - (TIME_WINDOW_HOURS * 3600)
    history = [e for e in history if e["timestamp"] > cutoff_time]
    
    save_history(history)
    
    # 4. Scoring and Alerting per Country
    # Group by country
    country_counts = {}
    for e in history:
        c = e["country"]
        country_counts[c] = country_counts.get(c, 0) + 1
        
    print(f"Active Regions (48h): {len(country_counts)} countries. New events: {len(new_events)}")
    
    # Check for spikes
    for country, count in country_counts.items():
        if count > ALERT_THRESHOLD:
            # Check if this country had new events in this scan (to avoid repeating alerts)
            new_events_in_country = sum(1 for e in new_events if e["country"] == country)
            
            if new_events_in_country > 0:
                send_alert(count, country, new_events_in_country)

def load_history():
    # 1. Try Redis
    r = get_redis_client()
    if r:
        try:
            data = r.get("flight_history")
            if data:
                print("Loaded history from Redis.")
                return json.loads(data)
        except Exception as e:
            print(f"Error reading from Redis: {e}")

    # 2. Try Google Sheets
    gc = get_gsheet_client()
    if gc:
        try:
            # Open sheet or create if not exists
            try:
                sh = gc.open(GSHEET_NAME)
                worksheet = sh.sheet1
                # Assume data is in first cell as JSON string for simplicity
                # Or row by row. For <1000 items, JSON string in cell A1 is simplest hack.
                # But cells have 50k char limit.
                # Better: read all rows.
                records = worksheet.get_all_records()
                print(f"Loaded {len(records)} records from Google Sheets.")
                return records
            except gspread.exceptions.SpreadsheetNotFound:
                print("Spreadsheet not found, starting fresh.")
                return []
        except Exception as e:
            print(f"Error reading from Google Sheets: {e}")

    # 3. Fallback to local file
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    # 1. Try Redis
    r = get_redis_client()
    if r:
        try:
            r.set("flight_history", json.dumps(history))
            print("Saved history to Redis.")
        except Exception as e:
            print(f"Error writing to Redis: {e}")
    
    # 2. Try Google Sheets
    gc = get_gsheet_client()
    if gc:
        try:
            try:
                sh = gc.open(GSHEET_NAME)
            except gspread.exceptions.SpreadsheetNotFound:
                sh = gc.create(GSHEET_NAME)
                # Share with user email if possible, otherwise it's private to service account
                print(f"Created new spreadsheet: {GSHEET_NAME}")

            worksheet = sh.sheet1
            # Clear and write all (inefficient but safe for small data)
            worksheet.clear()
            if history:
                # Write headers
                headers = list(history[0].keys())
                worksheet.append_row(headers)
                # Write rows
                rows = [list(event.values()) for event in history]
                worksheet.append_rows(rows)
            print("Saved history to Google Sheets.")
        except Exception as e:
            print(f"Error writing to Google Sheets: {e}")

    # 3. Always save to local file as backup/cache
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def send_alert(score, country, new_count):
    text = (
        f"⚠️ Global Anomaly Detected\n\n"
        f"In the last {TIME_WINDOW_HOURS}h we detected an unusual spike in private jet activity over [{country}].\n\n"
        f"Activity Score: {score} flights.\n"
        f"High concentration of private aircraft departing/transit.\n\n"
        f"Monitoring potential risk indicators."
    )
    
    print("--------------------------------------------------")
    print("SENDING TWITTER ALERT:")
    print(text)
    print("--------------------------------------------------")
    
    try:
        twitter_client = twitter.TwitterClient()
        twitter_client.post(text)
    except Exception as e:
        print(f"Failed to send tweet: {e}")

