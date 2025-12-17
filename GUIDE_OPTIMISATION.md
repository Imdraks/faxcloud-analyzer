# 📘 Guide d'Exécution - Optimisation MySQL FaxCloud

## 🎯 Objectif
Optimiser les performances en supprimant les index doublons et inefficaces, puis ajouter des index composés pour accélérer les requêtes de pagination et recherche.

---

## ⚙️ ÉTAPE 1: Ouvrir phpMyAdmin

1. Aller à: **http://localhost/phpmyadmin**
2. Se connecter avec vos identifiants (root/password par défaut)
3. Sélectionner la base **faxcloud_analyzer** dans le menu de gauche

---

## 📋 ÉTAPE 2: Accéder à l'éditeur SQL

1. Cliquer sur l'onglet **SQL** en haut
2. Vous verrez un grand champ de texte blanc pour les requêtes SQL

---

## 🔍 ÉTAPE 3: Copier le script d'optimisation

1. Ouvrir le fichier: `optimize_mysql.sql`
2. **Sélectionner tout** (Ctrl+A)
3. **Copier** (Ctrl+C)

---

## ✏️ ÉTAPE 4: Coller dans phpMyAdmin

1. Revenir à phpMyAdmin (onglet SQL)
2. **Cliquer dans le champ blanc**
3. **Coller** le script (Ctrl+V)

---

## ▶️ ÉTAPE 5: Exécuter le script

1. **Cliquer le bouton "Exécuter"** (ou appuyer sur Ctrl+Entrée)
2. Attendre quelques secondes...

---

## 📊 ÉTAPE 6: Vérifier les résultats

Le script va afficher **plusieurs résultats**:

### ✅ Résultat 1: INDEX AVANT
- Voir les index existants avant optimisation
- Regarder les colonnes (INDEX_NAME, COLUMN_NAME)

### ✅ Résultat 2: Suppressions
- Les DROP vont silencieusement supprimer les doublons
- (Pas d'erreur = normal, ils n'existaient pas tous)

### ✅ Résultat 3: Créations
- Les CREATE IF NOT EXISTS vont créer les nouveaux index
- (Pas d'erreur = succès)

### ✅ Résultat 4: ANALYZE
- Les tables sont analysées
- (Vise à optimiser l'utilisation des index)

### ✅ Résultat 5: INDEX APRÈS
- **Affiche les index optimisés**
- Comparer avec le Résultat 1 pour voir les améliorations
- **CARDINALITY** = efficacité de l'index (plus haut = mieux)

### ✅ Résultat 6: Taille des tables
- Voir la taille des tables en MB
- Nombre de lignes (TABLE_ROWS)

---

## 🎯 Que faire si vous voyez des erreurs?

### Erreur: "Table 'faxcloud_analyzer.fax_entries' doesn't exist"
- ✗ Vous n'êtes pas dans la bonne base
- ✓ Sélectionner **faxcloud_analyzer** dans le menu gauche

### Erreur: "Syntax error near..."
- ✗ Le SQL n'a pas été copié entièrement
- ✓ Essayer à nouveau, copier le fichier entier

### Erreur: "Can't drop index; check that it exists"
- ✗ L'index n'existait pas
- ✓ Normal! Le script utilise `DROP IF EXISTS` pour éviter cette erreur

### Pas d'erreur mais rien ne s'affiche
- ✓ C'est normal! Les DROP et CREATE n'affichent rien
- ✓ Regarder les SELECTs pour les résultats

---

## 🔍 Comment vérifier que ça a marché?

Après exécution, regarder les résultats SELECT:

### Résultat 1 vs Résultat 5:
- Les doublons doivent avoir disparu
- Les nouveaux index composés doivent être présents:
  - `idx_pagination` ✓
  - `idx_search_multi` ✓
  - `idx_stats` ✓

### Comparer les INDEX_NAME:
```
AVANT:                      APRÈS:
idx_fax_id                  idx_fax_id ✓
idx_utilisateur             idx_utilisateur ✓
idx_date_heure (DESC)       idx_date_heure (sans DESC) ✓
idx_pagination              idx_pagination ✓ (NOUVEAU)
idx_search_multi            idx_search_multi ✓ (NOUVEAU)
idx_stats                   idx_stats ✓ (NOUVEAU)
```

---

## 🚀 Étape 7: Redémarrer le serveur Flask

Pour que les optimisations prennent effet:

```bash
# Fermer le serveur web (Ctrl+C dans le terminal)
# Puis relancer:
run-web.bat
```

---

## 📈 Impact esperé

**Avant optimisation:**
- Pagination: 1-2 secondes
- Recherche: 1-2 secondes
- Statistiques: 500ms

**Après optimisation:**
- Pagination: 50-100ms (-95%)
- Recherche: 50ms (-95%)
- Statistiques: 10-50ms (-90%)

---

## 💡 Configuration WampServer (Optionnel)

Pour une performance MAXIMALE, éditer `C:\wamp64\bin\mysql\mysql8.0.x\my.ini`:

```ini
[mysqld]
# Performance
innodb_buffer_pool_size = 256M
innodb_log_file_size = 100M
max_connections = 200
query_cache_type = 1
query_cache_size = 64M
sort_buffer_size = 2M
join_buffer_size = 2M
```

Puis **redémarrer WampServer**.

---

## ✅ Checklist Final

- [ ] Copier `optimize_mysql.sql`
- [ ] Ouvrir phpMyAdmin
- [ ] Sélectionner base `faxcloud_analyzer`
- [ ] Coller dans onglet SQL
- [ ] Exécuter le script
- [ ] Vérifier les résultats (INDEX AVANT/APRÈS)
- [ ] Redémarrer le serveur Flask
- [ ] Tester la pagination et recherche

---

*Guide créé le 17 Dec 2025 - FaxCloud Analyzer v2.0*
