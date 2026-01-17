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
By default, this bot uses a local `flight_history.json` file. On serverless platforms like Vercel, this file is **ephemeral**.
To enable persistent storage, this project supports **Vercel KV (Redis)**.

### Setting up Vercel KV
1. Go to your Vercel Project Dashboard > Storage.
2. Create a new **Vercel KV** database.
3. Bind it to your project.
4. Vercel will automatically set the `KV_URL` environment variable.
5. The bot will now automatically use Redis for storing flight history.

### Alternative: Google Sheets (Free)
If you prefer a completely free alternative to Redis, you can use **Google Sheets**.

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account** and download the JSON key.
4. Encode the JSON key to Base64 (to fit in a single line):
   ```bash
   base64 -i your-key.json
   ```
5. Set environment variable `GOOGLE_SHEETS_CREDENTIALS` with the Base64 string.
6. The bot will create a sheet named `WarDetection_History` automatically.
   *(Note: You might need to share the sheet with your personal email to view it, as it is created by the service account).*

### Alternative: Upstash Redis (Free Tier)
You can also use [Upstash Redis](https://upstash.com/) which offers a generous free tier.
1. Create a database on Upstash.
2. Get the `REDIS_URL`.
3. Set `REDIS_URL` in your Vercel Environment Variables.

## Deployment Method 2: GitHub Actions (Completely Free & Recommended)
If you want to run this bot without any hosting costs and bypass Vercel's Cron limitations:

1. Push this code to a **GitHub Repository**.
2. Go to **Settings > Secrets and variables > Actions** in your repo.
3. Add the following **Repository secrets**:
   - `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_SECRET` (Twitter)
   - `OPENSKY_USERNAME`, `OPENSKY_PASSWORD` (OpenSky - Optional)
   - `GOOGLE_SHEETS_CREDENTIALS` (Base64 string) OR `REDIS_URL` (Upstash)
   
   **Important:** You MUST use Google Sheets or Redis for storage because GitHub Actions resets the filesystem on every run.

4. The bot is already configured (in `.github/workflows/scheduler.yml`) to run every ~5 minutes automatically.
5. You can check the "Actions" tab in GitHub to see the logs.
