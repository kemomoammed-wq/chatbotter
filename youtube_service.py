import os
import logging
from typing import Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class YoutubeVideo(BaseModel):
    title: str
    description: str
    thumbnail_url: str
    video_url: str
    channel_title: Optional[str] = None
    published_at: Optional[str] = None


async def search_youtube_video(query: str) -> Optional[YoutubeVideo]:
    """
    Search YouTube for a single educational / tutorial-style video.
    Returns None if API key is missing, request fails, or no items.
    """
    if not YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY is not set; skipping YouTube search")
        return None

    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 1,
        "safeSearch": "moderate",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(YOUTUBE_SEARCH_URL, params=params)
            resp.raise_for_status()
    except Exception as exc:
        logger.exception(f"Error while calling YouTube API: {exc}")
        return None

    data = resp.json()
    items = data.get("items") or []
    if not items:
        return None

    item = items[0]
    video_id = item.get("id", {}).get("videoId")
    snippet = item.get("snippet") or {}

    if not video_id:
        return None

    thumbnails = snippet.get("thumbnails") or {}
    thumbnail_url = (
        (thumbnails.get("high") or {}).get("url")
        or (thumbnails.get("medium") or {}).get("url")
        or (thumbnails.get("default") or {}).get("url")
        or ""
    )

    return YoutubeVideo(
        title=snippet.get("title", ""),
        description=snippet.get("description", "") or "",
        thumbnail_url=thumbnail_url,
        video_url=f"https://www.youtube.com/watch?v={video_id}",
        channel_title=snippet.get("channelTitle"),
        published_at=snippet.get("publishedAt"),
    )


