from __future__ import annotations

from pathlib import Path

from moviepy.editor import VideoFileClip


class ClipError(RuntimeError):
    pass


def crop_to_vertical(video: VideoFileClip) -> VideoFileClip:
    target_ratio = 9 / 16
    current_ratio = video.w / video.h

    if current_ratio > target_ratio:
        new_width = int(video.h * target_ratio)
        x_center = video.w / 2
        return video.crop(x_center=x_center, width=new_width, height=video.h)

    new_height = int(video.w / target_ratio)
    y_center = video.h / 2
    return video.crop(y_center=y_center, width=video.w, height=new_height)


def clip_local_video(
    source_path: Path,
    output_path: Path,
    start: float,
    end: float,
    vertical: bool = True,
) -> Path:
    if not source_path.exists():
        raise ClipError(f"Source file does not exist: {source_path}")

    if end <= start:
        raise ClipError("End time must be greater than start time.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with VideoFileClip(str(source_path)) as video:
        clip = video.subclip(start, min(end, video.duration))
        if vertical:
            clip = crop_to_vertical(clip).resize(height=1920)
            if clip.w > 1080:
                clip = clip.resize(width=1080)
        clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            threads=4,
        )
        clip.close()

    return output_path
