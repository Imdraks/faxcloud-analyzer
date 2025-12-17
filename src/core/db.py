from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from .config import settings, ensure_directories


def _connect() -> sqlite3.Connection:
    ensure_directories()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    ensure_directories()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            date_rapport TEXT,
            contract_id TEXT,
            date_debut TEXT,
            date_fin TEXT,
            total_fax INTEGER,
            fax_envoyes INTEGER,
            fax_recus INTEGER,
            pages_totales INTEGER,
            erreurs_totales INTEGER,
            taux_reussite REAL,
            qr_path TEXT,
            url_rapport TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS fax_entries (
            id TEXT PRIMARY KEY,
            report_id TEXT,
            fax_id TEXT,
            utilisateur TEXT,
            type TEXT,
            numero_original TEXT,
            numero_normalise TEXT,
            valide INTEGER,
            pages INTEGER,
            datetime TEXT,
            erreurs TEXT,
            FOREIGN KEY(report_id) REFERENCES reports(id)
        )
        """
    )
    conn.commit()
    conn.close()


def insert_report_to_db(report_id: str, report_json: Dict, qr_path: Optional[str]) -> None:
    conn = _connect()
    cur = conn.cursor()
    stats = report_json.get("statistics", {})
    cur.execute(
        """
        INSERT OR REPLACE INTO reports (
            id, date_rapport, contract_id, date_debut, date_fin,
            total_fax, fax_envoyes, fax_recus, pages_totales, erreurs_totales,
            taux_reussite, qr_path, url_rapport, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report_json.get("report_id"),
            report_json.get("timestamp"),
            report_json.get("contract_id"),
            report_json.get("date_debut"),
            report_json.get("date_fin"),
            stats.get("total_fax", 0),
            stats.get("fax_envoyes", 0),
            stats.get("fax_recus", 0),
            stats.get("pages_totales", 0),
            stats.get("erreurs_totales", 0),
            stats.get("taux_reussite", 0.0),
            qr_path,
            report_json.get("url_rapport"),
            report_json.get("timestamp"),
        ),
    )

    entries = report_json.get("entries", [])
    for entry in entries:
        cur.execute(
            """
            INSERT OR REPLACE INTO fax_entries (
                id, report_id, fax_id, utilisateur, type,
                numero_original, numero_normalise, valide, pages, datetime, erreurs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.get("id"),
                report_id,
                entry.get("fax_id"),
                entry.get("utilisateur"),
                entry.get("type"),
                entry.get("numero_original"),
                entry.get("numero_normalise"),
                1 if entry.get("valide") else 0,
                entry.get("pages"),
                entry.get("datetime"),
                json.dumps(entry.get("erreurs", [])),
            ),
        )

    conn.commit()
    conn.close()


def get_all_reports() -> List[Dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, contract_id, date_debut, date_fin, total_fax, erreurs_totales, taux_reussite
        FROM reports
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_report_by_id(report_id: str) -> Optional[Dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cur.execute("SELECT * FROM fax_entries WHERE report_id = ?", (report_id,))
    entries = [dict(r) for r in cur.fetchall()]
    conn.close()
    report = dict(row)
    report["entries"] = entries
    return report
