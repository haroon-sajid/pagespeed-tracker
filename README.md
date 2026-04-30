# PageSpeed Insights Tracker

Automated tool that fetches Google PageSpeed Insights metrics and logs them to Google Sheets every 4 hours.

## Features

- Fetches desktop and mobile performance metrics
- Automatic retry on failure (3 attempts per request)
- Rate limiting protection
- Multithreaded URL processing
- Scheduled runs every 4 hours
- CLI for managing tracked URLs

## Prerequisites

- Python 3.8+
- Google Cloud account
- Google Sheets account

## Setup

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/haroon-sajid/pagespeed-tracker.git
cd pagespeed-tracker
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable these APIs:
   - **PageSpeed Insights API**
   - **Google Sheets API**
   - **Google Drive API**

### 3. Create Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → Service Account**
3. Fill in the details and click **Create**
4. Skip the optional steps
5. Click on the created service account
6. Go to **Keys → Add Key → Create new key**
7. Select **JSON** and click Create
8. Save the file as `credentials.json` in the project root

### 4. Create API Key

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → API Key**
3. Copy the key
4. Create a `.env` file in the project root:
   ```
   PAGESPEED_API_KEY=your_api_key_here
   ```

### 5. Create Google Sheet

1. Create a new Google Sheet
2. Rename the first sheet to "PageSpeed Results"
3. Add headers in row 1:
   ```
   URL | Date | CLS | TBT | Speed Index | LCP | FCP | Screen Type
   ```
4. Share the sheet with the `client_email` from your `credentials.json` file (as Editor)

### 6. Run the Tracker

```bash
python main.py start
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
PAGESPEED_API_KEY=your_api_key_here
```

### Default URLs

Edit the `urls` list in `main.py` to change default tracked URLs:

```python
urls = [
    "https://buildberg.co/",
    "https://example.com",
]
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `python main.py start` | Start the scheduler |
| `python main.py add <url>` | Add a URL to track |
| `python main.py remove <url>` | Remove a URL |
| `python main.py list` | List all tracked URLs |

## Metrics Tracked

| Metric | Description |
|--------|-------------|
| CLS | Cumulative Layout Shift |
| TBT | Total Blocking Time |
| LCP | Largest Contentful Paint |
| FCP | First Contentful Paint |
| Speed Index | Overall speed metric |

## Project Structure

```
pagespeed-tracker/
├── main.py              # Main application
├── credentials.json     # Google Sheets credentials (not in git)
├── .env                 # API key (not in git)
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Troubleshooting

### DNS Resolution Error

If you get `Failed to resolve 'oauth2.googleapis.com'`, try:
```powershell
ipconfig /flushdns
```

### Rate Limiting

If you hit rate limits, the script automatically retries 3 times with 5-second delays.

### API Errors

Check the `pagespeed.log` file for detailed error messages.

## License

MIT License