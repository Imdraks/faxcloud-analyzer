import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Index, String, Text
from sqlmodel import Field, SQLModel, Relationship


class Report(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    filename: str
    checksum: str = Field(index=True)
    original_path: str
    public_token: str = Field(default_factory=lambda: uuid.uuid4().hex, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    latest_run_id: Optional[str] = Field(default=None, foreign_key="reportrun.id")

    runs: list["ReportRun"] = Relationship(back_populates="report")


class ReportRun(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    report_id: str = Field(foreign_key="report.id", index=True)
    status: str = Field(default="completed")
    stats_json: str = Field(sa_column=Column(Text))
    error_summary: str = Field(default="{}", sa_column=Column(Text))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    report: Report = Relationship(back_populates="runs")
    transmissions: list["Transmission"] = Relationship(back_populates="run")


class Transmission(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    report_run_id: str = Field(foreign_key="reportrun.id", index=True)
    sent_at: datetime
    recipient: str
    sender: Optional[str] = None
    status: str
    status_code: Optional[str] = None
    error_code: Optional[str] = None
    pages: Optional[int] = None
    duration_seconds: Optional[int] = None
    raw_row: str = Field(sa_column=Column(Text))

    run: ReportRun = Relationship(back_populates="transmissions")


Index("idx_trans_status", Transmission.status)
Index("idx_trans_error_code", Transmission.error_code)
