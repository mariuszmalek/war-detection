import sys
from unittest.mock import MagicMock

# Mock tweepy before importing clients.twitter
sys.modules["tweepy"] = MagicMock()
sys.modules["schedule"] = MagicMock()
# gspread is not used in core anymore, but if it were:
sys.modules["gspread"] = MagicMock()

import unittest
from unittest.mock import patch
import core
import os
import json

class TestCore(unittest.TestCase):
    
    def setUp(self):
        # Clean up history file before tests
        if os.path.exists("flight_history.json"):
            os.remove("flight_history.json")

    def tearDown(self):
        if os.path.exists("flight_history.json"):
            os.remove("flight_history.json")

    def test_get_origin_country(self):
        # Warsaw, Poland
        self.assertEqual(core.get_origin_country(52.2297, 21.0122), "Poland")
        # Prague, Czechia
        self.assertEqual(core.get_origin_country(50.0755, 14.4378), "Czechia")
        # Berlin, Germany (Should be None as it's outside defined regions)
        self.assertIsNone(core.get_origin_country(52.5200, 13.4050))
        
    @patch('clients.opensky.OpenskyClient')
    @patch('clients.twitter.TwitterClient')
    def test_watch_alert_trigger(self, mock_twitter, mock_opensky):
        # Setup Mock OpenSky to return 6 private jets exiting Poland
        # Needs to exceed ALERT_THRESHOLD (5)
        
        mock_instance = mock_opensky.return_value
        
        # Create 6 planes leaving Poland heading West (Track 270)
        planes = []
        for i in range(6):
            planes.append({
                "icao24": f"a{i}b{i}c{i}",
                "callsign": f"PVT{i}",
                "origin_country": "Poland",
                "latitude": 52.0,
                "longitude": 20.0,
                "velocity": 200, # moving
                "true_track": 270, # West
                "geo_altitude": 10000,
                "on_ground": False
            })
            
        mock_instance.detect.return_value = planes
        
        # Run watch
        core.watch()
        
        # Check if history file was created and has 6 entries
        with open("flight_history.json", 'r') as f:
            history = json.load(f)
        self.assertEqual(len(history), 6)
        
        # Check if Twitter alert was sent
        mock_twitter_instance = mock_twitter.return_value
        self.assertTrue(mock_twitter_instance.post.called)
        
    @patch('clients.opensky.OpenskyClient')
    @patch('clients.twitter.TwitterClient')
    def test_watch_no_alert(self, mock_twitter, mock_opensky):
        # Setup Mock OpenSky to return 1 private jet
        mock_instance = mock_opensky.return_value
        planes = [{
            "icao24": "aabbcc",
            "callsign": "PVT1",
            "origin_country": "Poland",
            "latitude": 52.0,
            "longitude": 20.0,
            "velocity": 200,
            "true_track": 270,
            "geo_altitude": 10000,
            "on_ground": False
        }]
        mock_instance.detect.return_value = planes
        
        core.watch()
        
        # Check history
        with open("flight_history.json", 'r') as f:
            history = json.load(f)
        self.assertEqual(len(history), 1)
        
        # Check NO Twitter alert
        mock_twitter_instance = mock_twitter.return_value
        self.assertFalse(mock_twitter_instance.post.called)

if __name__ == '__main__':
    unittest.main()
