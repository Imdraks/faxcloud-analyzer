# 🧠 PSEUDO-CODE COMPLET - FaxCloud Analyzer

## 📌 TABLE DES MATIÈRES
1. Algorithme général
2. Normalisation des numéros
3. Validation des numéros
4. Analyse des données
5. Génération QR code
6. Gestion base de données
7. API Web

---

## 1️⃣ ALGORITHME GÉNÉRAL (main.py)

```pseudocode
ALGORITHM FaxCloudAnalyzer
INPUT: user_action, contract_id, date_debut, date_fin, file_path
OUTPUT: report_id, report_json, qr_code_path

BEGIN
    // Initialisation
    INITIALIZE logging system
    INITIALIZE config from config.py
    CREATE necessary directories if not exist
    
    SWITCH user_action DO
        CASE "import":
            // Étape 1: Importer
            data ← IMPORT_FAXCLOUD_EXPORT(file_path)
            IF NOT data.success THEN
                RETURN error_message
            END IF
            
            // Étape 2: Analyser
            analysis ← ANALYZE_DATA(
                data.rows,
                contract_id,
                date_debut,
                date_fin
            )
            
            // Étape 3: Générer rapport
            report ← GENERATE_REPORT(analysis)
            
            // Étape 4: Sauvegarder en base
            INSERT_REPORT_TO_DB(report)
            
            RETURN {
                success: TRUE,
                report_id: report.id,
                qr_path: report.qr_path,
                report_url: report.url
            }
            
        CASE "list_reports":
            reports ← GET_ALL_REPORTS_FROM_DB()
            RETURN reports
            
        CASE "get_report":
            report ← GET_REPORT_BY_ID(contract_id)
            RETURN report
            
        DEFAULT:
            RETURN error("Action inconnue")
    END SWITCH
    
END
```

---

## 2️⃣ NORMALISATION DES NUMÉROS (analyzer.py)

### Pseudo-code détaillé

```pseudocode
FUNCTION normalize_number(raw_number: STRING) -> STRING

INPUT: raw_number
    Exemples: "0622334455", "+33622334455", "33 6 22 33 44 55", "invalid", "", NULL

OUTPUT: normalized (11 chiffres commençant par 33)
    Exemples: "33622334455", "", "33133445566"

PROCESS:
    
    // Étape 1: Vérifier si vide ou None
    IF raw_number IS NULL OR raw_number IS EMPTY THEN
        RETURN ""
    END IF
    
    // Étape 2: Supprimer les espaces avant/après
    normalized ← TRIM(raw_number)
    
    // Étape 3: Supprimer tous les caractères non-numériques
    //          (garder seulement 0-9, supprimer +, -, espaces, etc)
    normalized ← REGEX_REPLACE(normalized, "[^0-9]", "")
    
    // Étape 4: Vérifier à nouveau si vide après nettoyage
    IF normalized IS EMPTY THEN
        RETURN ""
    END IF
    
    // Étape 5: Gérer les formats français et internationaux
    SWITCH TRUE DO
        // Cas 1: Commence par "+33"
        CASE normalized STARTS WITH "+33":
            normalized ← "33" + SUBSTRING(normalized, 4)
            // "+33622334455" → "33622334455"
            
        // Cas 2: Commence par "0" (format local français)
        CASE normalized STARTS WITH "0":
            normalized ← "33" + SUBSTRING(normalized, 2)
            // "0622334455" → "33622334455"
            
        // Cas 3: Commence déjà par "33"
        CASE normalized STARTS WITH "33":
            // Garder tel quel
            // "33622334455" → "33622334455"
            
        // Cas 4: Autre (par exemple commence par "1", "2", etc)
        DEFAULT:
            // Cas numéro commençant par un autre code pays
            // On ne le normalise pas en France
            // Laisser tel quel pour validation ultérieure
    END SWITCH
    
    // Étape 6: Retourner le numéro normalisé
    RETURN normalized

END FUNCTION
```

### Tableau de transformation

| Entrée | Étape 1 | Étape 2 | Étape 3 | Étape 4 | Étape 5 | Sortie |
|--------|---------|---------|---------|---------|---------|--------|
| `0622334455` | (trim) | `0622334455` | (supprime non-num) | `0622334455` | Commence par 0 → `33622334455` | `33622334455` ✓ |
| `+33622334455` | (trim) | `+33622334455` | (supprime non-num) | `33622334455` | Commence par 33 → (rien) | `33622334455` ✓ |
| `33 6 22 33 44 55` | (trim) | `33 6 22 33 44 55` | (supprime non-num) | `33622334455` | Commence par 33 → (rien) | `33622334455` ✓ |
| `INVALID` | (trim) | `INVALID` | (supprime non-num) | `` | Vide → retour | `` |
| `` | (trim) | `` | Vide → retour | | | `` |

---

## 3️⃣ VALIDATION DES NUMÉROS (analyzer.py)

### Pseudo-code détaillé

```pseudocode
FUNCTION validate_number(normalized: STRING) -> DICTIONARY

INPUT: normalized (déjà normalisé par normalize_number())
    Exemples: "33622334455", "33133445566", ""

OUTPUT: {
    is_valid: BOOLEAN,
    normalized: STRING,
    errors: LIST[STRING]
}

PROCESS:
    
    // Initialiser le résultat
    result ← {
        is_valid: FALSE,
        normalized: normalized,
        errors: []
    }
    
    // Étape 1: Vérifier si vide
    IF normalized IS EMPTY THEN
        APPEND "Numéro vide" TO result.errors
        RETURN result
    END IF
    
    // Étape 2: Vérifier la longueur
    length ← LENGTH(normalized)
    IF length ≠ 11 THEN
        APPEND "Longueur incorrecte: " + length + " au lieu de 11" 
            TO result.errors
    END IF
    
    // Étape 3: Vérifier que ça commence par "33"
    IF NOT normalized STARTS WITH "33" THEN
        APPEND "Ne commence pas par 33" TO result.errors
    END IF
    
    // Étape 4: Vérifier que contient que des chiffres
    // (normalement déjà le cas après normalize_number)
    FOR EACH character IN normalized DO
        IF character NOT IN "0123456789" THEN
            APPEND "Caractères invalides détectés" TO result.errors
            BREAK
        END IF
    END FOR
    
    // Étape 5: Déterminer si valide
    IF result.errors IS EMPTY THEN
        result.is_valid ← TRUE
    ELSE
        result.is_valid ← FALSE
    END IF
    
    // Étape 6: Retourner le résultat
    RETURN result

END FUNCTION
```

### Matrice de validation

| Numéro normalisé | Vide ? | Longueur | Commence 33 ? | Chiffres OK ? | Valide ? | Erreurs |
|------------------|--------|----------|---------------|---------------|----------|---------|
| `33622334455` | Non | 11 ✓ | Oui ✓ | Oui ✓ | **OUI** | Aucune |
| `33133445566` | Non | 11 ✓ | Oui ✓ | Oui ✓ | **OUI** | Aucune |
| `` | Oui | - | - | - | **NON** | Numéro vide |
| `3362233445` | Non | 10 ✗ | Oui ✓ | Oui ✓ | **NON** | Longueur incorrecte |
| `3362233445566` | Non | 13 ✗ | Oui ✓ | Oui ✓ | **NON** | Longueur incorrecte |
| `4433622334455` | Non | 13 ✗ | Non ✗ | Oui ✓ | **NON** | Longueur + 33 |
| `0622334455` | Non | 10 ✗ | Non ✗ | Oui ✓ | **NON** | Longueur + 33 |

---

## 4️⃣ ANALYSE COMPLÈTE DES DONNÉES (analyzer.py)

### Pseudo-code principal

```pseudocode
FUNCTION analyze_data(
    rows: LIST[DICTIONARY],
    contract_id: STRING,
    date_debut: STRING,
    date_fin: STRING
) -> DICTIONARY

INPUT:
    rows: Liste de dictionnaires représentant les lignes du fichier
    contract_id: "CONTRACT_001"
    date_debut: "2024-12-01"
    date_fin: "2024-12-31"

OUTPUT: {
    entries: LIST[DICTIONARY],
    statistics: DICTIONARY,
    contract_id: STRING,
    date_debut: STRING,
    date_fin: STRING
}

PROCESS:

    // Initialiser les structures
    entries ← []
    statistics ← {
        total_fax: 0,
        fax_envoyes: 0,
        fax_recus: 0,
        pages_totales: 0,
        erreurs_totales: 0,
        taux_reussite: 0.0,
        erreurs_par_type: {
            numero_vide: 0,
            longueur_incorrecte: 0,
            ne_commence_pas_33: 0,
            caracteres_invalides: 0,
            autre: 0
        },
        envois_par_utilisateur: {},
        erreurs_par_utilisateur: {}
    }
    
    // Parcourir les lignes
    FOR EACH row IN rows DO
        
        // Étape 1: Extraire les données
        fax_id ← row['A']                    // Fax ID
        utilisateur ← row['B']               // Nom utilisateur
        mode ← row['D']                      // "SF" ou "RF"
        datetime ← row['F']                  // Date et heure
        numero_envoi ← row['G']              // Numéro d'envoi
        numero_appele ← row['H']             // Numéro appelé (critique)
        pages ← CONVERT_TO_INTEGER(row['K']) // Nombre de pages
        
        // Étape 2: Normaliser le numéro appelé
        numero_normalise ← normalize_number(numero_appele)
        validation ← validate_number(numero_normalise)
        
        // Étape 3: Déterminer le type (send/receive)
        IF mode = "SF" THEN
            type_fax ← "send"
        ELSE IF mode = "RF" THEN
            type_fax ← "receive"
        ELSE
            type_fax ← "unknown"
        END IF
        
        // Étape 4: Créer l'entrée
        entry ← {
            id: GENERATE_UUID(),
            fax_id: fax_id,
            utilisateur: utilisateur,
            type: type_fax,
            numero_original: numero_appele,
            numero_normalise: numero_normalise,
            valide: validation.is_valid,
            pages: pages,
            datetime: datetime,
            erreurs: validation.errors
        }
        APPEND entry TO entries
        
        // Étape 5: Mettre à jour les statistiques globales
        statistics.total_fax ← statistics.total_fax + 1
        
        IF type_fax = "send" THEN
            statistics.fax_envoyes ← statistics.fax_envoyes + 1
        ELSE IF type_fax = "receive" THEN
            statistics.fax_recus ← statistics.fax_recus + 1
        END IF
        
        statistics.pages_totales ← statistics.pages_totales + pages
        
        // Étape 6: Gérer les erreurs
        IF NOT validation.is_valid THEN
            statistics.erreurs_totales ← statistics.erreurs_totales + 1
            
            // Compter par type d'erreur
            FOR EACH error_msg IN validation.errors DO
                CASE error_msg OF
                    CONTAINS "vide":
                        statistics.erreurs_par_type.numero_vide ← +1
                    CONTAINS "Longueur":
                        statistics.erreurs_par_type.longueur_incorrecte ← +1
                    CONTAINS "33":
                        statistics.erreurs_par_type.ne_commence_pas_33 ← +1
                    CONTAINS "invalides":
                        statistics.erreurs_par_type.caracteres_invalides ← +1
                    DEFAULT:
                        statistics.erreurs_par_type.autre ← +1
                END CASE
            END FOR
        END IF
        
        // Étape 7: Compter par utilisateur
        IF utilisateur NOT IN statistics.envois_par_utilisateur THEN
            statistics.envois_par_utilisateur[utilisateur] ← 0
        END IF
        statistics.envois_par_utilisateur[utilisateur] ← +1
        
        IF NOT validation.is_valid THEN
            IF utilisateur NOT IN statistics.erreurs_par_utilisateur THEN
                statistics.erreurs_par_utilisateur[utilisateur] ← 0
            END IF
            statistics.erreurs_par_utilisateur[utilisateur] ← +1
        END IF
        
    END FOR
    
    // Étape 8: Calculer le taux de réussite
    IF statistics.total_fax > 0 THEN
        reussis ← statistics.total_fax - statistics.erreurs_totales
        statistics.taux_reussite ← (reussis / statistics.total_fax) * 100
    ELSE
        statistics.taux_reussite ← 0.0
    END IF
    
    // Étape 9: Retourner le résultat
    RETURN {
        entries: entries,
        statistics: statistics,
        contract_id: contract_id,
        date_debut: date_debut,
        date_fin: date_fin
    }

END FUNCTION
```

### Formule du taux de réussite

$$\text{Taux de réussite} = \frac{\text{Total FAX} - \text{Erreurs}}{\text{Total FAX}} \times 100$$

**Exemple**:
- Total: 150 FAX
- Erreurs: 12
- Réussis: 150 - 12 = 138
- Taux: (138 / 150) × 100 = 92%

---

## 5️⃣ GÉNÉRATION QR CODE (reporter.py)

### Pseudo-code détaillé

```pseudocode
FUNCTION generate_qr_code(
    report_id: STRING,
    base_url: STRING = "http://localhost/reports"
) -> STRING

INPUT:
    report_id: "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
    base_url: "http://localhost/reports"

OUTPUT: chemin du fichier PNG généré
    "reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png"

PROCESS:

    // Étape 1: Vérifier et créer le dossier
    IF NOT directory_exists("reports_qr") THEN
        CREATE_DIRECTORY("reports_qr")
    END IF
    
    // Étape 2: Construire l'URL cible
    target_url ← base_url + "/" + report_id
    // "http://localhost/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
    
    // Étape 3: Initialiser le générateur QR
    qr_generator ← INITIALIZE_QRCODE_GENERATOR()
    SET qr_generator.version ← 1              // Taille minimale
    SET qr_generator.error_correction ← HIGH  // ERROR_CORRECT_H
    SET qr_generator.box_size ← 10            // Pixels par boîte
    SET qr_generator.border ← 4               // Pixels de bordure
    
    // Étape 4: Ajouter les données
    ADD_DATA_TO_QR(qr_generator, target_url)
    FIT_QR(qr_generator)  // Ajuster la taille automatiquement
    
    // Étape 5: Générer l'image
    image ← qr_generator.make_image()
    SET image.fill_color ← "black"
    SET image.back_color ← "white"
    
    // Étape 6: Construire le chemin de sortie
    file_path ← "reports_qr/" + report_id + ".png"
    // "reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png"
    
    // Étape 7: Sauvegarder le fichier
    SAVE_IMAGE(image, file_path)
    
    // Étape 8: Retourner le chemin
    RETURN file_path

END FUNCTION
```

### Structure du QR code

```
┌───────────────────────┐
│ ███████   ███   █████ │
│ █ URL  █  QR   █ IMG │
│ █ LOC  █  DATA █     │
│ █      █  CODE █     │
│ █████████████████    │
│ █ BLACK on WHITE     │
│ ███████████████████  │
└───────────────────────┘

Contenu décodé:
→ http://localhost/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6

Quand scanné:
→ Ouvre le navigateur
→ Récupère le rapport JSON
→ Affiche les statistiques
```

---

## 6️⃣ GESTION BASE DE DONNÉES (db.py)

### Pseudo-code initialisation

```pseudocode
FUNCTION init_database(db_path: STRING = "database/faxcloud.db")

INPUT: db_path (chemin du fichier SQLite)

OUTPUT: Aucun (crée la base de données)

PROCESS:

    // Étape 1: Vérifier/créer le dossier
    IF NOT directory_exists("database") THEN
        CREATE_DIRECTORY("database")
    END IF
    
    // Étape 2: Établir la connexion
    connection ← CONNECT_TO_SQLITE(db_path)
    cursor ← CREATE_CURSOR(connection)
    
    // Étape 3: Créer la table 'reports'
    EXECUTE cursor: """
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            date_rapport TEXT NOT NULL,
            contract_id TEXT NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL,
            fichier_source TEXT,
            total_fax INTEGER NOT NULL,
            fax_envoyes INTEGER NOT NULL,
            fax_recus INTEGER NOT NULL,
            pages_totales INTEGER NOT NULL,
            erreurs_totales INTEGER NOT NULL,
            taux_reussite REAL NOT NULL,
            qr_path TEXT NOT NULL,
            url_rapport TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(id)
        )
    """
    
    // Étape 4: Créer la table 'fax_entries'
    EXECUTE cursor: """
        CREATE TABLE IF NOT EXISTS fax_entries (
            id TEXT PRIMARY KEY,
            report_id TEXT NOT NULL,
            fax_id TEXT NOT NULL,
            utilisateur TEXT NOT NULL,
            type TEXT NOT NULL,
            numero_original TEXT,
            numero_normalise TEXT,
            valide BOOLEAN NOT NULL,
            pages INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            erreurs TEXT,
            FOREIGN KEY (report_id) REFERENCES reports(id),
            UNIQUE(id)
        )
    """
    
    // Étape 5: Créer les indexes
    EXECUTE cursor: """
        CREATE INDEX IF NOT EXISTS idx_reports_contract 
        ON reports(contract_id)
    """
    
    EXECUTE cursor: """
        CREATE INDEX IF NOT EXISTS idx_reports_created 
        ON reports(created_at)
    """
    
    EXECUTE cursor: """
        CREATE INDEX IF NOT EXISTS idx_fax_entries_report 
        ON fax_entries(report_id)
    """
    
    EXECUTE cursor: """
        CREATE INDEX IF NOT EXISTS idx_fax_entries_utilisateur 
        ON fax_entries(utilisateur)
    """
    
    // Étape 6: Valider et fermer
    COMMIT(connection)
    CLOSE(cursor)
    CLOSE(connection)
    
    LOG "Base de données initialisée: " + db_path

END FUNCTION
```

### Pseudo-code insertion

```pseudocode
FUNCTION insert_report_to_db(
    report_id: STRING,
    report_json: DICTIONARY,
    qr_path: STRING
)

INPUT:
    report_id: UUID
    report_json: Dictionnaire du rapport complet
    qr_path: "reports_qr/[report_id].png"

OUTPUT: Aucun (sauvegarde en base)

PROCESS:

    // Étape 1: Établir la connexion
    connection ← CONNECT_TO_SQLITE("database/faxcloud.db")
    cursor ← CREATE_CURSOR(connection)
    
    // Étape 2: Insérer le rapport principal
    statistics ← report_json.statistics
    
    EXECUTE cursor: """
        INSERT INTO reports (
            id, date_rapport, contract_id, date_debut, date_fin,
            total_fax, fax_envoyes, fax_recus, pages_totales,
            erreurs_totales, taux_reussite, qr_path, url_rapport,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """ WITH PARAMETERS (
        report_id,
        report_json.timestamp,
        report_json.contract_id,
        report_json.date_debut,
        report_json.date_fin,
        statistics.total_fax,
        statistics.fax_envoyes,
        statistics.fax_recus,
        statistics.pages_totales,
        statistics.erreurs_totales,
        statistics.taux_reussite,
        qr_path,
        report_json.report_url,
        NOW()
    )
    
    // Étape 3: Insérer les entrées FAX
    FOR EACH entry IN report_json.entries DO
        
        erreurs_json ← CONVERT_TO_JSON(entry.erreurs)
        
        EXECUTE cursor: """
            INSERT INTO fax_entries (
                id, report_id, fax_id, utilisateur, type,
                numero_original, numero_normalise, valide, pages,
                datetime, erreurs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """ WITH PARAMETERS (
            entry.id,
            report_id,
            entry.fax_id,
            entry.utilisateur,
            entry.type,
            entry.numero_original,
            entry.numero_normalise,
            entry.valide,
            entry.pages,
            entry.datetime,
            erreurs_json
        )
    
    END FOR
    
    // Étape 4: Valider et fermer
    COMMIT(connection)
    CLOSE(cursor)
    CLOSE(connection)
    
    LOG "Rapport inséré: " + report_id

END FUNCTION
```

### Pseudo-code consultation

```pseudocode
FUNCTION get_all_reports() -> LIST[DICTIONARY]

PROCESS:
    connection ← CONNECT_TO_SQLITE("database/faxcloud.db")
    cursor ← CREATE_CURSOR(connection)
    
    EXECUTE cursor: """
        SELECT * FROM reports ORDER BY created_at DESC
    """
    
    reports ← FETCH_ALL(cursor)
    CLOSE(cursor)
    CLOSE(connection)
    
    RETURN reports

END FUNCTION

---

FUNCTION get_report_by_id(report_id: STRING) -> DICTIONARY

PROCESS:
    connection ← CONNECT_TO_SQLITE("database/faxcloud.db")
    cursor ← CREATE_CURSOR(connection)
    
    EXECUTE cursor: """
        SELECT * FROM reports WHERE id = ?
    """ WITH PARAMETERS (report_id)
    
    report ← FETCH_ONE(cursor)
    
    EXECUTE cursor: """
        SELECT * FROM fax_entries WHERE report_id = ?
    """ WITH PARAMETERS (report_id)
    
    entries ← FETCH_ALL(cursor)
    
    CLOSE(cursor)
    CLOSE(connection)
    
    RETURN {
        report: report,
        entries: entries
    }

END FUNCTION
```

---

## 7️⃣ API WEB (main.py - routes)

### Pseudo-code API REST

```pseudocode
// Routes HTTP

GET /
    → Servir index.html (Dashboard)
    → Récupérer tous les rapports
    → Afficher la liste en HTML/JSON

---

GET /reports
    → Retourner JSON: LIST[DICTIONARY]
    Réponse:
    {
        reports: [
            {
                id: "...",
                date_rapport: "...",
                contract_id: "...",
                total_fax: 150,
                fax_envoyes: 95,
                fax_recus: 55,
                erreurs_totales: 12,
                taux_reussite: 92.0,
                qr_path: "/reports_qr/..."
            },
            ...
        ]
    }

---

GET /reports/<report_id>
    → Récupérer le rapport complet
    → Retourner JSON du rapport
    Réponse:
    {
        report_id: "...",
        timestamp: "...",
        statistics: { ... },
        entries: [ ... ],
        qr_code_url: "/reports_qr/...",
        report_url: "/reports/..."
    }

---

GET /reports/<report_id>/html
    → Servir report.html avec les données injectées
    → Afficher rapport formaté avec statistiques

---

POST /import
    INPUT: FormData
    {
        file: <fichier CSV/XLSX>,
        contract_id: "CONTRACT_001",
        date_debut: "2024-12-01",
        date_fin: "2024-12-31"
    }
    
    PROCESS:
        1. Sauvegarder le fichier
        2. Importer les données
        3. Analyser
        4. Générer rapport
        5. Insérer en base
    
    OUTPUT:
    {
        success: TRUE,
        report_id: "...",
        qr_path: "/reports_qr/...",
        redirect_url: "/reports/..."
    }

---

GET /reports_qr/<report_id>.png
    → Servir l'image PNG du QR code

---

GET /api/stats
    → Retourner les statistiques globales
    Réponse:
    {
        total_reports: 15,
        total_fax: 2345,
        total_errors: 123,
        avg_success_rate: 94.75,
        users_count: 12
    }
```

---

## 8️⃣ DIAGRAMME DE FLUX COMPLET

```
┌─────────────────────────────────────────────────────────┐
│                   UTILISATEUR                           │
│            (Interface Web / CLI)                        │
└──────────────────────────────┬──────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   1. IMPORTER       │
                    │  (importer.py)      │
                    │                     │
                    │ • Lire CSV/XLSX     │
                    │ • Valider structure │
                    │ • Normaliser        │
                    └──────────┬──────────┘
                               │
                     ┌─────────▼─────────┐
                     │ DONNÉES BRUTES    │
                     │   (Dictionnaire)  │
                     └─────────┬─────────┘
                               │
                    ┌──────────▼──────────┐
                    │   2. ANALYSER       │
                    │  (analyzer.py)      │
                    │                     │
                    │ • Normaliser nums   │
                    │ • Valider           │
                    │ • Calculer stats    │
                    └──────────┬──────────┘
                               │
                     ┌─────────▼──────────────┐
                     │ RÉSULTATS ANALYSÉS    │
                     │ (entries + stats)     │
                     └─────────┬──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  3. RAPPORTER       │
                    │  (reporter.py)      │
                    │                     │
                    │ • Générer UUID      │
                    │ • Créer QR code     │
                    │ • Formater JSON     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼────┐          ┌─────▼──────┐         ┌─────▼──────┐
   │ JSON    │          │ QR Code    │         │ Base de    │
   │ Rapport │          │ PNG        │         │ données    │
   └────┬────┘          └─────┬──────┘         └─────┬──────┘
        │                     │                      │
        └─────────────────────┼──────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  4. PRÉSENTATION   │
                    │ (Interface Web)    │
                    │                    │
                    │ • Dashboard        │
                    │ • Détail rapport   │
                    │ • Lecteur QR       │
                    └────────────────────┘
```

---

## 9️⃣ EXEMPLE D'EXÉCUTION PAS À PAS

### Entrée
```csv
Fax ID;Nom et prénom utilisateur;Mode;Date et heure du fax;Numéro appelé;Nombre de pages réel
FAX001;Jean Dupont;SF;2024-12-10 14:30:00;0622334455;5
FAX002;Marie Martin;RF;2024-12-10 15:45:00;0133445566;3
FAX003;Pierre Leblanc;SF;2024-12-10 16:20:00;INVALID;0
```

### Étape 1: Normalisation (analyzer.py)

| Numéro brut | Processus | Résultat |
|-------------|-----------|----------|
| `0622334455` | Retire non-num → `0622334455` → Remplace 0 par 33 | `33622334455` |
| `0133445566` | Retire non-num → `0133445566` → Remplace 0 par 33 | `33133445566` |
| `INVALID` | Retire non-num → `` (vide) | `` |

### Étape 2: Validation (analyzer.py)

| Numéro normalisé | Longueur | Commence 33 ? | Valide | Erreurs |
|-----------------|----------|---------------|--------|---------|
| `33622334455` | 11 ✓ | Oui ✓ | **OUI** | Aucune |
| `33133445566` | 11 ✓ | Oui ✓ | **OUI** | Aucune |
| `` | 0 ✗ | Non ✗ | **NON** | Numéro vide |

### Étape 3: Analyse des statistiques

```
total_fax: 3
fax_envoyes: 2 (FAX001, FAX003)
fax_recus: 1 (FAX002)
pages_totales: 8 (5 + 3 + 0)
erreurs_totales: 1 (FAX003)
taux_reussite: (3-1)/3 * 100 = 66.67%

envois_par_utilisateur:
  Jean Dupont: 1
  Marie Martin: 1
  Pierre Leblanc: 1

erreurs_par_utilisateur:
  Pierre Leblanc: 1
```

### Étape 4: Génération rapport

```
report_id: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
qr_code_url: http://localhost/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
qr_file: reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png
```

### Étape 5: Stockage base de données

```sql
INSERT INTO reports VALUES (
    'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
    '2024-12-10T17:00:00',
    'CONTRACT_001',
    '2024-12-01',
    '2024-12-31',
    'export_faxcloud.csv',
    3, 2, 1, 8, 1, 66.67,
    'reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png',
    '/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
    '2024-12-10T17:00:00'
);

INSERT INTO fax_entries VALUES (
    'entry-uuid-1', 'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
    'FAX001', 'Jean Dupont', 'send',
    '0622334455', '33622334455', TRUE, 5,
    '2024-12-10T14:30:00', '[]'
);
-- ... (2 autres entrées)
```

### Sortie finale

```json
{
  "success": true,
  "report_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "qr_path": "reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png",
  "report_url": "http://localhost:8000/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
}
```

---

**Document généré**: 2024-12-10
**Complexité**: O(n) pour l'analyse (n = nombre de lignes)
**Mémoire**: O(n) pour stocker les entrées
