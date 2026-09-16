"""Server-rendered UI routes (slice S2)."""

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from app.models import Comment, Issue, get_db
from app.schemas import IssueCreate

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def list_issues_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    issues = list(db.scalars(select(Issue).order_by(Issue.id)).all())
    return templates.TemplateResponse(request, "list.html", {"issues": issues})


@router.get("/issues/new", response_class=HTMLResponse)
def new_issue_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "new.html",
        {
            "issue": None,
            "error": None,
            "action": "/issues/new",
            "submit": "Create issue",
        },
    )


@router.post("/issues/new")
def create_issue_via_form(
    request: Request,
    title: str | None = Form(None),
    body: str | None = Form(None),
    status: str = Form("open"),
    priority: int = Form(2),
    db: Session = Depends(get_db),
) -> Response:
    # title is optional at the FastAPI layer (an empty field arrives absent —
    # urlencoded `title=` parses with no value) so every bad submit re-renders
    # the form as HTML 422 via IssueCreate instead of a JSON 422.
    try:
        payload = IssueCreate(
            title=title,
            body=body or None,
            status=status,
            priority=priority,  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        message = exc.errors()[0]["msg"]
        return templates.TemplateResponse(
            request,
            "new.html",
            {
                "issue": None,
                "error": message,
                "action": "/issues/new",
                "submit": "Create issue",
            },
            status_code=422,
        )
    issue = Issue(**payload.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return RedirectResponse(url="/", status_code=303)


@router.get("/issues/{issue_id}/view", response_class=HTMLResponse)
def view_issue(
    request: Request, issue_id: int, db: Session = Depends(get_db)
) -> HTMLResponse:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not found")
    stmt = select(Comment).where(Comment.issue_id == issue_id).order_by(Comment.id)
    comments = list(db.scalars(stmt).all())
    return templates.TemplateResponse(
        request, "detail.html", {"issue": issue, "comments": comments}
    )


@router.get("/issues/{issue_id}/edit", response_class=HTMLResponse)
def edit_issue_form(
    request: Request, issue_id: int, db: Session = Depends(get_db)
) -> HTMLResponse:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not found")
    return templates.TemplateResponse(
        request,
        "edit.html",
        {
            "issue": issue,
            "error": None,
            "action": f"/issues/{issue_id}/edit",
            "submit": "Save changes",
        },
    )


@router.post("/issues/{issue_id}/edit")
def update_issue_via_form(
    request: Request,
    issue_id: int,
    title: str | None = Form(None),
    body: str | None = Form(None),
    status: str = Form("open"),
    priority: int = Form(2),
    db: Session = Depends(get_db),
) -> Response:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not found")
    # Same rule as the new form: the form always submits every field, so the
    # whole payload validates via IssueCreate and an empty title re-renders.
    try:
        payload = IssueCreate(
            title=title,
            body=body or None,
            status=status,
            priority=priority,  # type: ignore[arg-type]
        )
    except ValidationError as exc:
        message = exc.errors()[0]["msg"]
        return templates.TemplateResponse(
            request,
            "edit.html",
            {
                "issue": issue,
                "error": message,
                "action": f"/issues/{issue_id}/edit",
                "submit": "Save changes",
            },
            status_code=422,
        )
    issue.title = payload.title
    issue.body = payload.body
    issue.status = payload.status
    issue.priority = payload.priority
    db.commit()
    db.refresh(issue)
    return RedirectResponse(url=f"/issues/{issue_id}/view", status_code=303)
