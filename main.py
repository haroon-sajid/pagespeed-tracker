"""
PageSpeed Insights API Integration
Fetches performance metrics and logs them to Google Sheets every 4 hours.
"""

import requests
import gspread
import schedule
import time
import logging
import argparse
import threading
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ─── CONFIG ───────────────────────────────────────────────────────────────────

CREDENTIALS_FILE = "credentials.json"
SHEET_NAME = "PageSpeed Results"
PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY")  # Get from: console.cloud.google.com → APIs & Services → Credentials → API Key

# Default URLs to test (add/remove via CLI)
urls = [
    "https://buildberg.co/",
    "https://example.com",        # bonus extra URL for multithreading demo
]

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pagespeed.log"),
        logging.StreamHandler()
    ]
)

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────

def get_sheet():
    """Authenticate and return the Google Sheet."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def add_to_sheet(sheet, data: dict):
    """Append a row of metrics to the Google Sheet."""
    row = [
        data["url"],
        data["date"],
        data["cls"],
        data["tbt"],
        data["speed_index"],
        data["lcp"],
        data["fcp"],
        data["screen_type"],
    ]
    sheet.append_row(row)
    logging.info(f"Written to sheet: {data['url']} [{data['screen_type']}]")


# ─── PAGESPEED API ────────────────────────────────────────────────────────────

def fetch_metrics(url: str, strategy: str = "desktop", max_retries: int = 3) -> dict:
    """
    Fetch PageSpeed Insights metrics for a given URL.
    strategy: 'desktop' or 'mobile'
    max_retries: number of retry attempts on failure
    """
    params = {
        "url": url,
        "strategy": strategy,
        "key": PAGESPEED_API_KEY
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(PAGESPEED_API, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Navigate to the audit metrics inside the response
            audits = data["lighthouseResult"]["audits"]
            categories = data["lighthouseResult"]

            metrics = {
                "url": url,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cls":         audits["cumulative-layout-shift"]["displayValue"],
                "tbt":         audits["total-blocking-time"]["displayValue"],
                "speed_index": audits["speed-index"]["displayValue"],
                "lcp":         audits["largest-contentful-paint"]["displayValue"],
                "fcp":         audits["first-contentful-paint"]["displayValue"],
                "screen_type": strategy,
            }

            logging.info(f"Fetched metrics for {url} [{strategy}]")
            return metrics

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout fetching {url} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait 5 seconds before retry
        except requests.exceptions.HTTPError as e:
            logging.warning(f"HTTP error for {url}: {e} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)
        except KeyError as e:
            logging.error(f"Missing key in API response for {url}: {e}")
            break  # Don't retry for key errors
        except Exception as e:
            logging.warning(f"Unexpected error for {url}: {e} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)

    logging.error(f"Failed to fetch metrics for {url} after {max_retries} attempts")
    return None


# ─── PROCESS ONE URL ─────────────────────────────────────────────────────────

def process_url(url: str, sheet):
    """Fetch both desktop and mobile metrics and write to sheet."""
    for strategy in ["desktop", "mobile"]:
        metrics = fetch_metrics(url, strategy)
        if metrics:
            add_to_sheet(sheet, metrics)
        time.sleep(2)  # Avoid rate limiting


# ─── MULTITHREADING ───────────────────────────────────────────────────────────

def run_all():
    """Run all URLs concurrently using threads."""
    logging.info(f"Starting run for {len(urls)} URLs...")
    sheet = get_sheet()
    threads = []

    for i, url in enumerate(urls):
        time.sleep(i * 3)  # Stagger thread starts by 3 seconds each
        t = threading.Thread(target=process_url, args=(url, sheet))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    logging.info("Run complete.")


# ─── SCHEDULER ───────────────────────────────────────────────────────────────

def start_scheduler():
    """Run immediately, then every 4 hours."""
    run_all()  # Run once immediately on start
    schedule.every(4).hours.do(run_all)

    logging.info("Scheduler started. Running every 4 hours.")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


# ─── CLI ──────────────────────────────────────────────────────────────────────

def cli():
    """Command-line interface to manage URLs and start the scheduler."""
    parser = argparse.ArgumentParser(description="PageSpeed Insights Tracker")
    subparsers = parser.add_subparsers(dest="command")

    # Add URL command
    add_parser = subparsers.add_parser("add", help="Add a URL to track")
    add_parser.add_argument("url", type=str, help="URL to add")

    # Remove URL command
    remove_parser = subparsers.add_parser("remove", help="Remove a URL")
    remove_parser.add_argument("url", type=str, help="URL to remove")

    # List URLs command
    subparsers.add_parser("list", help="List all tracked URLs")

    # Start scheduler command
    subparsers.add_parser("start", help="Start the scheduler")

    args = parser.parse_args()

    if args.command == "add":
        if args.url not in urls:
            urls.append(args.url)
            print(f"✅ Added: {args.url}")
        else:
            print(f"Already exists: {args.url}")

    elif args.command == "remove":
        if args.url in urls:
            urls.remove(args.url)
            print(f"🗑️ Removed: {args.url}")
        else:
            print(f"URL not found: {args.url}")

    elif args.command == "list":
        print("Tracked URLs:")
        for u in urls:
            print(f"  - {u}")

    elif args.command == "start":
        start_scheduler()

    else:
        parser.print_help()


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()