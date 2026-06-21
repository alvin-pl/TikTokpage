from __future__ import annotations

import re

from .models import ClipPlan, TranscriptSegment, VideoCandidate
from .taxonomy import CATEGORY_BY_NAME


VIRAL_PHRASES = (
    "the truth",
    "most people",
    "never",
    "always",
    "why",
    "because",
    "marriage",
    "wife",
    "women",
    "men",
    "respect",
    "single",
    "commit",
    "loyal",
    "love",
)


CATEGORY_HASHTAGS = {
    "Marriage Lessons From Famous Men": ["#marriage", "#relationshipadvice", "#commitment", "#love"],
    "Why Men Don’t Commit": ["#dating", "#relationshiptalk", "#commitment", "#moderndating"],
    "What Women Actually Want": ["#women", "#respect", "#relationshipadvice", "#dating"],
    "Modern Dating Truths": ["#moderndating", "#datingadvice", "#relationships", "#truth"],
    "Celebrity Relationship Advice": ["#celebrity", "#relationshipadvice", "#love", "#marriage"],
}


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def segment_text_score(text: str, category: str) -> float:
    lowered = text.lower()
    score = 0.0
    category_config = CATEGORY_BY_NAME.get(category)

    for phrase in VIRAL_PHRASES:
        if phrase in lowered:
            score += 1.0

    if category_config:
        for keyword in category_config.keywords:
            if keyword.lower() in lowered:
                score += 1.5

    if "?" in text:
        score += 0.75

    word_count = len(text.split())
    if 45 <= word_count <= 140:
        score += 2.0
    elif word_count < 20:
        score -= 1.5

    return score


def build_windows(segments: list[TranscriptSegment], min_seconds: int, max_seconds: int) -> list[tuple[float, float, str]]:
    windows: list[tuple[float, float, str]] = []
    for index, segment in enumerate(segments):
        start = segment.start
        collected = []
        end = segment.end

        for next_segment in segments[index:]:
            end = next_segment.end
            collected.append(next_segment.text)
            duration = end - start

            if duration > max_seconds:
                break
            if duration >= min_seconds:
                windows.append((start, end, normalize_space(" ".join(collected))))

    return windows


def hook_from_text(text: str, fallback_category: str) -> str:
    cleaned = normalize_space(text)
    first_sentence = re.split(r"(?<=[.!?])\s+", cleaned)[0]
    words = first_sentence.split()

    if len(words) >= 5:
        return normalize_space(" ".join(words[:12])).rstrip(".,")

    if fallback_category == "Why Men Don’t Commit":
        return "This explains why some men avoid commitment"
    if fallback_category == "What Women Actually Want":
        return "This is what women actually want"
    if fallback_category == "Marriage Lessons From Famous Men":
        return "This is a marriage lesson people miss"
    if fallback_category == "Celebrity Relationship Advice":
        return "This celebrity gave real relationship advice"
    return "This is a modern dating truth"


def caption_from_plan(candidate: VideoCandidate, hook: str) -> str:
    question = "Do you agree?"
    if candidate.category == "Marriage Lessons From Famous Men":
        question = "Is this what makes marriage last?"
    elif candidate.category == "Why Men Don’t Commit":
        question = "Is this why men avoid commitment?"
    elif candidate.category == "What Women Actually Want":
        question = "Is this what women really want?"
    elif candidate.category == "Modern Dating Truths":
        question = "Is modern dating broken?"

    return f"{hook}. {question}"


def plan_clips_for_candidate(
    candidate: VideoCandidate,
    transcript: list[TranscriptSegment],
    min_seconds: int = 20,
    max_seconds: int = 60,
    max_clips: int = 2,
) -> list[ClipPlan]:
    windows = build_windows(transcript, min_seconds=min_seconds, max_seconds=max_seconds)
    scored = sorted(
        ((segment_text_score(text, candidate.category), start, end, text) for start, end, text in windows),
        key=lambda item: item[0],
        reverse=True,
    )

    plans: list[ClipPlan] = []
    for score, start, end, text in scored[:max_clips]:
        hook = hook_from_text(text, candidate.category)
        plans.append(
            ClipPlan(
                candidate=candidate,
                start=round(start, 2),
                end=round(end, 2),
                hook=hook,
                caption=caption_from_plan(candidate, hook),
                hashtags=CATEGORY_HASHTAGS.get(candidate.category, ["#relationships", "#dating", "#love"]),
                reason=f"Transcript window score {score:.2f}: {text[:240]}",
                safety_notes=[
                    "Confirm you have rights/permission or a fair-use basis before clipping.",
                    "Add original commentary, voiceover, or analysis to improve monetization eligibility.",
                ],
            )
        )

    return plans
