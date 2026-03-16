"""Configuration for Reddit content automation."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Reddit (public JSON API - no credentials needed)
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "flight-app/1.0")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Subreddits to pull from (aviation + videos for more video content)
SUBREDDITS = [
    "aviation",
    "flying",
    "planes",
    "videos",  # Video-heavy, often has aviation
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
