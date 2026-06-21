from __future__ import annotations

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled, YouTubeTranscriptApi

from .models import TranscriptSegment


class TranscriptError(RuntimeError):
    pass


def get_youtube_transcript(video_id: str) -> list[TranscriptSegment]:
    try:
        raw_segments = YouTubeTranscriptApi.get_transcript(video_id, languages=("en",))
    except (NoTranscriptFound, TranscriptsDisabled) as error:
        raise TranscriptError(f"No usable English transcript for {video_id}.") from error
    except Exception as error:
        raise TranscriptError(str(error)) from error

    return [
        TranscriptSegment(
            start=float(segment["start"]),
            duration=float(segment.get("duration", 0.0)),
            text=str(segment["text"]).replace("\n", " ").strip(),
        )
        for segment in raw_segments
        if str(segment.get("text", "")).strip()
    ]
