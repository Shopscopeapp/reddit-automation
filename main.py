"""Main pipeline: fetch Reddit aviation videos, download, generate captions."""
import argparse
from pathlib import Path

from config import VIDEOS_DIR, METADATA_DIR
from reddit_fetcher import fetch_videos, VideoPost
from video_downloader import download_video
from caption_generator import generate_caption, save_metadata


def run(
    limit: int = 10,
    caption_style: str = "engaging",
    output_videos: Path | None = None,
    output_metadata: Path | None = None,
    min_score: int = 10,
) -> tuple[list[dict], int, int]:
    """
    Run the full pipeline: fetch -> download -> caption -> save metadata.
    
    Returns (results, fetched_count, download_failed_count).
    """
    output_videos = output_videos or VIDEOS_DIR
    output_metadata = output_metadata or METADATA_DIR
    
    results = []
    fetched = 0
    download_failed = 0
    
    for post in fetch_videos(limit=limit, min_score=min_score):
        fetched += 1
        print(f"Processing: {post.title[:50]}... (r/{post.subreddit})")
        
        # Download
        video_path = download_video(post, output_videos)
        if not video_path:
            download_failed += 1
            print(f"  Skipped (download failed)")
            continue
        
        # Generate caption
        caption = generate_caption(post, style=caption_style)
        
        # Save metadata
        meta_path = save_metadata(post, caption, video_path, output_metadata)
        
        results.append({
            "post": post,
            "video_path": video_path,
            "caption": caption,
            "metadata_path": meta_path,
        })
        print(f"  Saved: {video_path.name}")
        try:
            print(f"  Caption: {caption[:60]}...")
        except UnicodeEncodeError:
            print(f"  Caption: [saved]")
    
    return results, fetched, download_failed


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
