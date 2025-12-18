from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import hashlib
from datetime import datetime, timedelta, timezone
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
            source_filename TEXT,
            source_filesize INTEGER,
            source_sha256 TEXT,
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

    # Audit log (traçabilité des actions: import/export/suppression, etc.)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            user TEXT,
            action TEXT,
            report_id TEXT,
            ip TEXT,
            user_agent TEXT,
            meta_json TEXT
        )
        """
    )
    conn.commit()

    # Migrations légères (anciens fichiers DB) : ajout des colonnes si absentes.
    # SQLite ne supporte pas IF NOT EXISTS sur ADD COLUMN partout.
    for stmt in (
        "ALTER TABLE reports ADD COLUMN source_filename TEXT",
        "ALTER TABLE reports ADD COLUMN source_filesize INTEGER",
        "ALTER TABLE reports ADD COLUMN source_sha256 TEXT",
        "ALTER TABLE fax_entries ADD COLUMN datetime_ts INTEGER",
    ):
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass

    # Indexes (best-effort) for faster filtering/pagination on large reports
    for stmt in (
        "CREATE INDEX IF NOT EXISTS idx_fax_entries_report_ts ON fax_entries(report_id, datetime_ts)",
        "CREATE INDEX IF NOT EXISTS idx_fax_entries_report_type ON fax_entries(report_id, type)",
        "CREATE INDEX IF NOT EXISTS idx_fax_entries_report_valide ON fax_entries(report_id, valide)",
        "CREATE INDEX IF NOT EXISTS idx_fax_entries_report_pages ON fax_entries(report_id, pages)",
    ):
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass

    # Backfill datetime_ts for existing rows (best-effort)
    try:
        _backfill_datetime_ts(cur)
        conn.commit()
    except Exception:
        # best-effort: do not prevent app start
        pass

    conn.close()


def _parse_datetime_to_ts(value) -> Optional[int]:
    if value is None:
        return None

    # Some pandas types stringify nicely; we just parse the string.
    text = str(value).strip()
    if not text:
        return None

    # Normalize common ISO variants
    iso_text = text.replace("Z", "+00:00")

    # Try python ISO parsing first
    try:
        dt = datetime.fromisoformat(iso_text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        pass

    # Try known common formats
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ):
        try:
            dt = datetime.strptime(text, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except Exception:
            continue

    return None


def _date_str_to_range(date_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse YYYY-MM-DD to [start_ts, end_ts_exclusive] in UTC."""
    if not date_str:
        return None, None
    s = str(date_str).strip()
    if not s:
        return None, None
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        start = d.replace(tzinfo=timezone.utc)
        end = (d + timedelta(days=1)).replace(tzinfo=timezone.utc)
        return int(start.timestamp()), int(end.timestamp())
    except Exception:
        return None, None


def _backfill_datetime_ts(cur: sqlite3.Cursor) -> None:
    # If the column doesn't exist yet, this will throw.
    cur.execute("SELECT COUNT(*) AS cnt FROM fax_entries WHERE datetime_ts IS NULL")
    missing = int(cur.fetchone()["cnt"])
    if missing <= 0:
        return

    batch_size = 5000
    while True:
        cur.execute(
            "SELECT id, datetime FROM fax_entries WHERE datetime_ts IS NULL LIMIT ?",
            (batch_size,),
        )
        rows = cur.fetchall()
        if not rows:
            break

        for r in rows:
            entry_id = r["id"]
            ts = _parse_datetime_to_ts(r["datetime"])
            if ts is None:
                # Leave NULL if unparseable
                continue
            cur.execute(
                "UPDATE fax_entries SET datetime_ts = ? WHERE id = ?",
                (ts, entry_id),
            )


def insert_audit_event(
    action: str,
    user: str = "anonymous",
    report_id: Optional[str] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    meta: Optional[Dict] = None,
) -> None:
    """Insère un événement d'audit (best-effort).

    Ne doit jamais casser l'app si l'audit échoue.
    """
    try:
        conn = _connect()
        cur = conn.cursor()
        ts = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(meta or {}, ensure_ascii=False)
        cur.execute(
            """
            INSERT INTO audit_log (ts, user, action, report_id, ip, user_agent, meta_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, user, action, report_id, ip, user_agent, meta_json),
        )
        conn.commit()
        conn.close()
    except Exception:
        # best-effort: ne pas faire tomber une export/import à cause de l'audit
        return


def list_audit_events(limit: int = 200, offset: int = 0) -> List[Dict]:
    """Retourne les événements d'audit les plus récents."""
    limit = max(1, min(1000, int(limit)))
    offset = max(0, int(offset))

    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, ts, user, action, report_id, ip, user_agent, meta_json
        FROM audit_log
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def insert_report_to_db(
    report_id: str,
    report_json: Dict,
    qr_path: Optional[str],
    source_filename: Optional[str] = None,
    source_filesize: Optional[int] = None,
    source_sha256: Optional[str] = None,
) -> None:
    conn = _connect()
    cur = conn.cursor()
    stats = report_json.get("statistics", {})
    cur.execute(
        """
        INSERT OR REPLACE INTO reports (
            id, date_rapport, contract_id, date_debut, date_fin,
            total_fax, fax_envoyes, fax_recus, pages_totales, erreurs_totales,
            taux_reussite, qr_path, url_rapport, created_at
            , source_filename, source_filesize, source_sha256
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            source_filename,
            source_filesize,
            source_sha256,
        ),
    )

    entries = report_json.get("entries", [])
    for entry in entries:
        dt_ts = _parse_datetime_to_ts(entry.get("datetime"))
        cur.execute(
            """
            INSERT OR REPLACE INTO fax_entries (
                id, report_id, fax_id, utilisateur, type,
                numero_original, numero_normalise, valide, pages, datetime, datetime_ts, erreurs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                dt_ts,
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
        SELECT id, contract_id, date_debut, date_fin, total_fax, erreurs_totales, taux_reussite,
               source_filename, source_filesize, source_sha256
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


def get_report_entries(
    report_id: str,
    offset: int = 0,
    limit: int = 200,
    *,
    entry_type: Optional[str] = None,
    valide: Optional[int] = None,
    q: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    pages_min: Optional[int] = None,
    pages_max: Optional[int] = None,
    order: str = "asc",
) -> Tuple[List[Dict], int]:
    """Retourne une page d'entrées + le total filtré d'entrées pour un rapport.

    Filtres (optionnels):
    - entry_type: "send" | "receive"
    - valide: 1 | 0
    - q: recherche sur utilisateur + numéros
    """
    offset = max(0, int(offset))
    limit = max(1, min(2000, int(limit)))

    where = ["report_id = ?"]
    params: List = [report_id]

    if entry_type:
        where.append("LOWER(type) = LOWER(?)")
        params.append(entry_type)

    if valide in (0, 1):
        where.append("valide = ?")
        params.append(int(valide))

    if q:
        q_like = f"%{q.strip()}%"
        where.append(
            "(utilisateur LIKE ? COLLATE NOCASE OR numero_normalise LIKE ? COLLATE NOCASE OR numero_original LIKE ? COLLATE NOCASE)"
        )
        params.extend([q_like, q_like, q_like])

    # Date filtering relies on datetime_ts when available.
    if date_from:
        start_ts, _ = _date_str_to_range(date_from)
        if start_ts is not None:
            where.append("datetime_ts >= ?")
            params.append(start_ts)

    if date_to:
        _, end_exclusive = _date_str_to_range(date_to)
        if end_exclusive is not None:
            where.append("datetime_ts < ?")
            params.append(end_exclusive)

    if pages_min is not None:
        try:
            pmin = int(pages_min)
            where.append("pages >= ?")
            params.append(pmin)
        except Exception:
            pass

    if pages_max is not None:
        try:
            pmax = int(pages_max)
            where.append("pages <= ?")
            params.append(pmax)
        except Exception:
            pass

    where_sql = " AND ".join(where)

    order_dir = "ASC" if str(order).lower() != "desc" else "DESC"
    order_sql = f"ORDER BY COALESCE(datetime_ts, 0) {order_dir}, datetime {order_dir}"

    conn = _connect()
    cur = conn.cursor()

    # Optimization: fetch page + total in one query using a window function.
    # If the page is empty, fall back to COUNT(*).
    cur.execute(
        f"""
        SELECT id, report_id, fax_id, utilisateur, type,
               numero_original, numero_normalise, valide, pages, datetime, erreurs,
               COUNT(*) OVER() AS total_count
        FROM fax_entries
        WHERE {where_sql}
        {order_sql}
        LIMIT ? OFFSET ?
        """,
        tuple(params + [limit, offset]),
    )
    fetched = cur.fetchall()
    if fetched:
        total = int(fetched[0]["total_count"])
        rows = [dict(r) for r in fetched]
        for r in rows:
            r.pop("total_count", None)
        conn.close()
        return rows, total

    cur.execute(
        f"SELECT COUNT(*) AS total FROM fax_entries WHERE {where_sql}",
        tuple(params),
    )
    total = int(cur.fetchone()["total"])
    conn.close()
    return [], total


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
