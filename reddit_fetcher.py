"""Fetch video posts from aviation subreddits."""
import praw
from dataclasses import dataclass
from typing import Generator

from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, SUBREDDITS


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


def get_reddit_client() -> praw.Reddit:
    """Create authenticated Reddit client."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        raise ValueError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set in .env")
    
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )


def is_video_post(submission) -> bool:
    """Check if submission is a video (v.redd.it or has video media)."""
    if hasattr(submission, "is_video") and submission.is_video:
        return True
    # v.redd.it URLs
    if "v.redd.it" in getattr(submission, "url", ""):
        return True
    # Check media
    if hasattr(submission, "media") and submission.media:
        return submission.media.get("type") == "video" or "reddit_video" in str(submission.media)
    return False


def fetch_videos(
    subreddits: list[str] | None = None,
    sort: str = "hot",
    limit: int = 25,
    min_score: int = 10,
) -> Generator[VideoPost, None, None]:
    """
    Fetch video posts from aviation subreddits.
    
    Args:
        subreddits: List of subreddit names (default: config SUBREDDITS)
        sort: 'hot', 'top', 'new', or 'rising'
        limit: Max posts per subreddit
        min_score: Minimum upvotes to include
    """
    subreddits = subreddits or SUBREDDITS
    reddit = get_reddit_client()
    
    # Combine subreddits for multi-feed
    multi = "+".join(subreddits)
    sub = reddit.subreddit(multi)
    
    sort_method = getattr(sub, sort, sub.hot)
    posts = sort_method(limit=limit * len(subreddits))
    
    seen_ids = set()
    
    for submission in posts:
        if submission.id in seen_ids:
            continue
        if submission.score < min_score:
            continue
        if not is_video_post(submission):
            continue
            
        seen_ids.add(submission.id)
        
        yield VideoPost(
            id=submission.id,
            title=submission.title,
            subreddit=str(submission.subreddit),
            url=f"https://www.reddit.com{submission.permalink}",
            permalink=submission.permalink,
            score=submission.score,
            num_comments=submission.num_comments,
            author=str(submission.author) if submission.author else "[deleted]",
            is_video=True,
        )
