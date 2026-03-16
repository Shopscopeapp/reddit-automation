# Reddit Aviation Video Automation

Automatically pull aviation-related videos from Reddit for your flight app. Fetches from aviation subreddits, downloads videos, and generates AI captions.

## Setup

### 1. Install dependencies

Using a virtual environment (recommended on Windows to avoid permission issues):

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

Or without venv: `pip install -r requirements.txt`

**Note:** [yt-dlp](https://github.com/yt-dlp/yt-dlp) handles Reddit's v.redd.it format (video + audio merge) automatically.

### 2. Reddit API credentials

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "create another app..."
3. Choose "script", add name and redirect URI (e.g. `http://localhost:8080`)
4. Copy the **client ID** (under the app name) and **secret**

### 3. OpenAI API (for captions)

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. If you skip this, captions will fall back to the Reddit title with light formatting

### 4. Configure

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=flight-app-content-bot/1.0
OPENAI_API_KEY=your_openai_key
```

## Web app (recommended – no database)

```bash
.\venv\Scripts\Activate.ps1   # if using venv
streamlit run app.py
```

Opens at http://localhost:8501. Everything runs locally – videos go to `downloaded_content/`, no database or cloud setup.

**Optional:** Set `APP_PASSWORD` in `.env` to require a login.

**Share with co-founder on same WiFi:**
```bash
streamlit run app.py --server.address 0.0.0.0
```
Others can open `http://YOUR_IP:8501` (e.g. `http://192.168.1.5:8501`).

**Deploy remotely (still no database):**
- [Streamlit Community Cloud](https://share.streamlit.io) – free, connect GitHub, add secrets
- [Railway](https://railway.app) – free tier, persistent storage

Both use your existing `.env` secrets (Reddit, OpenAI). No Supabase or database required.

## CLI usage

```bash
# Fetch 5 videos (default), engaging captions
python main.py

# Fetch 20 videos, professional captions
python main.py -n 20 --style professional

# Only high-engagement posts (50+ upvotes)
python main.py -n 10 --min-score 50

# Custom output directory
python main.py -o ./my_content
```

## Output structure

```
downloaded_content/
├── videos/           # .mp4 files named by Reddit post ID
│   ├── abc123.mp4
│   └── xyz789.mp4
└── metadata/        # JSON with caption, title, subreddit, etc.
    ├── abc123.json
    └── xyz789.json
```

Each metadata file includes:
- `caption` – AI-generated caption for posting
- `title` – Original Reddit title
- `subreddit` – Source subreddit
- `url` – Reddit permalink
- `video_path` – Local path to downloaded video

## Subreddits (configurable in `config.py`)

- r/aviation
- r/flying
- r/planes
- r/aviationpics
- r/MilitaryAviation
- r/WeirdWings
- r/airplanes

## Caption styles

| Style        | Use case                          |
|-------------|------------------------------------|
| `engaging`  | Social posts, shareable content    |
| `professional` | App feed, curated content      |
| `casual`    | Community feel, light tone         |
| `minimal`   | Short, punchy captions             |

## Integration with your flight app

Use the metadata JSON files to:

1. **Schedule posts** – Read `caption` and `video_path` for your posting queue
2. **Attribution** – Include `subreddit` and `url` in your UI
3. **Filtering** – Use `score` to prioritize high-engagement content

Example:

```python
import json
from pathlib import Path

for meta_file in Path("downloaded_content/metadata").glob("*.json"):
    data = json.loads(meta_file.read_text())
    # data["caption"], data["video_path"], data["url"], etc.
```
