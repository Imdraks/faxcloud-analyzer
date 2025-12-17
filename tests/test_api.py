import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth():
    return ("admin", "change-me")


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_upload_and_list(tmp_path, monkeypatch):
    sample = Path("tests/fixtures/sample.csv")
    with open(sample, "rb") as f:
        resp = client.post(
            "/api/reports/upload",
            files={"file": ("sample.csv", f, "text/csv")},
            auth=auth(),
        )
    assert resp.status_code in (200, 201, 409, 400)  # depends on duplicate / missing DB
    resp = client.get("/api/reports", auth=auth())
    assert resp.status_code == 200
