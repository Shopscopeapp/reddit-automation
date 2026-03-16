"""Fetch video posts from aviation subreddits."""
import time
from dataclasses import dataclass
from typing import Generator

import requests

from config import REDDIT_USER_AGENT, SUBREDDITS


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
    """Check if post data represents a video."""
    if data.get("is_video"):
        return True
    url = data.get("url") or ""
    if "v.redd.it" in url:
        return True
    if data.get("domain") == "v.redd.it":
        return True
    if data.get("post_hint") in ("video", "hosted:video"):
        return True
    media = data.get("media") or data.get("secure_media") or {}
    if isinstance(media, dict):
        if media.get("type") == "video":
            return True
        if "reddit_video" in media:
            return True
    if "reddit_video" in str(media):
        return True
    # Crossposts: check crosspost_parent_list
    for parent in data.get("crosspost_parent_list") or []:
        if _is_video_post(parent):
            return True
    return False


def _fetch_json(subreddit: str, sort: str = "hot", limit: int = 25) -> list[dict]:
    """Fetch posts from subreddit via Reddit's public JSON API (no auth required)."""
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    headers = {"User-Agent": REDDIT_USER_AGENT or "flight-app/1.0"}
    params = {"limit": min(limit, 100), "raw_json": 1}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return [c["data"] for c in data.get("data", {}).get("children", [])]
    except Exception as e:
        print(f"  Fetch failed for r/{subreddit}: {e}")
        return []


def fetch_videos(
    subreddits: list[str] | None = None,
    sort: str = "hot",
    limit: int = 25,
    min_score: int = 10,
) -> Generator[VideoPost, None, None]:
    """
    Fetch video posts from aviation subreddits.
    Uses Reddit's public JSON API - no API credentials required.
    """
    subreddits = subreddits or SUBREDDITS
    seen_ids = set()
    per_sub = max(limit * 3, 50)  # Fetch more to find enough videos

    for subreddit in subreddits:
        posts = _fetch_json(subreddit, sort=sort, limit=per_sub)
        for data in posts:
            if data.get("id") in seen_ids:
                continue
            if data.get("score", 0) < min_score:
                continue
            if not _is_video_post(data):
                continue

            seen_ids.add(data["id"])
            permalink = data.get("permalink", "")
            if not permalink.startswith("/"):
                permalink = "/" + permalink

            yield VideoPost(
                id=data["id"],
                title=data.get("title", "")[:300],
                subreddit=data.get("subreddit", subreddit),
                url=f"https://www.reddit.com{permalink}",
                permalink=permalink,
                score=data.get("score", 0),
                num_comments=data.get("num_comments", 0),
                author=data.get("author") or "[deleted]",
                is_video=True,
            )

        time.sleep(1)  # Be nice to Reddit's servers
