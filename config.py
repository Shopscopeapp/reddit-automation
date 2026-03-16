"""Configuration for Reddit content automation."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Reddit
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "flight-app-content-bot/1.0")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Aviation subreddits to pull from
SUBREDDITS = [
    "aviation",
    "flying",
    "planes",
    "aviationpics",
    "MilitaryAviation",
    "WeirdWings",
    "airplanes",
]

# Web app auth (optional - set APP_PASSWORD to require login)
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Output
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "downloaded_content"))
VIDEOS_DIR = OUTPUT_DIR / "videos"
METADATA_DIR = OUTPUT_DIR / "metadata"
