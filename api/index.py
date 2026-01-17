from flask import Flask, jsonify
import sys
import os

# Add parent directory to path to import core and clients
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import core

app = Flask(__name__)

@app.route('/api/cron', methods=['GET', 'POST'])
def cron_handler():
    try:
        # Run the watch logic
        # Note: On Vercel, local file storage (flight_history.json) is ephemeral.
        # For production, we must switch to a database (Redis/Postgres) or external storage.
        core.watch()
        return jsonify({"status": "success", "message": "Scan completed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "online", "message": "War Detection Bot is running"}), 200

if __name__ == '__main__':
    app.run(debug=True)
