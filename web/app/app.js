/* ═══════════════════════════════════════════════════════════════════════ */
/* FaxCloud Analyzer - JavaScript (Drag & Drop + Local Analysis)           */
/* ═══════════════════════════════════════════════════════════════════════ */
/* CONFORMITÉ: CONDITIONS_ANALYSE.md (v1.0 - 10 Décembre 2025)            */
/* ═══════════════════════════════════════════════════════════════════════ */

let currentAnalysis = null;
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const uploadStatus = document.getElementById('uploadStatus');

// ═══════════════════════════════════════════════════════════════════════
// DRAG & DROP EVENTS
// ═══════════════════════════════════════════════════════════════════════

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// ═══════════════════════════════════════════════════════════════════════
// FILE HANDLING & ANALYSIS
// ═══════════════════════════════════════════════════════════════════════

async function handleFile(file) {
    // Vérification du type
    const validTypes = ['text/csv', 'text/plain', 'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const validExtensions = ['.csv', '.xlsx', '.xls'];

    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!validExtensions.includes(ext)) {
        showStatus('error', '❌ Type de fichier invalide. Utilisez CSV ou XLSX.');
        return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB max
        showStatus('error', '❌ Fichier trop volumineux (max 10MB)');
        return;
    }

    // Démarrage de l'analyse
    showStatus('info', '📥 Fichier reçu: ' + file.name);
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'block';

    try {
        await analyzeFile(file);
    } catch (error) {
        console.error(error);
        uploadSection.style.display = 'block';
        loadingSection.style.display = 'none';
        showStatus('error', '❌ Erreur: ' + error.message);
    }
}

async function analyzeFile(file) {
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (ext === '.csv') {
        analyzeCSV(file);
    } else if (ext === '.xlsx' || ext === '.xls') {
        analyzeExcel(file);
    }
}

function analyzeCSV(file) {
    const reader = new FileReader();

    reader.onload = (e) => {
        try {
            const csv = e.target.result;
            const lines = csv.split('\n').filter(l => l.trim());

            if (lines.length < 2) {
                throw new Error('Fichier CSV vide ou invalide');
            }

            // Parser CSV simple
            const headers = parseCSVLine(lines[0]);
            const data = lines.slice(1).map(line => {
                const values = parseCSVLine(line);
                return {
                    faxId: values[0] || '',
                    utilisateur: values[1] || '',
                    reseller: values[2] || '',
                    mode: values[3] || '',
                    email: values[4] || '',
                    datetime: values[5] || '',
                    numeroEnvoi: values[6] || '',
                    numeroAppele: values[7] || '',
                    intlCall: values[8] || '',
                    internalCall: values[9] || '',
                    pages: parseInt(values[10]) || 0,
                    duration: values[11] || '',
                    billedPages: values[12] || '',
                    billingType: values[13] || ''
                };
            });

            performAnalysis(data);
        } catch (error) {
            throw new Error('Erreur lors de la lecture du CSV: ' + error.message);
        }
    };

    reader.readAsText(file);
}

function analyzeExcel(file) {
    // Pour Excel, on utilise une approche simplifiée avec papaparse ou autre
    // Pour maintenant, on affiche un message
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            // Conversion basique: afficher le contenu en texte
            const text = e.target.result;
            showStatus('warning', '⚠️ Format Excel détecté - Conversion en cours...');
            
            // Fallback: parser comme texte si possible
            setTimeout(() => {
                showStatus('error', '❌ Les fichiers Excel nécessitent une bibliothèque supplémentaire. Utilisez CSV.');
                uploadSection.style.display = 'block';
                loadingSection.style.display = 'none';
            }, 1000);
        } catch (error) {
            throw new Error('Erreur Excel: ' + error.message);
        }
    };

    reader.readAsArrayBuffer(file);
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        const nextChar = line[i + 1];

        if (char === '"') {
            if (inQuotes && nextChar === '"') {
                current += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }

    result.push(current.trim());
    return result;
}

// ═══════════════════════════════════════════════════════════════════════
// ANALYSIS ENGINE (Normalization & Validation)
// ═══════════════════════════════════════════════════════════════════════

function performAnalysis(data) {
    try {
        const analysis = {
            totalFax: data.length,
            faxEnvoyes: 0,
            faxRecus: 0,
            pagesTotales: 0,
            erreursTotales: 0,
            entries: [],
            userStats: {},
            errorTypes: {},
            successRate: 0,
            reportId: generateUUID()
        };

        for (const row of data) {
            const entry = analyzeEntry(row);
            analysis.entries.push(entry);

            // Statistiques globales
            if (entry.mode === 'SF') analysis.faxEnvoyes++;
            if (entry.mode === 'RF') analysis.faxRecus++;
            analysis.pagesTotales += entry.pages;
            if (!entry.valide) analysis.erreursTotales++;

            // Stats par utilisateur
            const user = entry.utilisateur;
            if (!analysis.userStats[user]) {
                analysis.userStats[user] = { total: 0, errors: 0 };
            }
            analysis.userStats[user].total++;
            if (!entry.valide) analysis.userStats[user].errors++;

            // Types d'erreurs
            if (entry.erreurs.length > 0) {
                entry.erreurs.forEach(err => {
                    analysis.errorTypes[err] = (analysis.errorTypes[err] || 0) + 1;
                });
            }
        }

        // Calcul du taux de réussite
        analysis.successRate = analysis.totalFax > 0
            ? Math.round(((analysis.totalFax - analysis.erreursTotales) / analysis.totalFax) * 100)
            : 0;

        currentAnalysis = analysis;
        loadingSection.style.display = 'none';
        displayResults(analysis);
    } catch (error) {
        loadingSection.style.display = 'none';
        uploadSection.style.display = 'block';
        showStatus('error', '❌ Erreur d\'analyse: ' + error.message);
    }
}

function analyzeEntry(row) {
    const numeroAppele = row.numeroAppele || '';
    const normalized = normalizeNumber(numeroAppele);
    const isValid = validateNumber(normalized);

    const erreurs = [];
    if (!isValid) {
        if (!numeroAppele) {
            erreurs.push('Numéro vide');
        } else if (normalized.length !== 11 && normalized.length > 0) {
            erreurs.push('Longueur incorrecte');
        } else if (!normalized.startsWith('33')) {
            erreurs.push('Code pays invalide');
        } else if (!/^\d+$/.test(normalized) && normalized.length > 0) {
            erreurs.push('Caractères invalides');
        }
    }

    return {
        faxId: row.faxId,
        utilisateur: row.utilisateur,
        mode: row.mode === 'SF' ? 'Envoyé' : row.mode === 'RF' ? 'Reçu' : row.mode,
        numeroOriginal: numeroAppele,
        numeroNormalise: normalized || '(vide)',
        valide: isValid,
        pages: row.pages,
        datetime: row.datetime,
        erreurs: erreurs
    };
}

function normalizeNumber(raw) {
    if (!raw) return '';

    // Supprimer les espaces et caractères spéciaux
    let cleaned = raw.replace(/\D/g, '');

    if (!cleaned) return '';

    // Si commence par 0, remplacer par 33
    if (cleaned.startsWith('0')) {
        cleaned = '33' + cleaned.substring(1);
    }

    // Si commence par +33, supprimer le +
    if (cleaned.startsWith('+33')) {
        cleaned = '33' + cleaned.substring(3);
    }

    return cleaned;
}

function validateNumber(normalized) {
    if (!normalized) return false;
    if (normalized.length !== 11) return false;
    if (!normalized.startsWith('33')) return false;
    if (!/^\d+$/.test(normalized)) return false;
    return true;
}

// ═══════════════════════════════════════════════════════════════════════
// DISPLAY RESULTS
// ═══════════════════════════════════════════════════════════════════════

function displayResults(analysis) {
    // Stats principales
    document.getElementById('resultTotalFax').textContent = analysis.totalFax;
    document.getElementById('resultSent').textContent = analysis.faxEnvoyes;
    document.getElementById('resultReceived').textContent = analysis.faxRecus;
    document.getElementById('resultSuccessRate').textContent = analysis.successRate + '%';

    // Détails
    document.getElementById('detailPages').textContent = analysis.pagesTotales;
    document.getElementById('detailErrors').textContent = analysis.erreursTotales;
    document.getElementById('detailUsers').textContent = Object.keys(analysis.userStats).length;

    // Détails utilisateurs
    const userDetails = document.getElementById('userDetails');
    userDetails.innerHTML = '';
    for (const [user, stats] of Object.entries(analysis.userStats)) {
        const rate = ((stats.total - stats.errors) / stats.total * 100).toFixed(1);
        userDetails.innerHTML += `
            <p>
                <strong>${user}</strong><br>
                FAX: ${stats.total} | Erreurs: ${stats.errors} | Réussite: ${rate}%
            </p>
        `;
    }

    // Erreurs détectées
    const errorDetails = document.getElementById('errorDetails');
    errorDetails.innerHTML = '';
    if (Object.keys(analysis.errorTypes).length === 0) {
        errorDetails.innerHTML = '<p style="color: green;">✅ Aucune erreur détectée!</p>';
    } else {
        for (const [error, count] of Object.entries(analysis.errorTypes)) {
            const percent = ((count / analysis.erreursTotales) * 100).toFixed(1);
            errorDetails.innerHTML += `<p>${error}: <strong>${count}</strong> (${percent}%)</p>`;
        }
    }

    // QR Code
    generateQRCode(analysis.reportId);
    document.getElementById('reportId').innerHTML = `Report ID: <code>${analysis.reportId}</code>`;

    // Table de données (premiers 20)
    const tbody = document.getElementById('dataTableBody');
    tbody.innerHTML = '';
    for (let i = 0; i < Math.min(20, analysis.entries.length); i++) {
        const entry = analysis.entries[i];
        const validClass = entry.valide ? 'valid-yes' : 'valid-no';
        const validText = entry.valide ? '✓ Oui' : '✗ Non';
        const errors = entry.erreurs.length > 0 ? entry.erreurs.join(', ') : '-';

        tbody.innerHTML += `
            <tr>
                <td>${entry.utilisateur}</td>
                <td>${entry.mode}</td>
                <td>${entry.numeroOriginal}</td>
                <td>${entry.numeroNormalise}</td>
                <td class="${validClass}">${validText}</td>
                <td>${entry.pages}</td>
                <td><small>${errors}</small></td>
            </tr>
        `;
    }

    resultsSection.style.display = 'block';
}

// ═══════════════════════════════════════════════════════════════════════
// QR CODE GENERATION
// ═══════════════════════════════════════════════════════════════════════

function generateQRCode(reportId) {
    const canvas = document.getElementById('qrCanvas');
    const url = `http://localhost:8000/reports/${reportId}`;

    new QRious({
        element: canvas,
        value: url,
        size: 200,
        level: 'H',
        mime: 'image/png'
    });
}

function downloadQRCode() {
    if (!currentAnalysis) return;

    const canvas = document.getElementById('qrCanvas');
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/png');
    link.download = `qrcode-${currentAnalysis.reportId}.png`;
    link.click();
}

// ═══════════════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════════════

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function resetAnalysis() {
    currentAnalysis = null;
    resultsSection.style.display = 'none';
    loadingSection.style.display = 'none';
    uploadSection.style.display = 'block';
    fileInput.value = '';
    uploadStatus.style.display = 'none';
}

function showStatus(type, message) {
    uploadStatus.textContent = message;
    uploadStatus.className = 'status-message ' + type;
    uploadStatus.style.display = 'block';

    if (type !== 'error' && type !== 'warning') {
        setTimeout(() => {
            uploadStatus.style.display = 'none';
        }, 3000);
    }
}
