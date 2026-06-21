# TikTok Content Automation

A weekly research assistant for finding relationship-content candidates, categorizing them, planning short-form clips, generating caption ideas, and clipping local rights-cleared video files.

## What it automates

- Finds YouTube candidates for these buckets:
  - Marriage Lessons From Famous Men
  - Why Men Don’t Commit
  - What Women Actually Want
  - Modern Dating Truths
  - Celebrity Relationship Advice
- Scores candidates by relationship-topic relevance.
- Pulls available English transcripts.
- Suggests timestamp ranges, hooks, TikTok captions, and hashtags.
- Exports weekly CSV/JSON files for review.
- Clips local video files into vertical 9:16 format.
- Exports SRT captions from available transcripts.

## Monetization safety

Use this as a research and production assistant, not as a repost bot. TikTok monetization is more likely when the final content is original or meaningfully transformed. Before clipping/uploading, confirm you have rights, permission, licensed footage, public-domain footage, Creative Commons rights, or a strong fair-use basis. Add original commentary, voiceover, analysis, edits, or on-screen framing.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your YouTube Data API key to `.env`:

```bash
YOUTUBE_API_KEY=your_key_here
```

## Generate a weekly content plan

```bash
python -m content_pipeline.cli weekly --max-per-query 5 --max-candidates 25 --max-clips-per-video 2
```

Outputs:

- `data/weekly/YYYY-MM-DD/weekly_plan.json`
- `data/weekly/YYYY-MM-DD/candidates.csv`
- `data/weekly/YYYY-MM-DD/clip_ideas.csv`

## Clip a local rights-cleared video

```bash
python -m content_pipeline.cli clip-local path/to/source.mp4 --start 42 --end 95 --output-path data/clips/example.mp4
```

## Generate SRT captions from a YouTube transcript

```bash
python -m content_pipeline.cli srt-youtube VIDEO_ID --start 42 --end 95 --output-path data/captions/example.srt
```

## Weekly workflow

1. Run the weekly planner.
2. Review `clip_ideas.csv`.
3. Check rights/permissions for the clips you want.
4. Download or import only footage you are allowed to use.
5. Use `clip-local` to cut the best segment.
6. Add original voiceover/commentary and branded text in CapCut, Premiere, or TikTok Studio.
7. Upload on a weekly schedule.
