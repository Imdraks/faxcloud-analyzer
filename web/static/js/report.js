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
    this.limit = 20;
    this.total = null;
    this.page = 1;
    this.pageCount = 1;

    this.filters = {
      type: '',
      valide: '',
      q: '',
      date_from: '',
      date_to: '',
      pages_min: '',
      pages_max: '',
      order: 'asc',
    };

    this.tbody = document.querySelector('#entriesTableBody');
    this.status = document.querySelector('#entriesStatus');
    this.pagination = document.querySelector('#entriesPagination');

    this.typeFilter = document.getElementById('entriesTypeFilter');
    this.validFilter = document.getElementById('entriesValidFilter');
    this.dateFromInput = document.getElementById('entriesDateFrom');
    this.dateToInput = document.getElementById('entriesDateTo');
    this.pagesMinInput = document.getElementById('entriesPagesMin');
    this.pagesMaxInput = document.getElementById('entriesPagesMax');
    this.searchInput = document.getElementById('entriesSearchInput');
    this.orderSelect = document.getElementById('entriesOrder');
    this.applyBtn = document.getElementById('entriesApplyFilters');
    this.clearBtn = document.getElementById('entriesClearFilters');
    this.exportFilteredBtn = document.getElementById('entriesExportFilteredCsv');
    this.exportFilteredJsonBtn = document.getElementById('entriesExportFilteredJson');

    this._searchDebounceTimer = null;

    this.applyBtn?.addEventListener('click', () => this.applyFilters());
    this.clearBtn?.addEventListener('click', () => this.clearFilters());
    this.searchInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.applyFilters();
    });

    // Debounced search
    this.searchInput?.addEventListener('input', () => {
      if (this._searchDebounceTimer) window.clearTimeout(this._searchDebounceTimer);
      this._searchDebounceTimer = window.setTimeout(() => this.applyFilters(), 300);
    });

    // Auto-apply on most inputs
    this.typeFilter?.addEventListener('change', () => this.applyFilters());
    this.validFilter?.addEventListener('change', () => this.applyFilters());
    this.dateFromInput?.addEventListener('change', () => this.applyFilters());
    this.dateToInput?.addEventListener('change', () => this.applyFilters());
    this.pagesMinInput?.addEventListener('change', () => this.applyFilters());
    this.pagesMaxInput?.addEventListener('change', () => this.applyFilters());

    this.orderSelect?.addEventListener('change', () => this.applyFilters());
    this.exportFilteredBtn?.addEventListener('click', () => this.exportFilteredCsv());
    this.exportFilteredJsonBtn?.addEventListener('click', () => this.exportFilteredJson());

    // Restore state from URL (filters + page)
    this.restoreFromUrl();
  }

  restoreFromUrl() {
    const params = new URLSearchParams(window.location.search);

    const page = parseInt(params.get('page') || '1', 10);
    if (!Number.isNaN(page) && page >= 1) this.page = page;

    const setIfPresent = (key, el, fallback = '') => {
      const v = params.get(key);
      if (v === null) return;
      if (el) el.value = v;
      this.filters[key] = v;
      if (v === '' && fallback !== '') this.filters[key] = fallback;
    };

    setIfPresent('type', this.typeFilter);
    setIfPresent('valide', this.validFilter);
    setIfPresent('q', this.searchInput);
    setIfPresent('date_from', this.dateFromInput);
    setIfPresent('date_to', this.dateToInput);
    setIfPresent('pages_min', this.pagesMinInput);
    setIfPresent('pages_max', this.pagesMaxInput);
    setIfPresent('order', this.orderSelect, 'asc');

    if (this.orderSelect && !this.orderSelect.value) this.orderSelect.value = 'asc';
    if (!this.filters.order) this.filters.order = 'asc';
  }

  _updateUrl(page) {
    const params = new URLSearchParams();
    params.set('page', String(page));
    if (this.filters.type) params.set('type', this.filters.type);
    if (this.filters.valide) params.set('valide', this.filters.valide);
    if (this.filters.q) params.set('q', this.filters.q);
    if (this.filters.date_from) params.set('date_from', this.filters.date_from);
    if (this.filters.date_to) params.set('date_to', this.filters.date_to);
    if (this.filters.pages_min) params.set('pages_min', this.filters.pages_min);
    if (this.filters.pages_max) params.set('pages_max', this.filters.pages_max);
    if (this.filters.order && this.filters.order !== 'asc') params.set('order', this.filters.order);

    const next = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({ page }, '', next);
  }

  setStatus(text) {
    if (this.status) this.status.textContent = text;
  }

  _readFiltersFromUI() {
    this.filters.type = (this.typeFilter?.value || '').trim();
    this.filters.valide = (this.validFilter?.value || '').trim();
    this.filters.q = (this.searchInput?.value || '').trim();
    this.filters.date_from = (this.dateFromInput?.value || '').trim();
    this.filters.date_to = (this.dateToInput?.value || '').trim();
    this.filters.pages_min = (this.pagesMinInput?.value || '').trim();
    this.filters.pages_max = (this.pagesMaxInput?.value || '').trim();
    this.filters.order = (this.orderSelect?.value || 'asc').trim() || 'asc';
  }

  _buildQueryParams(offset) {
    const params = new URLSearchParams();
    params.set('offset', String(offset));
    params.set('limit', String(this.limit));

    if (this.filters.type) params.set('type', this.filters.type);
    if (this.filters.valide) params.set('valide', this.filters.valide);
    if (this.filters.q) params.set('q', this.filters.q);
    if (this.filters.date_from) params.set('date_from', this.filters.date_from);
    if (this.filters.date_to) params.set('date_to', this.filters.date_to);
    if (this.filters.pages_min) params.set('pages_min', this.filters.pages_min);
    if (this.filters.pages_max) params.set('pages_max', this.filters.pages_max);
    if (this.filters.order) params.set('order', this.filters.order);

    return params.toString();
  }

  applyFilters() {
    this._readFiltersFromUI();
    // Basic validation: keep as simple UX (no modal)
    const pmin = this.filters.pages_min ? parseInt(this.filters.pages_min, 10) : null;
    const pmax = this.filters.pages_max ? parseInt(this.filters.pages_max, 10) : null;
    if (pmin !== null && pmax !== null && !Number.isNaN(pmin) && !Number.isNaN(pmax) && pmin > pmax) {
      // swap
      this.filters.pages_min = String(pmax);
      this.filters.pages_max = String(pmin);
      if (this.pagesMinInput) this.pagesMinInput.value = this.filters.pages_min;
      if (this.pagesMaxInput) this.pagesMaxInput.value = this.filters.pages_max;
    }
    this.loadPage(1);
  }

  clearFilters() {
    if (this.typeFilter) this.typeFilter.value = '';
    if (this.validFilter) this.validFilter.value = '';
    if (this.dateFromInput) this.dateFromInput.value = '';
    if (this.dateToInput) this.dateToInput.value = '';
    if (this.pagesMinInput) this.pagesMinInput.value = '';
    if (this.pagesMaxInput) this.pagesMaxInput.value = '';
    if (this.searchInput) this.searchInput.value = '';
    if (this.orderSelect) this.orderSelect.value = 'asc';
    this._readFiltersFromUI();
    this.loadPage(1);
  }

  _buildExportQueryParams() {
    const params = new URLSearchParams();
    if (this.filters.type) params.set('type', this.filters.type);
    if (this.filters.valide) params.set('valide', this.filters.valide);
    if (this.filters.q) params.set('q', this.filters.q);
    if (this.filters.date_from) params.set('date_from', this.filters.date_from);
    if (this.filters.date_to) params.set('date_to', this.filters.date_to);
    if (this.filters.pages_min) params.set('pages_min', this.filters.pages_min);
    if (this.filters.pages_max) params.set('pages_max', this.filters.pages_max);
    if (this.filters.order) params.set('order', this.filters.order);
    return params.toString();
  }

  exportFilteredCsv() {
    this._readFiltersFromUI();
    const qs = this._buildExportQueryParams();
    const url = `/api/report/${encodeURIComponent(this.reportId)}/export.csv${qs ? `?${qs}` : ''}`;
    window.location.href = url;
  }

  exportFilteredJson() {
    this._readFiltersFromUI();
    const qs = this._buildExportQueryParams();
    const url = `/api/report/${encodeURIComponent(this.reportId)}/export.entries.json${qs ? `?${qs}` : ''}`;
    window.location.href = url;
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
      this._updateUrl(target);
      const offset = (target - 1) * this.limit;

      const url = `/api/report/${encodeURIComponent(this.reportId)}/entries?${this._buildQueryParams(offset)}`;
      const data = await fetchJson(url);

      this.total = data.total;
      this.pageCount = Math.max(1, Math.ceil((this.total || 0) / this.limit));
      this.page = Math.min(this.pageCount, target);

      // Si la page demandée dépasse le total (ex: suppression, changement de total), on recalcule.
      if (this.page !== target) {
        const offset2 = (this.page - 1) * this.limit;
        const url2 = `/api/report/${encodeURIComponent(this.reportId)}/entries?${this._buildQueryParams(offset2)}`;
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
  // Handle back/forward navigation
  window.addEventListener('popstate', async () => {
    entries.restoreFromUrl();
    await entries.loadPage(entries.page || 1);
  });

  await entries.loadPage(entries.page || 1);
});
