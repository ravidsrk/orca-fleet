"""Per-issue comment routes (slice S1)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Comment, Issue, get_db
from app.schemas import CommentCreate, CommentRead

router = APIRouter(prefix="/issues/{issue_id}/comments", tags=["comments"])


def _require_issue(issue_id: int, db: Session) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not found")
    return issue


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(
    issue_id: int, payload: CommentCreate, db: Session = Depends(get_db)
) -> Comment:
    _require_issue(issue_id, db)
    comment = Comment(issue_id=issue_id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("", response_model=list[CommentRead])
def list_comments(issue_id: int, db: Session = Depends(get_db)) -> list[Comment]:
    _require_issue(issue_id, db)
    stmt = select(Comment).where(Comment.issue_id == issue_id).order_by(Comment.id)
    return list(db.scalars(stmt).all())
