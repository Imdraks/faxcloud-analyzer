-- =============================================================================
-- FaxCloud Analyzer - Optimisations MySQL
-- Exécuter ce script dans phpMyAdmin pour optimiser les performances
-- =============================================================================

USE faxcloud_analyzer;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. AJOUTER LES INDEX POUR LA RECHERCHE
-- ─────────────────────────────────────────────────────────────────────────────

-- Index sur fax_id pour recherche rapide
CREATE INDEX idx_fax_id ON fax_entries(fax_id(20));

-- Index sur utilisateur pour filtrer par utilisateur
CREATE INDEX idx_utilisateur ON fax_entries(utilisateur(50));

-- Index sur numero pour chercher les numéros
CREATE INDEX idx_numero ON fax_entries(numero_original(20), numero_normalise(20));

-- Index sur la date pour trier chronologiquement (sans DESC, MySQL l'ignore)
CREATE INDEX idx_date_heure ON fax_entries(date_heure);

-- Index sur le mode (SF/RF/FAX) pour filtrer
CREATE INDEX idx_mode ON fax_entries(mode);

-- Index sur valide (pour les erreurs)
CREATE INDEX idx_valide ON fax_entries(valide);

-- Index composite optimisé pour pagination + recherche + filtrage
CREATE INDEX idx_report_filter ON fax_entries(report_id, valide, utilisateur(50));

-- Index composé pour recherche avec tri par date
CREATE INDEX idx_search_date ON fax_entries(fax_id(20), utilisateur(50), numero_original(20), date_heure);

-- Index sur report_id + date pour les requêtes ORDER BY récentes
CREATE INDEX idx_report_date ON fax_entries(report_id, date_heure);

-- Index pour les statistiques rapides (count par mode/valide)
CREATE INDEX idx_mode_valide ON fax_entries(mode, valide);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. OPTIMISER LA TABLE ANALYSIS_HISTORY
-- ─────────────────────────────────────────────────────────────────────────────

-- Index sur la date pour trier les rapports récents
CREATE INDEX idx_analysis_created_at ON analysis_history(created_at);

-- Index sur l'ID analyse
CREATE INDEX idx_analysis_id ON analysis_history(analysis_id);

-- Index composite pour rapports récents avec ID
CREATE INDEX idx_analysis_recent ON analysis_history(created_at, analysis_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. AFFICHER LES STATISTIQUES DES INDEX
-- ─────────────────────────────────────────────────────────────────────────────

-- Vérifier que tous les index ont été créés
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    SEQ_IN_INDEX,
    COLUMN_NAME,
    NON_UNIQUE,
    CARDINALITY
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME IN ('fax_entries', 'analysis_history')
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. VÉRIFIER LA TAILLE DE LA TABLE
-- ─────────────────────────────────────────────────────────────────────────────

SELECT 
    TABLE_NAME,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as 'Size (MB)',
    ROUND((data_free / 1024 / 1024), 2) as 'Free Space (MB)',
    TABLE_ROWS as 'Rows'
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME IN ('fax_entries', 'analysis_history');

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. ANALYSER LA TABLE (améliore les performances des requêtes)
-- ─────────────────────────────────────────────────────────────────────────────

ANALYZE TABLE fax_entries;
ANALYZE TABLE analysis_history;

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. ACTIVER LES QUERY CACHE ET OPTIMISER LE SERVEUR
-- ─────────────────────────────────────────────────────────────────────────────
-- À exécuter sur localhost, pas accessible via phpMyAdmin

-- Pour WampServer, editer C:\wamp64\bin\mysql\mysql8.0.x\my.ini:
-- [mysqld]
-- query_cache_type = 1
-- query_cache_size = 64M
-- max_connections = 200
-- innodb_buffer_pool_size = 256M
-- innodb_log_file_size = 100M

-- ═════════════════════════════════════════════════════════════════════════════
-- INSTRUCTIONS:
-- 1. Ouvrir phpMyAdmin
-- 2. Aller à l'onglet "SQL"
-- 3. Copier/coller ce script
-- 4. Exécuter
-- Les index seront créés et les performances améliorées drastiquement!
-- ═════════════════════════════════════════════════════════════════════════════
