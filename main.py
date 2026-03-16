"""CLI for Reddit aviation video pipeline."""
import argparse
from pathlib import Path

from config import VIDEOS_DIR, METADATA_DIR
from pipeline import run


def main():
    parser = argparse.ArgumentParser(description="Fetch aviation videos from Reddit for your flight app")
    parser.add_argument("-n", "--limit", type=int, default=5, help="Max videos to fetch (default: 5)")
    parser.add_argument("--style", default="engaging", 
                        choices=["engaging", "professional", "casual", "minimal"],
                        help="Caption style (default: engaging)")
    parser.add_argument("--min-score", type=int, default=10, help="Min upvotes (default: 10)")
    parser.add_argument("-o", "--output", type=Path, help="Output directory (default: downloaded_content)")
    
    args = parser.parse_args()
    
    output = args.output or Path("downloaded_content")
    videos_dir = output / "videos"
    metadata_dir = output / "metadata"
    
    print(f"Fetching up to {args.limit} aviation videos from Reddit...")
    print(f"Output: {output}\n")
    
    results, fetched, failed = run(
        limit=args.limit,
        caption_style=args.style,
        output_videos=videos_dir,
        output_metadata=metadata_dir,
        min_score=args.min_score,
    )
    
    print(f"\nDone! Fetched {fetched} videos, downloaded {len(results)}, {failed} failed.")
    print(f"Videos: {videos_dir}")
    print(f"Metadata + captions: {metadata_dir}")


if __name__ == "__main__":
    main()
