![alt text](https://github.com/mariuszmalek/war-detection/blob/master/assets/image.png?raw=true)

# War Detection (Global Edition)

## Information
The bot analyzes global flight data obtained from opensky-network.org to detect unusual movements of private jets.

We focus on private planes (Business Jets, Ultra Long Range) to identify potential mass exodus events of high-net-worth individuals. When a significant cluster of private flights departs from a specific country within a short time window, it triggers an anomaly alert.

This system monitors the **whole world** using reverse geocoding to identify the origin of flights.

Then a message is created on Twitter about the threat. Example:
![alt text](https://github.com/mariuszmalek/war-detection/blob/master/assets/twitt.png?raw=true)


## Contributing
I'm open to any help or suggestions, I realize there are many better ways to improve this program and better ways to get this program to work properly.

## Installation
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env-clone` to `.env` and fill in your OpenSky and Twitter credentials.
3. Run the bot:
   ```
   python main.py
   ```
