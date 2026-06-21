from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class VideoCandidate(BaseModel):
    source: str
    source_id: str
    url: HttpUrl
    title: str
    description: str = ""
    channel: str = ""
    published_at: datetime | None = None
    category: str
    score: float = 0.0
    rights_status: str = "needs_review"
    notes: list[str] = Field(default_factory=list)


class TranscriptSegment(BaseModel):
    start: float
    duration: float
    text: str

    @property
    def end(self) -> float:
        return self.start + self.duration


class ClipPlan(BaseModel):
    candidate: VideoCandidate
    start: float
    end: float
    hook: str
    caption: str
    hashtags: list[str]
    reason: str
    safety_notes: list[str] = Field(default_factory=list)


class WeeklyPlan(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    candidates: list[VideoCandidate]
    clip_plans: list[ClipPlan]

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    def write_csv(self, path: Path) -> None:
        import csv

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=(
                    "category",
                    "score",
                    "title",
                    "channel",
                    "url",
                    "published_at",
                    "rights_status",
                    "notes",
                ),
            )
            writer.writeheader()
            for candidate in self.candidates:
                writer.writerow(
                    {
                        "category": candidate.category,
                        "score": round(candidate.score, 2),
                        "title": candidate.title,
                        "channel": candidate.channel,
                        "url": str(candidate.url),
                        "published_at": candidate.published_at.isoformat() if candidate.published_at else "",
                        "rights_status": candidate.rights_status,
                        "notes": " | ".join(candidate.notes),
                    }
                )


def model_to_dict(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")
