from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .captions import write_srt
from .clipper import clip_local_video
from .discovery import DiscoveryError, discover_youtube_candidates
from .models import ClipPlan, WeeklyPlan
from .planner import plan_clips_for_candidate
from .transcripts import TranscriptError, get_youtube_transcript


app = typer.Typer(help="Weekly TikTok relationship content research and clipping assistant.")
console = Console()


def write_clip_csv(plans: list[ClipPlan], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                "category",
                "title",
                "channel",
                "url",
                "start",
                "end",
                "hook",
                "caption",
                "hashtags",
                "reason",
                "safety_notes",
            ),
        )
        writer.writeheader()
        for plan in plans:
            writer.writerow(
                {
                    "category": plan.candidate.category,
                    "title": plan.candidate.title,
                    "channel": plan.candidate.channel,
                    "url": str(plan.candidate.url),
                    "start": plan.start,
                    "end": plan.end,
                    "hook": plan.hook,
                    "caption": plan.caption,
                    "hashtags": " ".join(plan.hashtags),
                    "reason": plan.reason,
                    "safety_notes": " | ".join(plan.safety_notes),
                }
            )


def print_candidate_table(plan: WeeklyPlan) -> None:
    table = Table(title="Top Candidates")
    table.add_column("Score", justify="right")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("Channel")
    table.add_column("URL")

    for candidate in plan.candidates[:10]:
        table.add_row(
            f"{candidate.score:.1f}",
            candidate.category,
            candidate.title[:64],
            candidate.channel[:24],
            str(candidate.url),
        )

    console.print(table)


@app.command()
def weekly(
    max_per_query: int = typer.Option(5, "--max-per-query", help="YouTube results per search query."),
    max_candidates: int = typer.Option(25, "--max-candidates", help="Maximum candidates to transcript-check."),
    max_clips_per_video: int = typer.Option(2, "--max-clips-per-video", help="Maximum clip ideas per video."),
    since_days: int | None = typer.Option(None, "--since-days", help="Only search videos published in the last N days."),
    out_dir: Path = typer.Option(Path("data/weekly"), "--out-dir", help="Output directory."),
) -> None:
    load_dotenv()
    published_after = None
    if since_days is not None:
        published_after = datetime.now(timezone.utc) - timedelta(days=since_days)

    try:
        candidates = discover_youtube_candidates(max_per_query=max_per_query, published_after=published_after)
    except DiscoveryError as error:
        console.print(f"Discovery failed: {error}")
        raise typer.Exit(1) from error

    clip_plans: list[ClipPlan] = []
    for candidate in candidates[:max_candidates]:
        try:
            transcript = get_youtube_transcript(candidate.source_id)
        except TranscriptError as error:
            candidate.notes.append(f"transcript_unavailable:{error}")
            continue

        clip_plans.extend(
            plan_clips_for_candidate(
                candidate,
                transcript,
                max_clips=max_clips_per_video,
            )
        )

    plan = WeeklyPlan(candidates=candidates, clip_plans=clip_plans)
    week_dir = out_dir / datetime.now().strftime("%Y-%m-%d")
    plan.write_json(week_dir / "weekly_plan.json")
    plan.write_csv(week_dir / "candidates.csv")
    write_clip_csv(clip_plans, week_dir / "clip_ideas.csv")

    print_candidate_table(plan)
    console.print(f"Saved weekly plan to {week_dir}")
    console.print(f"Generated {len(clip_plans)} clip ideas.")


@app.command("clip-local")
def clip_local(
    source_path: Path = typer.Argument(..., help="Local source video path you have rights to use."),
    start: float = typer.Option(..., "--start", help="Start time in seconds."),
    end: float = typer.Option(..., "--end", help="End time in seconds."),
    output_path: Path = typer.Option(Path("data/clips/output.mp4"), "--output-path", help="Output MP4 path."),
    vertical: bool = typer.Option(True, "--vertical/--no-vertical", help="Crop to 9:16 vertical."),
) -> None:
    output = clip_local_video(
        source_path=source_path,
        output_path=output_path,
        start=start,
        end=end,
        vertical=vertical,
    )
    console.print(f"Saved clip to {output}")


@app.command("srt-youtube")
def srt_youtube(
    video_id: str = typer.Argument(..., help="YouTube video ID."),
    start: float = typer.Option(0.0, "--start", help="Clip start time in seconds."),
    end: float | None = typer.Option(None, "--end", help="Clip end time in seconds."),
    output_path: Path = typer.Option(Path("data/captions/captions.srt"), "--output-path", help="Output SRT path."),
) -> None:
    transcript = get_youtube_transcript(video_id)
    output = write_srt(transcript, output_path=output_path, start=start, end=end)
    console.print(f"Saved SRT captions to {output}")


if __name__ == "__main__":
    app()
