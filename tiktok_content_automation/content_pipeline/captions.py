from __future__ import annotations

from pathlib import Path

from .models import TranscriptSegment


def format_srt_timestamp(seconds: float) -> str:
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def write_srt(
    segments: list[TranscriptSegment],
    output_path: Path,
    start: float = 0.0,
    end: float | None = None,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    selected = [segment for segment in segments if segment.end >= start and (end is None or segment.start <= end)]

    blocks: list[str] = []
    for index, segment in enumerate(selected, start=1):
        local_start = max(0.0, segment.start - start)
        local_end = max(local_start + 0.1, segment.end - start)
        blocks.append(
            "\n".join(
                (
                    str(index),
                    f"{format_srt_timestamp(local_start)} --> {format_srt_timestamp(local_end)}",
                    segment.text,
                )
            )
        )

    output_path.write_text("\n\n".join(blocks), encoding="utf-8")
    return output_path
