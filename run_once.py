# -*- coding: utf-8 -*-
import core
import sys

# Single run script for GitHub Actions / Cron
if __name__ == "__main__":
    print("Starting single scan execution...")
    try:
        core.watch()
        print("Scan completed successfully.")
    except Exception as e:
        print(f"Scan failed: {e}")
        sys.exit(1)
