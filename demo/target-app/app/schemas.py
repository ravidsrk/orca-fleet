"""Pydantic request/response shapes (slice S1)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["open", "closed"]


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str | None = None
    status: Status = "open"
    priority: int = Field(default=2, ge=1, le=3)


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = None
    status: Status | None = None
    priority: int | None = Field(default=None, ge=1, le=3)


class IssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str | None
    status: str
    priority: int


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    issue_id: int
    body: str
