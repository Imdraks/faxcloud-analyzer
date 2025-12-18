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
    this.limit = 200;
    this.total = null;
    this.page = 1;
    this.pageCount = 1;

    this.tbody = document.querySelector('#entriesTableBody');
    this.status = document.querySelector('#entriesStatus');
    this.pagination = document.querySelector('#entriesPagination');
  }

  setStatus(text) {
    if (this.status) this.status.textContent = text;
  }

  setRows(rows) {
    if (!this.tbody) return;
    this.tbody.innerHTML = '';
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

  renderPagination() {
    if (!this.pagination) return;
    this.pagination.innerHTML = '';

    if (!this.total || this.pageCount <= 1) return;

    const makeBtn = (label, targetPage, { disabled = false, active = false } = {}) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `page-btn${active ? ' active' : ''}`;
      btn.textContent = label;
      btn.disabled = disabled;
      btn.addEventListener('click', () => this.loadPage(targetPage));
      return btn;
    };

    // « previous, » next (simple)
    this.pagination.appendChild(makeBtn('«', this.page - 1, { disabled: this.page <= 1 }));

    const windowSize = 10;
    let start = Math.max(1, this.page - Math.floor(windowSize / 2));
    let end = start + windowSize - 1;
    if (end > this.pageCount) {
      end = this.pageCount;
      start = Math.max(1, end - windowSize + 1);
    }

    for (let p = start; p <= end; p++) {
      this.pagination.appendChild(makeBtn(String(p), p, { active: p === this.page }));
    }

    this.pagination.appendChild(makeBtn('»', this.page + 1, { disabled: this.page >= this.pageCount }));
  }

  async loadPage(page) {
    try {
      this.setStatus('Chargement…');

      const target = Math.max(1, parseInt(page, 10) || 1);
      const offset = (target - 1) * this.limit;

      const url = `/api/report/${encodeURIComponent(this.reportId)}/entries?offset=${offset}&limit=${this.limit}`;
      const data = await fetchJson(url);

      this.total = data.total;
      this.pageCount = Math.max(1, Math.ceil((this.total || 0) / this.limit));
      this.page = Math.min(this.pageCount, target);

      // Si la page demandée dépasse le total (ex: suppression, changement de total), on recalcule.
      if (this.page !== target) {
        const offset2 = (this.page - 1) * this.limit;
        const url2 = `/api/report/${encodeURIComponent(this.reportId)}/entries?offset=${offset2}&limit=${this.limit}`;
        const data2 = await fetchJson(url2);
        this.total = data2.total;
        this.pageCount = Math.max(1, Math.ceil((this.total || 0) / this.limit));
        this.setRows(data2.entries || []);
      } else {
        this.setRows(data.entries || []);
      }

      const shown = (data.entries || []).length;
      const from = (this.page - 1) * this.limit + (shown > 0 ? 1 : 0);
      const to = (this.page - 1) * this.limit + shown;
      this.setStatus(`Page ${this.page}/${this.pageCount} — lignes ${from}-${to} / ${this.total}`);
      this.renderPagination();
    } catch (e) {
      this.setStatus(`Erreur: ${e.message}`);
    } finally {
      // nothing
    }
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  const root = document.querySelector('[data-report-id]');
  const reportId = root?.getAttribute('data-report-id');
  if (!reportId) return;

  const deleteBtn = document.getElementById('deleteReportBtn');
  deleteBtn?.addEventListener('click', async () => {
    const ok = confirm('Supprimer ce rapport ? Cette action est irréversible.');
    if (!ok) return;
    try {
      deleteBtn.disabled = true;
      const res = await fetch(`/api/report/${encodeURIComponent(reportId)}`, { method: 'DELETE' });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }
      window.location.href = '/reports';
    } catch (e) {
      alert(`Erreur suppression: ${e.message}`);
    } finally {
      deleteBtn.disabled = false;
    }
  });

  const entries = new ReportEntries(reportId);
  await entries.loadPage(1);
});
