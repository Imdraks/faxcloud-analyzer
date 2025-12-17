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

        const contractInput = document.getElementById('contractInput');
        const startInput = document.getElementById('startInput');
        const endInput = document.getElementById('endInput');

        const contract = contractInput?.value?.trim();
        const start = startInput?.value?.trim();
        const end = endInput?.value?.trim();

        if (contract) formData.append('contract', contract);
        if (start) formData.append('start', start);
        if (end) formData.append('end', end);

        const msgDiv = document.getElementById('uploadMessage');
        const progressDiv = document.getElementById('uploadProgress');
        
        try {
            progressDiv.classList.remove('hidden');

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                msgDiv.innerHTML = `<div class="success">✓ Rapport créé! ID: ${data.report_id} — FAX: ${data.total_fax ?? ''} — erreurs: ${data.errors ?? ''}</div>`;
                setTimeout(() => window.location.href = `/report/${data.report_id}`, 900);
            } else {
                msgDiv.innerHTML = `<div class="error">✗ Erreur: ${data.error}</div>`;
            }
        } catch (error) {
            msgDiv.innerHTML = `<div class="error">✗ Erreur: ${error.message}</div>`;
        } finally {
            progressDiv.classList.add('hidden');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => new FaxApp());
