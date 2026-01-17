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

## Twitter/X Integration
This bot uses **Twitter API v2**. You need to provide the following credentials in `.env`:
- `CONSUMER_KEY` (API Key)
- `CONSUMER_SECRET` (API Key Secret)
- `ACCESS_TOKEN`
- `ACCESS_SECRET`

Make sure your App has **Read and Write** permissions.

## Deployment on Vercel
This project is configured for Vercel with Cron Jobs.

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` to deploy.
3. Set Environment Variables in Vercel Dashboard.
4. The bot will run automatically every 5 minutes via Vercel Cron.

**Note on Storage:**
By default, this bot uses a local `flight_history.json` file. On serverless platforms like Vercel, this file is **ephemeral** (it will be lost between runs).
For production use on Vercel, you should implement a persistent storage adapter (e.g., Vercel KV, MongoDB, or Google Sheets).
