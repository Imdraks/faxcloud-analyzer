class FaxApp {
    constructor() {
        this.init();
    }

    init() {
        const fileInput = document.getElementById('fileInput');
        const dragZone = document.getElementById('dragDropZone');

        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.uploadFile(e.target.files[0]));
        }

        if (dragZone) {
            dragZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dragZone.classList.add('drag-over');
            });
            dragZone.addEventListener('dragleave', () => dragZone.classList.remove('drag-over'));
            dragZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dragZone.classList.remove('drag-over');
                this.uploadFile(e.dataTransfer.files[0]);
            });
        }
    }

    async uploadFile(file) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        const msgDiv = document.getElementById('uploadMessage');
        const progressDiv = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const statusEl = document.getElementById('uploadStatus');

        const setStatus = (t) => {
            if (statusEl) statusEl.textContent = t;
        };
        const setPercent = (p) => {
            const pct = Math.max(0, Math.min(100, Math.round(p)));
            if (progressFill) progressFill.style.width = `${pct}%`;
        };

        msgDiv.innerHTML = '';
        progressDiv.classList.remove('hidden');
        setStatus('Envoi du fichier…');
        setPercent(0);

        let evt = null;
        let pollTimer = null;
        let lastProgressAt = Date.now();

        const stopEvents = () => {
            try { evt?.close(); } catch (_) {}
            evt = null;
        };

        const stopPolling = () => {
            if (pollTimer) {
                window.clearInterval(pollTimer);
                pollTimer = null;
            }
        };

        const applyProgressPayload = (data) => {
            if (!data.success) throw new Error(data.error || 'Erreur');

            const message = data.message || '';
            const backendPercent = Number.isFinite(data.percent) ? data.percent : 0;

            // Map backend 0..100 to overall 35..100 (upload is 0..35)
            const overall = 35 + (backendPercent * 0.65);
            setPercent(overall);

            const label = message ? `${message}` : 'Traitement…';
            setStatus(label);

            if (data.done) {
                if (data.error) throw new Error(data.error);
                if (data.report_id) {
                    setStatus('Terminé. Redirection…');
                    setPercent(100);
                    stopEvents();
                    stopPolling();
                    window.location.href = `/report/${data.report_id}`;
                }
            }
        };

        const startPolling = (uploadId) => {
            if (pollTimer) return;
            stopEvents();

            pollTimer = window.setInterval(async () => {
                try {
                    const res = await fetch(`/api/upload/${encodeURIComponent(uploadId)}`, {
                        headers: { 'Accept': 'application/json' }
                    });
                    const data = await res.json();
                    applyProgressPayload(data);
                } catch (err) {
                    // Keep polling briefly; errors can be transient.
                }
            }, 750);
        };

        const startEvents = (uploadId) => {
            stopEvents();
            stopPolling();

            evt = new EventSource(`/api/upload/${encodeURIComponent(uploadId)}/events`);

            evt.addEventListener('progress', (e) => {
                try {
                    const data = JSON.parse(e.data);
                    lastProgressAt = Date.now();
                    applyProgressPayload(data);
                } catch (err) {
                    // If SSE payload breaks, fall back to polling.
                    startPolling(uploadId);
                }
            });

            evt.addEventListener('error', () => {
                // Best-effort: SSE may fail due to proxies; fall back to polling.
                startPolling(uploadId);
            });

            // If SSE is connected but no events come through, fall back to polling.
            window.setTimeout(() => {
                if (!evt) return;
                if (Date.now() - lastProgressAt > 2000) {
                    startPolling(uploadId);
                }
            }, 2200);
        };

        try {
            const uploadId = await new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/api/upload_async');

                xhr.upload.onprogress = (e) => {
                    if (!e.lengthComputable) return;
                    const pct = (e.loaded / e.total) * 35;
                    setPercent(pct);
                    setStatus(`Envoi du fichier… ${Math.round((e.loaded / e.total) * 100)}%`);
                };

                xhr.onload = () => {
                    try {
                        const data = JSON.parse(xhr.responseText || '{}');
                        if (!xhr.status || xhr.status >= 400) {
                            throw new Error(data.error || `HTTP ${xhr.status}`);
                        }
                        if (!data.success) throw new Error(data.error || 'Erreur');
                        resolve(data.upload_id);
                    } catch (err) {
                        reject(err);
                    }
                };

                xhr.onerror = () => reject(new Error('Erreur réseau'));
                xhr.send(formData);
            });

            setPercent(35);
            setStatus('Traitement…');
            startEvents(uploadId);
        } catch (error) {
            stopEvents();
            stopPolling();
            msgDiv.innerHTML = `<div class="error">✗ Erreur: ${error.message}</div>`;
            progressDiv.classList.add('hidden');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => new FaxApp());
