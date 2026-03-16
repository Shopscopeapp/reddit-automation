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

# Aviation subreddits – ordered by activity and video content
# Research: r/aviation (2.3M), r/flying (359K), r/airplanes, r/Planes, r/WeirdWings (78K),
# r/MilitaryAviation, r/Helicopters, r/combatfootage (military aviation videos)
SUBREDDITS = [
    "aviation",           # 2.3M – main aviation, photos + videos
    "flying",             # 359K – pilots, cockpit footage
    "airplanes",          # commercial/civilian aircraft
    "Planes",             # military + civilian, broad
    "WeirdWings",         # 78K – unusual aircraft
    "MilitaryAviation",   # military jets, fighters
    "Helicopters",        # rotorcraft
    "aviationmaintenance", # 113K – walkthroughs, maintenance videos
    "combatfootage",      # military aviation, cockpit footage
]

# Web app auth (optional - set APP_PASSWORD to require login)
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Output
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "downloaded_content"))
VIDEOS_DIR = OUTPUT_DIR / "videos"
METADATA_DIR = OUTPUT_DIR / "metadata"
