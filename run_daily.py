"""Run the pipeline - use with Task Scheduler / cron for daily automation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pipeline import run
from config import VIDEOS_DIR, METADATA_DIR

if __name__ == "__main__":
    results, _, _ = run(
        limit=10,
        caption_style="engaging",
        output_videos=VIDEOS_DIR,
        output_metadata=METADATA_DIR,
        min_score=25,  # Only quality posts
    )
