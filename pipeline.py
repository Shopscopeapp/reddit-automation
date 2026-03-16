"""All-in-one pipeline: fetch, download, caption. Consolidates modules to avoid import issues."""
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import requests

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    REDDIT_USER_AGENT,
    SUBREDDITS,
    VIDEOS_DIR,
    METADATA_DIR,
)


@dataclass
class VideoPost:
    """Represents a Reddit video post."""
    id: str
    title: str
    subreddit: str
    url: str
    permalink: str
    score: int
    num_comments: int
    author: str
    is_video: bool


def _is_video_post(data: dict) -> bool:
    if data.get("is_video"):
        return True
    url = data.get("url") or ""
    if "v.redd.it" in url or data.get("domain") == "v.redd.it":
        return True
    if data.get("post_hint") in ("video", "hosted:video"):
        return True
    media = data.get("media") or data.get("secure_media") or {}
    if isinstance(media, dict) and (media.get("type") == "video" or "reddit_video" in media):
        return True
    if "reddit_video" in str(media):
        return True
    for parent in data.get("crosspost_parent_list") or []:
        if _is_video_post(parent):
            return True
    return False


def _fetch_json(subreddit: str, sort: str = "hot", limit: int = 25) -> list[dict]:
    ua = REDDIT_USER_AGENT or (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    headers = {"User-Agent": ua, "Accept": "application/json"}
    params = {"limit": min(limit, 100), "raw_json": 1}
    for base in ["https://www.reddit.com", "https://old.reddit.com"]:
        try:
            r = requests.get(
                f"{base}/r/{subreddit}/{sort}.json",
                headers=headers,
                params=params,
                timeout=20,
            )
            r.raise_for_status()
            data = r.json()
            return [c["data"] for c in data.get("data", {}).get("children", [])]
        except Exception:
            continue
    return []


def fetch_videos(
    subreddits: list[str] | None = None,
    sort: str = "hot",
    limit: int = 25,
    min_score: int = 10,
) -> Generator[VideoPost, None, None]:
    subreddits = subreddits or SUBREDDITS
    seen_ids = set()
    per_sub = max(limit * 3, 50)

    for subreddit in subreddits:
        posts = _fetch_json(subreddit, sort=sort, limit=per_sub)
        for data in posts:
            if data.get("id") in seen_ids or data.get("score", 0) < min_score:
                continue
            if not _is_video_post(data):
                continue

            seen_ids.add(data["id"])
            permalink = data.get("permalink", "") or ""
            if not permalink.startswith("/"):
                permalink = "/" + permalink

            yield VideoPost(
                id=data["id"],
                title=(data.get("title") or "")[:300],
                subreddit=data.get("subreddit", subreddit),
                url=f"https://www.reddit.com{permalink}",
                permalink=permalink,
                score=data.get("score", 0),
                num_comments=data.get("num_comments", 0),
                author=data.get("author") or "[deleted]",
                is_video=True,
            )
        time.sleep(1)


def _download_video(post: VideoPost, output_dir: Path) -> Path | None:
    import yt_dlp

    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / f"{post.id}.%(ext)s")
    opts = {
        "outtmpl": template,
        "format": "best",
        "noplaylist": True,
        "no_overwrites": True,
        "quiet": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([post.url])
        for ext in [".mp4", ".webm", ".mkv"]:
            p = output_dir / f"{post.id}{ext}"
            if p.exists():
                return p
        for f in output_dir.glob(f"{post.id}.*"):
            return f
    except Exception:
        pass
    return None


def _generate_caption(post: VideoPost, style: str = "engaging") -> str:
    if not OPENAI_API_KEY:
        return f"✈️ {post.title}\n\nVia r/{post.subreddit}"

    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompts = {
        "engaging": "Write an engaging caption. Add 2-3 hashtags.",
        "professional": "Write a professional, informative caption.",
        "casual": "Write a casual caption. Include 2-3 hashtags.",
        "minimal": "Write a short caption (1-2 sentences). 2 hashtags.",
    }
    prompt = f"""Caption for aviation video. Title: {post.title}. Subreddit: r/{post.subreddit}. Upvotes: {post.score}.
{prompts.get(style, prompts["engaging"])} Output ONLY the caption, under 220 chars."""

    r = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You write aviation social media captions."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )
    return r.choices[0].message.content.strip()


def _save_metadata(post: VideoPost, caption: str, video_path: Path | None, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": post.id,
        "title": post.title,
        "subreddit": post.subreddit,
        "url": post.url,
        "score": post.score,
        "author": post.author,
        "caption": caption,
        "video_path": str(video_path) if video_path else None,
    }
    path = out_dir / f"{post.id}.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return path


def run(
    limit: int = 10,
    caption_style: str = "engaging",
    output_videos: Path | None = None,
    output_metadata: Path | None = None,
    min_score: int = 10,
) -> tuple[list[dict], int, int]:
    output_videos = output_videos or VIDEOS_DIR
    output_metadata = output_metadata or METADATA_DIR
    results = []
    fetched = 0
    download_failed = 0

    for post in fetch_videos(limit=limit, min_score=min_score):
        fetched += 1
        video_path = _download_video(post, output_videos)
        if not video_path:
            download_failed += 1
            continue

        caption = _generate_caption(post, style=caption_style)
        _save_metadata(post, caption, video_path, output_metadata)
        results.append({
            "post": post,
            "video_path": video_path,
            "caption": caption,
        })

    return results, fetched, download_failed
