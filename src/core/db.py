from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def _normalize_report_text_fields(report: Dict) -> Dict:
    for key in ("contract_id", "date_debut", "date_fin"):
        val = report.get(key)
        if isinstance(val, str) and val.strip().lower() in {"none", "null", ""}:
            report[key] = None
    return report


def get_report_summary_by_id(report_id: str) -> Optional[Dict]:
    """Retourne un rapport sans les entrées (rapide pour affichage/API).

    Ajoute aussi des stats dérivées SF/RF/pages réelles via agrégats SQL.
    """
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    # Agrégats type/pages sans charger toutes les entrées
    cur.execute(
        """
        SELECT type, COUNT(*) AS cnt, COALESCE(SUM(pages), 0) AS pages
        FROM fax_entries
        WHERE report_id = ?
        GROUP BY type
        """,
        (report_id,),
    )
    agg = cur.fetchall()

    cur.execute(
        "SELECT COUNT(*) AS total FROM fax_entries WHERE report_id = ?",
        (report_id,),
    )
    entries_total = int(cur.fetchone()["total"])

    conn.close()

    report = dict(row)
    _normalize_report_text_fields(report)

    fax_sf = 0
    fax_rf = 0
    pages_sf = 0
    pages_rf = 0
    for r in agg:
        t = (r["type"] or "").lower()
        if t == "send":
            fax_sf = int(r["cnt"])
            pages_sf = int(r["pages"])
        elif t == "receive":
            fax_rf = int(r["cnt"])
            pages_rf = int(r["pages"])

    report["fax_sf"] = fax_sf
    report["fax_rf"] = fax_rf
    report["pages_reelles_sf"] = pages_sf
    report["pages_reelles_rf"] = pages_rf
    report["pages_reelles_totales"] = pages_sf + pages_rf
    report["pages_envoyees"] = pages_sf
    report["pages_recues"] = pages_rf
    report["entries_total"] = entries_total

    # Compat avec champs existants
    if report.get("fax_envoyes") in (None, ""):
        report["fax_envoyes"] = fax_sf
    if report.get("fax_recus") in (None, ""):
        report["fax_recus"] = fax_rf
    if report.get("pages_totales") in (None, ""):
        report["pages_totales"] = pages_sf + pages_rf

    return report


def get_report_entries(report_id: str, offset: int = 0, limit: int = 200) -> Tuple[List[Dict], int]:
    """Retourne une page d'entrées + le total d'entrées pour un rapport."""
    offset = max(0, int(offset))
    limit = max(1, min(2000, int(limit)))

    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) AS total FROM fax_entries WHERE report_id = ?",
        (report_id,),
    )
    total = int(cur.fetchone()["total"])

    cur.execute(
        """
        SELECT id, report_id, fax_id, utilisateur, type,
               numero_original, numero_normalise, valide, pages, datetime, erreurs
        FROM fax_entries
        WHERE report_id = ?
        ORDER BY datetime ASC
        LIMIT ? OFFSET ?
        """,
        (report_id, limit, offset),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows, total


def delete_report(report_id: str) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM fax_entries WHERE report_id = ?", (report_id,))
    cur.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()


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
    # Compat: certaines routes historiques exposaient `fax_entries`
    report["entries"] = entries
    report["fax_entries"] = entries

    _normalize_report_text_fields(report)

    # Statistiques dérivées depuis les entrées (utile pour afficher pages SF/RF)
    pages_sf = 0
    pages_rf = 0
    fax_sf = 0
    fax_rf = 0
    for e in entries:
        t = (e.get("type") or "").lower()
        pages = e.get("pages") or 0
        try:
            pages = int(pages)
        except Exception:
            pages = 0

        if t == "send":
            fax_sf += 1
            pages_sf += pages
        elif t == "receive":
            fax_rf += 1
            pages_rf += pages

    report["fax_sf"] = fax_sf
    report["fax_rf"] = fax_rf
    # Compat avec champs stats/affichage
    report["fax_envoyes"] = report.get("fax_envoyes", fax_sf)
    report["fax_recus"] = report.get("fax_recus", fax_rf)

    report["pages_reelles_sf"] = pages_sf
    report["pages_reelles_rf"] = pages_rf
    report["pages_reelles_totales"] = pages_sf + pages_rf

    # Champs pages (par cohérence avec "envoyées/reçues")
    report["pages_envoyees"] = pages_sf
    report["pages_recues"] = pages_rf

    return report
