import json
from pathlib import Path

import pandas as pd

from app.services.importer import FileImporterService


def test_import_csv(tmp_path):
    importer = FileImporterService()
    sample = Path("tests/fixtures/sample.csv")
    rows, meta = importer.import_file(sample)
    assert len(rows) == 2
    assert meta["rows"] == 2
    assert rows[0]["recipient"]


def test_checksum(tmp_path):
    importer = FileImporterService()
    sample = Path("tests/fixtures/sample.csv")
    checksum = importer.compute_checksum(sample)
    assert len(checksum) == 64


def test_mapping_missing(tmp_path):
    importer = FileImporterService()
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"foo": [1]}).to_csv(bad, index=False)
    try:
        importer.import_file(bad)
    except Exception as e:
        assert "Colonnes essentielles" in str(e)
