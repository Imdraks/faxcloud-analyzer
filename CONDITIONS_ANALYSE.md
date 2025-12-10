# 📋 CONDITIONS D'ANALYSE (VERSION OFFICIELLE)

**Document de référence pour le moteur d'analyse FaxCloud**

---

## 🔹 1. Type d'événement FAX (envoyé / reçu)

Basé sur la **colonne D (Mode)** :

| Mode | Type | Description |
|------|------|-------------|
| **SF** | Fax envoyé | Send Fax |
| **RF** | Fax reçu | Receive Fax |

**Exemple:**
```
Mode: SF → Compte comme "fax envoyé"
Mode: RF → Compte comme "fax reçu"
```

---

## 🔹 2. Identification du numéro appelé (Colonne H)

C'est l'élément **principal** pour détecter les erreurs.

Le numéro doit respecter **toutes les règles** suivantes (dans cet ordre):

### ✔️ Règle 1 — Normalisation

**Avant l'analyse, retirer tout ce qui n'est pas un chiffre.**

| Format original | Après normalisation | Raison |
|---|---|---|
| `03.27.93.69.43` | `0327936943` | Points retirés |
| `+33 1 45 22 11 34` | `33145221134` | Espaces retirés, +33 → 33 |
| `+33-1-45-22-11-34` | `33145221134` | Tirets retirés |
| `0033145221134` | `33145221134` | Zéros retirés en début |
| `(0)145221134` | `0145221134` | Parenthèses retirées |

**Exemple en code:**
```python
numero_brut = "+33 1 45 22 11 34"
numero_normalise = re.sub(r'\D', '', numero_brut)  # Garde que les chiffres
# Résultat: "33145221134"
```

### ✔️ Règle 2 — Longueur exacte = 11 chiffres

Un numéro valide doit avoir **exactement 11 caractères numériques**.

| Numéro | Longueur | Valide ? | Motif |
|---|---|---|---|
| `33145221134` | 11 | ✔️ | OK |
| `0145221134` | 10 | ❌ | Trop court |
| `0033145221134` | 13 | ❌ | Trop long |
| `331452211` | 9 | ❌ | Trop court |

**Règle:** `len(numero_normalise) == 11`

### ✔️ Règle 3 — Le numéro doit commencer par 33

C'est l'**indicateur international pour la France**.

| Numéro | Commence par 33 ? | Valide ? |
|---|---|---|
| `33145221134` | ✔️ | OK |
| `0145221134` | ❌ | Erreur |
| `+33145221134` | (après normalisation → OK) | OK |
| `33(1)45221134` | (après normalisation → OK) | OK |

**Règle:** `numero_normalise.startswith("33")`

**IMPORTANT:** Les numéros commençant par `0` doivent être convertis:
- `01XXXXXXXX` → `3301XXXXXXXX` (supprimer le 0, ajouter 33)
- `02XXXXXXXX` → `3302XXXXXXXX`

### ✔️ Règle 4 — Le numéro doit être identifié comme FAX (Asterisk)

**Phase actuelle (v1):**
- Cette étape est **fictive**
- On considère "fax valide" si les trois règles ci-dessus sont respectées

**Phase évoluée (v2+):**
- Une requête **Asterisk** validera réellement si le numéro correspond à une ligne FAX (vs voix)

---

## 🔹 3. Détection des erreurs

Un numéro est considéré comme **erroné** si **UNE SEULE** de ces conditions échoue:

### ❌ Erreur 1 → Numéro vide ou null

**Cas d'erreur:**
- Champ complètement vide
- Contenant autre chose que des chiffres (après normalisation)
- Seulement des espaces/tirets/caractères spéciaux

**Code:**
```python
if not numero_normalise or len(numero_normalise) == 0:
    erreur = "Numéro vide"
```

### ❌ Erreur 2 → Longueur ≠ 11

**Cas d'erreur:**
- Moins de 11 chiffres
- Plus de 11 chiffres

**Exemples:**
- `0145221134` → 10 chiffres → ❌ Erreur
- `0033145221134` → 13 chiffres → ❌ Erreur

**Code:**
```python
if len(numero_normalise) != 11:
    erreur = "Longueur incorrecte"
```

### ❌ Erreur 3 → Ne commence pas par 33

**Cas d'erreur:**
- Commence par `0`
- Commence par `+33` avant normalisation (accepté après normalisation)
- Commence par `0033` (incorrect, contient trop de 0)

**Exemples:**
- `0145221134` → Commence par 0 → ❌ Erreur
- `+33145221134` → Avant normalisation: commence par +33 → **Acceptable** (se normalise en 33145221134)

**Code:**
```python
if not numero_normalise.startswith("33"):
    erreur = "Indicatif invalide (doit commencer par 33)"
```

### ❌ Erreur 4 → Ligne non analysable

**Cas d'erreur:**
- Caractères illisibles/corrompus
- Format anormal (suite de caractères étranges)
- Données manquantes dans la ligne CSV

**Exemple:**
- `🔥🎉🔥` (emojis)
- `\x00\x01\x02` (caractères de contrôle)

**Code:**
```python
try:
    numero_normalise = re.sub(r'\D', '', str(numero_brut))
except Exception:
    erreur = "Format invalide"
```

### ❌ Erreur 5 → Futur : ligne détectée comme "voix" par Asterisk

**(Pas encore activé - Phase v2+)**

Sera utilisé quand Asterisk est intégré.

---

## 🔹 4. Nombre de pages (Colonne K)

### Extraction

1. **Convertir en entier:**
   ```python
   pages = int(colonne_K)
   ```

2. **Si vide ou non numérique:**
   ```python
   if not pages or pages < 0:
       erreur_page = "Nombre de pages invalide"
   ```

### Utilisation dans les statistiques

```python
total_pages += pages

if mode == "SF":  # Fax envoyé
    pages_envoyees += pages
elif mode == "RF":  # Fax reçu
    pages_recues += pages
```

---

## 🔹 5. Statistiques obligatoires à produire

### 📊 Global

| Métrique | Calcul | Exemple |
|---|---|---|
| **Total FAX envoyés** | Compte tous les mode="SF" | 1,250 |
| **Total FAX reçus** | Compte tous les mode="RF" | 890 |
| **Total pages envoyées** | Sum(pages) où mode="SF" | 5,432 pages |
| **Total pages reçues** | Sum(pages) où mode="RF" | 3,210 pages |
| **Total pages globales** | pages_envoyees + pages_recues | 8,642 pages |
| **Taux de réussite** | (fax_valides / fax_total) × 100 | 94.2% |

**Formule du taux:**
```python
taux_reussite = (fax_valides / total_fax) * 100
```

### 📊 Erreurs

| Métrique | Description | Exemple |
|---|---|---|
| **Nombre total d'erreurs** | Somme de toutes les erreurs | 156 |
| **Erreurs par type** | Histogramme des types | Voir ci-dessous |

**Histogramme des erreurs:**
```
Erreur 1 (Numéro vide): 45 occurrences
Erreur 2 (Longueur incorrecte): 78 occurrences
Erreur 3 (Mauvais indicatif): 23 occurrences
Erreur 4 (Format invalide): 10 occurrences
Total: 156 erreurs
```

### 📊 Par utilisateur

**Basé sur la colonne B (Utilisateur):**

| Utilisateur | Envois | Erreurs | Taux réussite | Pages |
|---|---|---|---|---|
| Alice Dupont | 145 | 8 | 94.5% | 820 pages |
| Bob Martin | 98 | 5 | 94.9% | 560 pages |
| Carol Leblanc | 112 | 14 | 87.5% | 640 pages |

**Calcul par utilisateur:**
```python
par_utilisateur[user] = {
    'total': count,
    'erreurs': error_count,
    'taux_reussite': ((count - error_count) / count) * 100,
    'pages': sum_pages
}
```

---

## 🔹 6. ID unique et QR code

### ID Unique

Chaque rapport analysé obtient un **UUIDv4**:

```python
import uuid
report_id = uuid.uuid4()  # Exemple: "550e8400-e29b-41d4-a716-446655440000"
```

### QR Code

Le QR code pointe vers:

```
http://localhost:8000/reports/<uuid>
```

Exemple complet:
```
http://localhost:8000/reports/550e8400-e29b-41d4-a716-446655440000
```

### Sauvegarde

Le QR code est enregistré en **PNG**:

```
./data/reports_qr/<uuid>.png
```

Chemin complet:
```
./data/reports_qr/550e8400-e29b-41d4-a716-446655440000.png
```

---

## 💡 Résumé ultra-court

### Pseudo-code de validation

```python
def valider_numero(numero_brut):
    """
    Valide un numéro selon les règles officielles
    Retourne: (est_valide: bool, erreur: str)
    """
    
    # Étape 1: Normalisation
    numero = re.sub(r'\D', '', str(numero_brut))
    
    # Étape 2: Vérification du vide
    if not numero:
        return False, "Numéro vide"
    
    # Étape 3: Conversion 0X → 33X
    if numero.startswith("0"):
        numero = "33" + numero[1:]
    
    # Étape 4: Vérification longueur
    if len(numero) != 11:
        return False, "Longueur incorrecte"
    
    # Étape 5: Vérification indicatif
    if not numero.startswith("33"):
        return False, "Indicatif invalide"
    
    # Étape 6: All good!
    return True, None
```

### Exemple d'utilisation

```python
# Test 1: Numéro valide
valider_numero("+33 1 45 22 11 34")  
# → (True, None)

# Test 2: Numéro avec 0 en début
valider_numero("01 45 22 11 34")  
# → (True, None)  [converti en 3301452211134, wait → erreur de longueur!]

# Test 3: Numéro vide
valider_numero("")  
# → (False, "Numéro vide")

# Test 4: Mauvaise longueur
valider_numero("0145221134")  
# → (False, "Longueur incorrecte")  [10 chiffres]

# Test 5: Mauvais indicatif
valider_numero("+1 (212) 555-1234")  
# → (False, "Indicatif invalide")
```

---

## 📝 Checklist d'implémentation

- [ ] Normalisation: retirer caractères non-numériques
- [ ] Conversion 0X → 33X
- [ ] Vérification longueur = 11
- [ ] Vérification indicatif = 33
- [ ] Génération UUID pour chaque rapport
- [ ] Génération QR code PNG
- [ ] Calcul statistiques globales
- [ ] Calcul statistiques par erreur
- [ ] Calcul statistiques par utilisateur
- [ ] Enregistrement en base de données MySQL
- [ ] Export rapports JSON
- [ ] Interface affichage résultats

---

## 🔄 Versions du projet

| Version | Statut | Validation Asterisk | Détails |
|---|---|---|---|
| **v1** | ✅ Actuelle | ❌ Non | Validation basée sur format uniquement |
| **v2** | 🔜 Planifiée | ✔️ Oui | Intégration Asterisk pour FAX réels |
| **v3** | 📅 Futur | ✔️ + API | Webhooks, notifications email |

---

**Dernière mise à jour:** 10 décembre 2025  
**Document officiel pour:** FaxCloud Analyzer v1.0
