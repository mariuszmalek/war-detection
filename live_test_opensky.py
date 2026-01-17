import sys
import os
import reverse_geocoder as rg
import json
from clients import opensky

def test_live_data():
    print("Fetching live data from OpenSky Network...")
    client = opensky.OpenskyClient()
    
    # This calls fetch() and applies the "private jet" heuristics
    planes = client.detect()
    
    total_planes = len(planes)
    print(f"Total potential private/special aircraft detected globally: {total_planes}")
    
    if total_planes == 0:
        print("No aircraft matching the criteria were found.")
        return

    # Extract coordinates for batch geocoding
    coords = [(p["latitude"], p["longitude"]) for p in planes]
    
    print("Geolocating aircraft...")
    # rg.search returns a list of dicts corresponding to the coords
    results = rg.search(coords)
    
    # Combine plane data with location data
    # Filter for planes that are actually flying (velocity > 50 m/s ~ 180 km/h) to filter out taxiing/parked
    flying_planes = []
    
    for plane, geo in zip(planes, results):
        # Velocity check: 50 m/s is roughly 100 knots. 
        # Private jets cruise much faster, but 50 filters out static/taxiing well.
        if plane["velocity"] and plane["velocity"] > 50 and not plane["on_ground"]:
            plane["country_code"] = geo.get('cc', 'Unknown')
            plane["location_name"] = geo.get('name', 'Unknown')
            plane["admin1"] = geo.get('admin1', 'Unknown')
            flying_planes.append(plane)
            
    print(f"Aircraft currently airborne (>50m/s): {len(flying_planes)}")
    
    if not flying_planes:
        print("No airborne aircraft found matching criteria.")
        return

    print("\n--- Sample of Detected Aircraft (Top 10) ---")
    # Show a mix of countries if possible
    
    # Sort by country code for nicer display
    flying_planes.sort(key=lambda x: x["country_code"])
    
    for i, p in enumerate(flying_planes[:10]):
        print(f"{i+1}. Call: {p['callsign']} | ICAO: {p['icao24']} | Loc: {p['location_name']}, {p['country_code']} | Vel: {p['velocity']} m/s")

    # Show country distribution stats
    print("\n--- Country Distribution (Top 5) ---")
    country_counts = {}
    for p in flying_planes:
        cc = p['country_code']
        country_counts[cc] = country_counts.get(cc, 0) + 1
    
    sorted_counts = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    for cc, count in sorted_counts[:5]:
        print(f"{cc}: {count} aircraft")

if __name__ == "__main__":
    test_live_data()
