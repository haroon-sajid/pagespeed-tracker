# PageSpeed Insights Tracker

Fetches Google PageSpeed metrics and logs them to Google Sheets every 4 hours.

## Setup

1. Clone the repo
2. Install dependencies:  pip install -r requirements.txt
3. Place your credentials.json in the root folder
4. Share your Google Sheet with the service account email
5. Run: python main.py start

## CLI Commands

| Command | Description |
|---|---|
| python main.py start | Start scheduler |
| python main.py add <url> | Add URL to track |
| python main.py remove <url> | Remove URL |
| python main.py list | Show all URLs |

## Assumptions
- PageSpeed API is used without an API key (free tier, 25,000 req/day)
- Both desktop and mobile are tested for each URL
- Credentials file is named credentials.json