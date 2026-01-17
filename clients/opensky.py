import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

# Common commercial, cargo, and military airline codes to filter out
EXCLUDED_AIRLINES = {
    "RYR", "WZZ", "LOT", "ENT", "RYS", "NSZ", "AUA", "DLH", "AFR", "BAW", 
    "SAS", "FIN", "KLM", "EZY", "TRA", "BTI", "SWR", "UAE", "QTR", "THY",
    "AFL", "UPS", "FDX", "GTI", "CLX", "BOX", "BCS", "TAY", "SRR", "NPT"
}

class OpenskyClient():

    def detect(self):
        states = self.fetch()
        
        private_jets = []
        
        if states:
            for state in states:
                # State vector indices:
                # 0: icao24, 1: callsign, 2: origin_country, 5: longitude, 6: latitude, 
                # 9: velocity, 10: true_track, 13: geo_altitude, 17: category
                
                icao24 = state[0]
                callsign = state[1].strip()
                
                if not callsign:
                    continue
                    
                # Heuristic 1: Filter out known commercial airline codes
                if any(callsign.startswith(code) for code in EXCLUDED_AIRLINES):
                    continue
                
                # Heuristic 2: Check for commercial flight number pattern (3 letters + numbers)
                # e.g., BAW123, DLH456. Private jets usually use registration e.g., N12345, SP-ABC.
                if re.match(r'^[A-Z]{3}\d+', callsign):
                    continue

                # Heuristic 3: Filter by category if available (not reliable in basic API, but useful if present)
                # 1 = No ADS-B Emitter Category Information
                # We assume if it passed the filters above, it's a candidate.
                
                # Construct a clean object
                plane = {
                    "icao24": icao24,
                    "callsign": callsign,
                    "origin_country": state[2],
                    "longitude": state[5],
                    "latitude": state[6],
                    "velocity": state[9],
                    "true_track": state[10],
                    "geo_altitude": state[13],
                    "on_ground": state[8]
                }
                
                # Basic geographical filter to ensure it's in our rough interest zone (redundant if fetch is tight, but good for safety)
                if plane["latitude"] and plane["longitude"]:
                     private_jets.append(plane)
        
        return private_jets

    def fetch(self):
        # Fetch global data (no coordinates)
        
        try:
            url = 'https://opensky-network.org/api/states/all'
            
            # Use credentials if available, otherwise anonymous (limited rate)
            user = os.getenv('USER_NAME')
            password = os.getenv('USER_PASSWORD')
            
            if user and password:
                response = requests.get(url, auth=(user, password), timeout=15)
            else:
                response = requests.get(url, timeout=15)
                
            if response.status_code == 200:
                data = response.json()
                return data.get('states', [])
            else:
                print(f"Error fetching data: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Exception in fetch: {e}")
            return []


