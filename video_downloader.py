"""Download Reddit videos using yt-dlp."""
from pathlib import Path

import yt_dlp

from reddit_fetcher import VideoPost


def download_video(post: VideoPost, output_dir: Path) -> Path | None:
    """
    Download a Reddit video to the output directory.
    
    Returns the path to the downloaded file, or None if failed.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / f"{post.id}.%(ext)s")
    
    ydl_opts = {
        "outtmpl": output_template,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "no_overwrites": True,
        "quiet": True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([post.url])
        
        # Find the downloaded file
        for ext in [".mp4", ".webm", ".mkv"]:
            path = output_dir / f"{post.id}{ext}"
            if path.exists():
                return path
        
        for f in output_dir.glob(f"{post.id}.*"):
            return f
        
        return None
    except Exception as e:
        print(f"Download failed for {post.id}: {e}")
        return None
