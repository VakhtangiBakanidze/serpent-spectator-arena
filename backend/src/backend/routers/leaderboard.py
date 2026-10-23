"""Leaderboard and score submission routers."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import ScoreDB, get_db
from ..models import Mode, ScoreEntry, SubmitScoreRequest, User

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard", response_model=list[ScoreEntry])
def get_leaderboard(
    mode: Optional[Mode] = None,
    db_session: Session = Depends(get_db),
) -> list[ScoreEntry]:
    """Return top 10 scores, optionally filtered by mode."""
    query = db_session.query(ScoreDB)
    if mode is not None:
        query = query.filter(ScoreDB.mode == mode.value)

    scores = query.order_by(ScoreDB.score.desc()).limit(10).all()
    return [
        ScoreEntry(
            username=s.username,
            score=s.score,
            mode=s.mode,  # type: ignore[arg-type]
            date=s.date,
        )
        for s in scores
    ]


@router.post("/scores", response_model=ScoreEntry, status_code=status.HTTP_201_CREATED)
def submit_score(
    body: SubmitScoreRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> ScoreEntry:
    """Submit a score (requires authentication)."""
    entry = ScoreDB(
        username=current_user.username,
        score=body.score,
        mode=body.mode.value,
        date=date.today().isoformat(),
    )
    db_session.add(entry)
    db_session.commit()
    return ScoreEntry(
        username=entry.username,
        score=entry.score,
        mode=entry.mode,  # type: ignore[arg-type]
        date=entry.date,
    )
