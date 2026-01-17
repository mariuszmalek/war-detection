import sys
from unittest.mock import MagicMock

# Mock modules
sys.modules["tweepy"] = MagicMock()
sys.modules["schedule"] = MagicMock()
sys.modules["reverse_geocoder"] = MagicMock()
sys.modules["redis"] = MagicMock()
sys.modules["gspread"] = MagicMock()
sys.modules["google.oauth2.service_account"] = MagicMock()

import unittest
from unittest.mock import patch
import core
import os
import json

class TestCore(unittest.TestCase):
    
    def setUp(self):
        # Force local storage by mocking env vars or client getters
        # But patching them in test methods is cleaner.
        if os.path.exists("flight_history.json"):
            os.remove("flight_history.json")

    def tearDown(self):
        if os.path.exists("flight_history.json"):
            os.remove("flight_history.json")

    @patch('core.get_gsheet_client', return_value=None)
    @patch('core.get_redis_client', return_value=None)
    @patch('clients.opensky.OpenskyClient')
    @patch('clients.twitter.TwitterClient')
    @patch('reverse_geocoder.search')
    def test_watch_global_alert(self, mock_rg, mock_twitter, mock_opensky, mock_redis, mock_gsheet):
        # Setup: 6 planes in Poland (PL)
        mock_instance = mock_opensky.return_value
        planes = []
        for i in range(6):
            planes.append({
                "icao24": f"pl{i}",
                "callsign": f"PVT{i}",
                "origin_country": "Poland", # OpenSky field, ignored by our new logic
                "latitude": 52.0 + (i*0.01),
                "longitude": 21.0,
                "velocity": 200,
                "true_track": 270,
                "geo_altitude": 10000,
                "on_ground": False
            })
        
        mock_instance.detect.return_value = planes
        
        # Mock Reverse Geocoder response
        # It returns a list of dicts, one per coordinate
        # We expect 6 results, all Poland
        mock_rg.return_value = [{'cc': 'PL', 'admin1': 'Masovian Voivodeship', 'name': 'Warsaw'}] * 6
        
        # Run
        core.watch()
        
        # Verify
        with open("flight_history.json", 'r') as f:
            history = json.load(f)
        self.assertEqual(len(history), 6)
        
        # Check Alert
        mock_twitter_instance = mock_twitter.return_value
        self.assertTrue(mock_twitter_instance.post.called)
        
        # Check Alert Content
        args, _ = mock_twitter_instance.post.call_args
        self.assertIn("PL", args[0]) # Country code should be in the message
        self.assertIn("Global Anomaly", args[0])

    @patch('core.get_gsheet_client', return_value=None)
    @patch('core.get_redis_client', return_value=None)
    @patch('clients.opensky.OpenskyClient')
    @patch('clients.twitter.TwitterClient')
    @patch('reverse_geocoder.search')
    def test_watch_mixed_countries_no_alert(self, mock_rg, mock_twitter, mock_opensky, mock_redis, mock_gsheet):
        # Setup: 3 planes in PL, 3 in US. Threshold is 5 per country.
        mock_instance = mock_opensky.return_value
        planes = []
        # 3 PL
        for i in range(3):
            planes.append({
                "icao24": f"pl{i}",
                "callsign": f"PVT{i}",
                "latitude": 52.0,
                "longitude": 21.0,
                "velocity": 200, "true_track": 0, "geo_altitude": 100, "on_ground": False
            })
        # 3 US
        for i in range(3):
            planes.append({
                "icao24": f"us{i}",
                "callsign": f"PVT_US{i}",
                "latitude": 40.0,
                "longitude": -74.0,
                "velocity": 200, "true_track": 0, "geo_altitude": 100, "on_ground": False
            })
            
        mock_instance.detect.return_value = planes
        
        # Mock RG: first 3 PL, next 3 US
        mock_rg.return_value = [{'cc': 'PL'}] * 3 + [{'cc': 'US'}] * 3
        
        core.watch()
        
        # History should have 6 items
        with open("flight_history.json", 'r') as f:
            history = json.load(f)
        self.assertEqual(len(history), 6)
        
        # Alert? NO. Max count per country is 3, Threshold is 5.
        mock_twitter_instance = mock_twitter.return_value
        self.assertFalse(mock_twitter_instance.post.called)

if __name__ == '__main__':
    unittest.main()
