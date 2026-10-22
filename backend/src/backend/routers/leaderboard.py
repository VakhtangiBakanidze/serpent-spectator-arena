"""Leaderboard and score submission routers."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, status

from .. import database as db
from ..auth import get_current_user
from ..models import Mode, ScoreEntry, SubmitScoreRequest, User

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard", response_model=list[ScoreEntry])
def get_leaderboard(mode: Optional[Mode] = None) -> list[ScoreEntry]:
    """Return top 10 scores, optionally filtered by mode."""
    filtered = db.scores
    if mode is not None:
        filtered = [s for s in db.scores if s["mode"] == mode.value]

    sorted_scores = sorted(filtered, key=lambda s: s["score"], reverse=True)
    top10 = sorted_scores[:10]
    return [ScoreEntry(**s) for s in top10]


@router.post("/scores", response_model=ScoreEntry, status_code=status.HTTP_201_CREATED)
def submit_score(
    body: SubmitScoreRequest,
    current_user: User = Depends(get_current_user),
) -> ScoreEntry:
    """Submit a score (requires authentication)."""
    entry = {
        "username": current_user.username,
        "score": body.score,
        "mode": body.mode.value,
        "date": date.today().isoformat(),
    }
    db.scores.append(entry)
    return ScoreEntry(**entry)
