from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Mode(str, Enum):
    walls = "walls"
    pass_through = "pass-through"


class Direction(str, Enum):
    up = "up"
    down = "down"
    left = "left"
    right = "right"


class Point(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class GameState(BaseModel):
    width: int
    height: int
    snake: list[Point]
    dir: Direction
    pendingDir: Direction
    food: Point
    score: int
    alive: bool
    mode: Mode


class User(BaseModel):
    username: str
    email: str


class ScoreEntry(BaseModel):
    username: str
    score: int
    mode: Mode
    date: str  # ISO date string


class LivePlayer(BaseModel):
    id: str
    username: str
    mode: Mode
    state: GameState


# Request schemas

class SignUpRequest(BaseModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=6)


class LogInRequest(BaseModel):
    email: str
    password: str


class SubmitScoreRequest(BaseModel):
    score: int = Field(ge=0)
    mode: Mode

