"""add index on comments.issue_id (slice S4; FROZEN PENDING — see FLAWS.md F3).

F3: this revision is generated but NOT applied at freeze. Fixture boot
(app/seed.py ensure_migrated) pins `alembic upgrade 0002`, so `alembic current`
on a booted DB reads 0002 while `alembic heads` shows 0003. Applying it is a
migrate-it mission run, not this build.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_comments_issue_id", "comments", ["issue_id"])


def downgrade() -> None:
    op.drop_index("ix_comments_issue_id", table_name="comments")
