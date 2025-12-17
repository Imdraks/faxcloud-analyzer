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
        
        try {
            progressDiv.classList.remove('hidden');

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                msgDiv.innerHTML = `<div class="success">✓ Rapport créé! ID: ${data.report_id}</div>`;
                setTimeout(() => window.location.href = '/reports', 2000);
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
