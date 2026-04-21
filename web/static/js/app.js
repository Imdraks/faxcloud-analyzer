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

        this.initAsteriskConfig();
    }

    async initAsteriskConfig() {
        const form = document.getElementById('asteriskConfigForm');
        if (!form) return;

        // Charger la config courante
        try {
            const res = await fetch('/api/asterisk/config');
            if (res.ok) {
                const cfg = await res.json();
                document.getElementById('cfgEnabled').checked = !!cfg.ami_enabled;
                document.getElementById('cfgSimulation').checked = !!cfg.ami_simulation;
                document.getElementById('cfgHost').value = cfg.ami_host || '';
                document.getElementById('cfgPort').value = cfg.ami_port || 5038;
                document.getElementById('cfgUsername').value = cfg.ami_username || '';
                document.getElementById('cfgSecret').value = '';  // masqué côté serveur
                document.getElementById('cfgTrunk').value = cfg.ami_trunk || '';
                document.getElementById('cfgContext').value = cfg.ami_context || 'faxcloud-detect';
                document.getElementById('cfgCallTimeout').value = cfg.ami_call_timeout || 15;
                document.getElementById('cfgDetectTimeout').value = cfg.ami_detect_timeout || 10;
                document.getElementById('cfgCacheTtl').value = cfg.cache_ttl_hours || 168;
                this._updateSimHelp();
            }
        } catch (_) {}

        document.getElementById('cfgSimulation').addEventListener('change', () => this._updateSimHelp());

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveAsteriskConfig();
        });
    }

    _updateSimHelp() {
        const help = document.getElementById('cfgSimulationHelp');
        if (help) {
            help.style.display = document.getElementById('cfgSimulation')?.checked ? 'block' : 'none';
        }
    }

    async saveAsteriskConfig() {
        const statusEl = document.getElementById('cfgSaveStatus');
        const setStatus = (msg, ok = true) => {
            if (statusEl) { statusEl.textContent = msg; statusEl.style.color = ok ? '#2a7' : '#c33'; }
        };
        setStatus('Enregistrement…');

        const payload = {
            ami_enabled: document.getElementById('cfgEnabled').checked,
            ami_simulation: document.getElementById('cfgSimulation').checked,
            ami_host: document.getElementById('cfgHost').value.trim() || '127.0.0.1',
            ami_port: parseInt(document.getElementById('cfgPort').value) || 5038,
            ami_username: document.getElementById('cfgUsername').value.trim() || 'admin',
            ami_secret: document.getElementById('cfgSecret').value || '********',
            ami_trunk: document.getElementById('cfgTrunk').value.trim(),
            ami_context: document.getElementById('cfgContext').value.trim() || 'faxcloud-detect',
            ami_call_timeout: parseInt(document.getElementById('cfgCallTimeout').value) || 15,
            ami_detect_timeout: parseInt(document.getElementById('cfgDetectTimeout').value) || 10,
            cache_ttl_hours: parseInt(document.getElementById('cfgCacheTtl').value) || 168,
        };

        try {
            const res = await fetch('/api/asterisk/config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                setStatus('Configuration enregistrée.', true);
            } else {
                const err = await res.json().catch(() => ({}));
                setStatus('Erreur: ' + (err.error || res.status), false);
            }
        } catch (err) {
            setStatus('Erreur réseau: ' + err.message, false);
        }
    }

    async uploadFile(file) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        
        // Ajoute les paramètres d'analyse
        const enableDetection = document.getElementById('enableDetection');
        if (enableDetection && enableDetection.checked) {
            formData.append('enable_detection', 'true');
        }

        const msgDiv = document.getElementById('uploadMessage');
        const progressDiv = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const statusEl = document.getElementById('uploadStatus');

        const formatBytes = (bytes) => {
            const b = Number(bytes);
            if (!Number.isFinite(b) || b <= 0) return '0 B';
            const units = ['B', 'KB', 'MB', 'GB'];
            const i = Math.min(units.length - 1, Math.floor(Math.log(b) / Math.log(1024)));
            const v = b / Math.pow(1024, i);
            return `${v.toFixed(v >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
        };

        const setStatus = (t) => {
            if (statusEl) statusEl.textContent = t;
        };
        const setPercent = (p) => {
            const pct = Math.max(0, Math.min(100, Math.round(p)));
            if (progressFill) progressFill.style.width = `${pct}%`;
        };

        msgDiv.innerHTML = '';
        progressDiv.classList.remove('hidden');
        setStatus(`Fichier: ${file.name} (${formatBytes(file.size)}) — Envoi…`);
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
            setStatus('Erreur');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => new FaxApp());
