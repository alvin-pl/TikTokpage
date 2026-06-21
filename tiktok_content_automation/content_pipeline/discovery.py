from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Iterable

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import VideoCandidate
from .taxonomy import CATEGORIES, Category


YOUTUBE_URL = "https://www.youtube.com/watch?v={video_id}"


class DiscoveryError(RuntimeError):
    pass


def score_candidate(title: str, description: str, category: Category) -> tuple[float, list[str]]:
    text = f"{title} {description}".lower()
    score = 0.0
    notes: list[str] = []

    for keyword in category.keywords:
        if keyword.lower() in text:
            score += 2.0
            notes.append(f"keyword:{keyword}")

    if "interview" in text or "podcast" in text:
        score += 1.5
        notes.append("format:interview_or_podcast")

    if any(word in text for word in ("wife", "marriage", "married", "commitment")):
        score += 1.25
        notes.append("relationship_core")

    if any(word in text for word in ("official music video", "trailer", "shorts compilation")):
        score -= 3.0
        notes.append("possible_low_fit")

    return score, notes


def parse_youtube_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def discover_youtube_candidates(
    max_per_query: int = 5,
    categories: Iterable[Category] = CATEGORIES,
    published_after: datetime | None = None,
) -> list[VideoCandidate]:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise DiscoveryError("Set YOUTUBE_API_KEY in your environment or .env file.")

    youtube = build("youtube", "v3", developerKey=api_key)
    candidates: dict[str, VideoCandidate] = {}

    try:
        for category in categories:
            for query in category.search_terms:
                request_kwargs = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "videoDuration": "medium",
                    "maxResults": max_per_query,
                    "order": "relevance",
                    "safeSearch": "none",
                }
                if published_after:
                    request_kwargs["publishedAfter"] = published_after.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

                response = youtube.search().list(**request_kwargs).execute()
                for item in response.get("items", []):
                    video_id = item["id"]["videoId"]
                    snippet = item.get("snippet", {})
                    title = snippet.get("title", "")
                    description = snippet.get("description", "")
                    score, notes = score_candidate(title, description, category)

                    existing = candidates.get(video_id)
                    candidate = VideoCandidate(
                        source="youtube",
                        source_id=video_id,
                        url=YOUTUBE_URL.format(video_id=video_id),
                        title=title,
                        description=description,
                        channel=snippet.get("channelTitle", ""),
                        published_at=parse_youtube_datetime(snippet.get("publishedAt")),
                        category=category.name,
                        score=score,
                        rights_status="needs_review",
                        notes=[f"query:{query}", *notes],
                    )

                    if existing is None or candidate.score > existing.score:
                        candidates[video_id] = candidate
    except HttpError as error:
        raise DiscoveryError(str(error)) from error

    return sorted(candidates.values(), key=lambda candidate: candidate.score, reverse=True)
