async function fetchJson(url) {
  const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

class ReportEntries {
  constructor(reportId) {
    this.reportId = reportId;
    this.offset = 0;
    this.limit = 200;
    this.total = null;

    this.tbody = document.querySelector('#entriesTableBody');
    this.status = document.querySelector('#entriesStatus');
    this.btnMore = document.querySelector('#loadMoreBtn');

    this.btnMore?.addEventListener('click', () => this.loadMore());
  }

  setStatus(text) {
    if (this.status) this.status.textContent = text;
  }

  appendRows(rows) {
    if (!this.tbody) return;
    const fragment = document.createDocumentFragment();

    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escapeHtml(r.datetime)}</td>
        <td>${escapeHtml(r.type)}</td>
        <td>${escapeHtml(r.pages)}</td>
        <td>${escapeHtml(r.utilisateur)}</td>
        <td>${escapeHtml(r.numero_normalise || r.numero_original)}</td>
        <td>${r.valide ? '✓' : '✗'}</td>
      `;
      fragment.appendChild(tr);
    }

    this.tbody.appendChild(fragment);
  }

  async loadMore() {
    try {
      this.btnMore && (this.btnMore.disabled = true);
      this.setStatus('Chargement…');

      const url = `/api/report/${encodeURIComponent(this.reportId)}/entries?offset=${this.offset}&limit=${this.limit}`;
      const data = await fetchJson(url);

      this.total = data.total;
      this.appendRows(data.entries || []);
      this.offset += (data.entries || []).length;

      const remaining = Math.max(0, (this.total ?? 0) - this.offset);
      this.setStatus(`Affiché: ${this.offset}/${this.total} (reste ${remaining})`);

      if (remaining <= 0) {
        if (this.btnMore) this.btnMore.classList.add('hidden');
      } else {
        if (this.btnMore) this.btnMore.classList.remove('hidden');
      }
    } catch (e) {
      this.setStatus(`Erreur: ${e.message}`);
    } finally {
      this.btnMore && (this.btnMore.disabled = false);
    }
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const root = document.querySelector('[data-report-id]');
  const reportId = root?.getAttribute('data-report-id');
  if (!reportId) return;

  const entries = new ReportEntries(reportId);
  await entries.loadMore();
});
