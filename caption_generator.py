"""Generate social media captions for aviation videos using AI."""
import json
from pathlib import Path

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from reddit_fetcher import VideoPost


def generate_caption(post: VideoPost, style: str = "engaging") -> str:
    """
    Generate a caption for a Reddit aviation video.
    
    Args:
        post: The video post with title, subreddit, etc.
        style: 'engaging', 'professional', 'casual', or 'minimal'
    """
    if not OPENAI_API_KEY:
        # Fallback: use title with light formatting
        return f"✈️ {post.title}\n\nVia r/{post.subreddit}"
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    style_prompts = {
        "engaging": "Write an engaging, shareable caption that hooks viewers. Include relevant aviation terms. Add 2-3 relevant hashtags at the end.",
        "professional": "Write a professional, informative caption suitable for an aviation/flight app. Keep it factual and polished.",
        "casual": "Write a casual, friendly caption. Light humor is okay. Include 2-3 hashtags.",
        "minimal": "Write a short, punchy caption (1-2 sentences max). Include 2 hashtags.",
    }
    style_instruction = style_prompts.get(style, style_prompts["engaging"])
    
    prompt = f"""Generate a social media caption for an aviation video post.

Original Reddit title: {post.title}
Subreddit: r/{post.subreddit}
Upvotes: {post.score}

{style_instruction}

Do NOT include the original title verbatim. Create something fresh. 
Keep it under 150 characters if possible, or 220 for longer captions.
Output ONLY the caption text, no quotes or extra formatting."""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a social media copywriter for an aviation/flight enthusiast app. You write engaging, accurate captions about planes and flying."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )
    
    caption = response.choices[0].message.content.strip()
    return caption


def save_metadata(post: VideoPost, caption: str, video_path: Path | None, output_dir: Path) -> Path:
    """Save post metadata and caption for later use."""
    output_dir.mkdir(parents=True, exist_ok=True)
    meta_path = output_dir / f"{post.id}.json"
    
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
    
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path
