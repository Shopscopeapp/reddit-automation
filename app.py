"""Streamlit web app for Reddit aviation video automation."""
import json
from pathlib import Path

import streamlit as st

from config import VIDEOS_DIR, METADATA_DIR, SUBREDDITS, APP_PASSWORD
from main import run

st.set_page_config(
    page_title="Flight App Content",
    page_icon="✈️",
    layout="wide",
)

# Custom styling
st.markdown("""
<style>
    .stVideo { border-radius: 8px; }
    .caption-box { 
        background: #f0f2f6; 
        padding: 1rem; 
        border-radius: 8px; 
        font-size: 0.95rem;
        margin: 0.5rem 0;
    }
    .meta-row { color: #666; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)


def load_existing_content():
    """Load metadata for already downloaded videos."""
    if not METADATA_DIR.exists():
        return []
    items = []
    for f in sorted(METADATA_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            video_path = Path(data.get("video_path", ""))
            data["video_exists"] = video_path.exists() if video_path else False
            items.append(data)
        except Exception:
            pass
    return items


def check_auth():
    """Optional password protection."""
    if not APP_PASSWORD:
        return True
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return True
    st.title("✈️ Flight App Content")
    st.caption("Enter password to continue")
    pwd = st.text_input("Password", type="password", key="pwd")
    if st.button("Login") and pwd == APP_PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    if pwd and pwd != APP_PASSWORD:
        st.error("Wrong password")
    return False


def main():
    if not check_auth():
        st.stop()
    st.title("✈️ Flight App Content")
    st.caption("Pull aviation videos from Reddit • Download • Generate captions")

    # Sidebar
    with st.sidebar:
        if APP_PASSWORD:
            if st.button("🚪 Logout"):
                st.session_state.authenticated = False
                st.rerun()
        st.header("Fetch new videos")
        limit = st.slider("Number of videos", 1, 25, 5)
        caption_style = st.selectbox(
            "Caption style",
            ["engaging", "professional", "casual", "minimal"],
            index=0,
        )
        min_score = st.number_input("Min upvotes", 0, 500, 0, step=5, help="Set to 0 to include all videos")
        st.caption("Subreddits: " + ", ".join(f"r/{s}" for s in SUBREDDITS[:4]) + "...")

        fetch_clicked = st.button("🚀 Fetch videos", type="primary", use_container_width=True)

    # Main content
    if fetch_clicked:
        with st.spinner("Fetching from Reddit, downloading, generating captions..."):
            try:
                results = run(
                    limit=limit,
                    caption_style=caption_style,
                    output_videos=VIDEOS_DIR,
                    output_metadata=METADATA_DIR,
                    min_score=min_score,
                )
                if results:
                    st.success(f"Downloaded {len(results)} videos! Scroll down to view.")
                    st.rerun()
                else:
                    st.warning(
                        "No videos found. Try: set Min upvotes to 0, or increase the number of videos. "
                        "If running on Streamlit Cloud, downloads may fail – try running locally."
                    )
            except Exception as e:
                st.error(f"Error: {e}")

    # Browse existing content
    st.divider()
    st.subheader("Downloaded content")

    items = load_existing_content()
    if not items:
        st.info("No content yet. Use the sidebar to fetch videos from Reddit.")
        return

    # Filter to only show items with existing videos
    items_with_video = [i for i in items if i.get("video_exists")]
    if not items_with_video:
        st.warning("Metadata found but video files are missing. Run a fetch to download.")
        return

    for item in items_with_video:
        video_path = Path(item["video_path"])
        if not video_path.exists():
            continue

        with st.expander(f"**{item['title'][:60]}...** • r/{item['subreddit']} • {item['score']} ↑", expanded=False):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.video(str(video_path))
            with col2:
                st.markdown("**Caption**")
                st.markdown(f'<div class="caption-box">{item["caption"]}</div>', unsafe_allow_html=True)
                st.download_button(
                    "📋 Download caption",
                    data=item["caption"],
                    file_name=f"{item['id']}_caption.txt",
                    mime="text/plain",
                    key=f"cap_{item['id']}",
                )
                st.markdown(f'<div class="meta-row">Source: <a href="{item["url"]}" target="_blank">{item["url"]}</a></div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download video",
                    data=video_path.read_bytes(),
                    file_name=video_path.name,
                    mime="video/mp4",
                    key=f"dl_{item['id']}",
                )


if __name__ == "__main__":
    main()
