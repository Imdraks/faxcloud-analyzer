"""init tables

Revision ID: 0001_init
Revises:
Create Date: 2025-12-17
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "report",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=False, index=True),
        sa.Column("original_path", sa.String(), nullable=False),
        sa.Column("public_token", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("latest_run_id", sa.String(), nullable=True),
    )
    op.create_index("ix_report_public_token", "report", ["public_token"], unique=True)
    op.create_index("ix_report_created_at", "report", ["created_at"])
    op.create_table(
        "reportrun",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("report_id", sa.String(), sa.ForeignKey("report.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("stats_json", sa.Text(), nullable=False),
        sa.Column("error_summary", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "transmission",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("report_run_id", sa.String(), sa.ForeignKey("reportrun.id"), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("recipient", sa.String(), nullable=False),
        sa.Column("sender", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("status_code", sa.String(), nullable=True),
        sa.Column("error_code", sa.String(), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("raw_row", sa.Text(), nullable=False),
    )
    op.create_index("idx_trans_status", "transmission", ["status"])
    op.create_index("idx_trans_error_code", "transmission", ["error_code"])


def downgrade() -> None:
    op.drop_table("transmission")
    op.drop_table("reportrun")
    op.drop_table("report")
