"""Issue CRUD routes (slice S1; list shape owned by S3 for F1)."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Comment, Issue, get_db
from app.schemas import IssueCreate, IssueRead, IssueUpdate

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=IssueRead, status_code=status.HTTP_201_CREATED)
def create_issue(payload: IssueCreate, db: Session = Depends(get_db)) -> Issue:
    issue = Issue(**payload.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.get("", response_model=list[IssueRead])
def list_issues(response: Response, db: Session = Depends(get_db)) -> list[Issue]:
    # F1 (documented flaw, S3-owned): N+1 — one ids query, then per row one
    # issue fetch plus one comments fetch (unindexed: each is a full SCAN of
    # comments; the pending 0003 index is a separate flaw, F3). Same JSON
    # shape as the straightforward read; the per-row fan-out behind the
    # X-Total-Comments header is the flaw. Do NOT fix outside a mission run
    # (oracle: app.seed docstring).
    ids = list(db.scalars(select(Issue.id).order_by(Issue.id)).all())
    issues: list[Issue] = []
    total_comments = 0
    for issue_id in ids:
        issue = db.get(Issue, issue_id)
        if issue is None:
            continue
        comments = list(
            db.scalars(
                select(Comment).where(Comment.issue_id == issue_id)
            ).all()
        )
        total_comments += len(comments)
        issues.append(issue)
    response.headers["X-Total-Comments"] = str(total_comments)
    return issues


@router.get("/{issue_id}", response_model=IssueRead)
def get_issue(issue_id: int, db: Session = Depends(get_db)) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not found")
    return issue


@router.patch("/{issue_id}", response_model=IssueRead)
def update_issue(
    issue_id: int, payload: IssueUpdate, db: Session = Depends(get_db)
) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not found")
    data = payload.model_dump(exclude_unset=True)
    for field in ("title", "status", "priority"):
        if field in data and data[field] is None:
            raise HTTPException(status_code=422, detail=f"{field} must not be null")
    for field, value in data.items():
        setattr(issue, field, value)
    db.commit()
    db.refresh(issue)
    return issue
