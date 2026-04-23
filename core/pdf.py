from __future__ import annotations

from datetime import datetime
from pathlib import Path


def _l(text: str) -> str:
    subs = {
        "\u2014": "-", "\u2013": "-", "\u2012": "-",
        "\u2192": "->", "\u2190": "<-", "\u2194": "<->",
        "\u2026": "...", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
    }
    return "".join(subs.get(ch, ch if ord(ch) <= 255 else "?") for ch in text)


def _fmt(value: str) -> str:
    try:
        n = int(float(value.replace(",", ".")))
        return f"{n:,}".replace(",", " ")
    except Exception:
        return value


def build_report_pdf(report: dict) -> bytes:
    from fpdf import FPDF

    stats = report.get("statistics") or {}

    def get(key: str, default: str = "-") -> str:
        v = report.get(key)
        if v is None:
            v = stats.get(key)
        if v is None or str(v).strip() in ("", "None", "null"):
            return default
        return _l(str(v))

    def get_num(key: str, default: str = "-") -> str:
        v = get(key, default)
        return _fmt(v) if v != default else default

    BLUE   = (41,  98, 255)
    DARK   = (30,  30,  30)
    MUTED  = (120, 120, 130)
    LIGHT  = (245, 246, 250)
    WHITE  = (255, 255, 255)
    RED    = (220,  38,  38)
    GREEN  = (22,  163,  74)
    ORANGE = (200, 120,   0)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 0, 210, 32, "F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_y(6)
    pdf.cell(0, 12, "FaxCloud Analyzer", align="C")
    pdf.ln(11)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(200, 210, 255)
    pdf.cell(0, 5, "Rapport d'analyse FAX", align="C")
    pdf.ln(16)

    pdf.set_text_color(*DARK)
    contract  = get("contract_id", "Non defini")
    date_deb  = get("date_debut", "-")
    date_fin  = get("date_fin",   "-")
    ref       = _l(str(report.get("report_id", ""))[:8])
    timestamp = get("timestamp", "")
    try:
        dt = datetime.fromisoformat(timestamp.replace(".", "T")[:19])
        timestamp = dt.strftime("%d/%m/%Y a %H:%M")
    except Exception:
        pass

    y_meta = pdf.get_y()
    pdf.set_fill_color(*LIGHT)
    pdf.rect(10, y_meta, 190, 34, "F")

    def meta_line(label: str, value: str) -> None:
        pdf.set_x(16)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(44, 7, _l(label), border=0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, _l(value), border=0, ln=True)

    pdf.set_y(y_meta + 3)
    meta_line("Contrat :", contract)
    meta_line("Periode :", f"{date_deb}  ->  {date_fin}")
    meta_line("Genere le :", f"{timestamp}   [ref: {ref}]")
    pdf.ln(10)

    def section_title(text: str) -> None:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BLUE)
        pdf.set_x(10)
        pdf.cell(0, 7, _l(text.upper()), ln=True)
        pdf.set_draw_color(*BLUE)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.set_text_color(*DARK)
        pdf.set_line_width(0.2)
        pdf.ln(2)

    def stat_row(label: str, value: str, fill: bool = False,
                 indent: int = 0, vcolor: tuple | None = None,
                 bold: bool = False) -> None:
        pdf.set_fill_color(*(LIGHT if fill else WHITE))
        pdf.set_x(10)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(105, 7, _l("    " * indent + label), border=0, fill=True)
        pdf.set_font("Helvetica", "B" if (bold or vcolor) else "", 10)
        if vcolor:
            pdf.set_text_color(*vcolor)
        pdf.cell(85, 7, _l(value), border=0, fill=True, align="R", ln=True)
        pdf.set_text_color(*DARK)

    section_title("Statistiques globales")

    total   = get_num("total_fax")
    sf      = get_num("fax_envoyes")
    rf      = get_num("fax_recus")
    p_tot   = get_num("pages_totales")
    p_sf    = get_num("pages_envoyees")
    p_rf    = get_num("pages_recues")
    erreurs = get_num("erreurs_totales")
    taux_s  = get("taux_reussite")

    stat_row("Total FAX",       total,  fill=True,  bold=True)
    stat_row("Envoyes (SF)",    sf,     fill=False, indent=1)
    stat_row("Recus (RF)",      rf,     fill=True,  indent=1)
    pdf.ln(1)
    stat_row("Pages totales",   p_tot,  fill=False, bold=True)
    stat_row("Pages envoyees",  p_sf,   fill=True,  indent=1)
    stat_row("Pages recues",    p_rf,   fill=False, indent=1)
    pdf.ln(1)
    err_color = RED if erreurs not in ("-", "0") else GREEN
    stat_row("Erreurs totales", erreurs, fill=True, vcolor=err_color, bold=True)

    pdf.ln(5)
    try:
        taux_f = float(taux_s.replace(",", "."))
        taux_color = GREEN if taux_f >= 95 else (ORANGE if taux_f >= 80 else RED)
        taux_disp  = f"{taux_f:.2f}%"
    except Exception:
        taux_color = MUTED
        taux_disp  = "-"

    y_taux = pdf.get_y()
    pdf.set_fill_color(*LIGHT)
    pdf.rect(10, y_taux, 190, 20, "F")
    pdf.set_y(y_taux + 4)
    pdf.set_x(16)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*DARK)
    pdf.cell(105, 10, "Taux de reussite", border=0)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*taux_color)
    pdf.cell(79, 10, taux_disp, border=0, align="R")
    pdf.ln(22)
    pdf.set_text_color(*DARK)

    errs = stats.get("erreurs_par_type") or report.get("erreurs_par_type") or {}
    if isinstance(errs, dict) and errs:
        section_title("Erreurs par type")
        sorted_errs = sorted(errs.items(), key=lambda x: -x[1])
        total_errs = sum(v for _, v in sorted_errs)
        for i, (etype, cnt) in enumerate(sorted_errs):
            pct = f"  ({cnt / total_errs * 100:.1f}%)" if total_errs else ""
            stat_row(_l(str(etype)), _fmt(str(cnt)) + pct,
                     fill=(i % 2 == 0), vcolor=RED)
        pdf.ln(6)

    qr_path = report.get("qr_path")
    if qr_path:
        qr_file = Path(str(qr_path))
        if qr_file.exists():
            section_title("QR Code - acces au rapport PDF")
            y_qr = pdf.get_y() + 2
            try:
                pdf.image(str(qr_file), x=80, y=y_qr, w=50, h=50)
                pdf.set_y(y_qr + 54)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*MUTED)
                pdf.cell(0, 5, "Scannez pour acceder au rapport PDF en ligne",
                         align="C")
                pdf.set_text_color(*DARK)
                pdf.ln(4)
            except Exception:
                pass

    pdf.set_y(-14)
    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*MUTED)
    full_id = _l(str(report.get("report_id", "")))
    pdf.cell(0, 5, f"FaxCloud Analyzer  |  ref: {full_id}", align="C")

    return bytes(pdf.output())