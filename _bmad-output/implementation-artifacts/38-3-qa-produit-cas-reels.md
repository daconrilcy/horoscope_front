Status: done

## Story

As a product owner de l'application horoscope,
I want une phase de QA métier documentée avec des cas de test sur profils variés et une grille d'évaluation structurée,
so that la feature de prédiction quotidienne est validée en usage réel avant release, avec un backlog d'ajustements et une décision explicite de go/no-go.

## Acceptance Criteria

### AC1 — Au moins 5 cas de QA sur profils variés

[x] Le script `generate_qa_cases.py` génère au minimum 5 cas de test couvrant des signes différents et des dates différentes. Chaque cas produit un payload complet de prédiction.

### AC2 — Checklist remplie sur 6 dimensions

[x] Le rapport QA rempli évalue chaque cas sur les 6 dimensions : compréhensible, cohérent avec la journée, trop vague, trop alarmiste, pivots crédibles, timeline utile. Chaque dimension est notée (OK / KO / N/A) avec commentaire libre.

### AC3 — Anomalies documentées avec code catégorie, note, et description

[x] Toute anomalie identifiée lors de la QA est enregistrée avec : code catégorie (`VAGUE`, `ALARME`, `INCOHERENT`, `PIVOT_FAIBLE`, `TIMELINE_VIDE`, `AUTRE`), note (1-20), et description en langage naturel.

### AC4 — Backlog d'ajustements produit créé

[x] `docs/qa/product-adjustments-backlog.md` liste les ajustements produit identifiés, classés par priorité (P0 bloquant / P1 important / P2 amélioration).

### AC5 — Décision explicite go/no-go

[x] Le rapport QA contient une section "Décision" avec une des deux valeurs : `validé pour release` ou `bloquant identifié`, suivie d'une justification d'une phrase.

## Tasks / Subtasks

### T1 — Créer la checklist QA (AC2)

- [x] Créer `docs/qa/daily-prediction-checklist.md` avec :
  - [x] Introduction : objectif, date de la QA, profils testés
  - [x] Grille des 6 dimensions pour chaque cas de test :
    - `compréhensible ?` — le texte est lisible et clair pour un non-astrologue
    - `cohérent avec la journée ?` — les conseils semblent plausibles pour la date testée
    - `trop vague ?` — le texte ne dit rien d'actionnable
    - `trop alarmiste ?` — le ton inquiète sans raison proportionnée
    - `pivots crédibles ?` — les pivots horaires semblent plausibles et utiles
    - `timeline utile ?` — la répartition des blocs horaires apporte de la valeur
  - [x] Colonne de décision par cas : `validé` / `à retravailler` / `bloquant`

### T2 — Créer le script de génération des cas QA (AC1) — via couche service, pas API publique

- [x] Créer `backend/app/jobs/qa/generate_qa_cases.py` (Option A) :
  - [x] S'appuyer sur les fixtures de test (`conftest.py`) ou sur un script de seed dédié pour avoir 5+ utilisateurs de test avec natal persisté en DB
  - [x] Pour chaque utilisateur de test : appeler `DailyPredictionService.get_or_compute()` directement (pas via HTTP)
  - [x] Dump les résultats en JSON dans `docs/qa/cases/` (un fichier par profil/utilisateur)
  - [x] Afficher un résumé console : profil, note globale, tons, nombre de pivots
  - [x] **Ne pas appeler l'endpoint HTTP** depuis ce script — risque de dépendance à un serveur en fonctionnement
- [x] Créer le dossier `docs/qa/cases/` (avec `.gitkeep`)

### T3 — Remplir le rapport QA initial (AC2, AC3, AC5)

- [x] Créer `docs/qa/daily-prediction-qa-report-2026-03-08.md` avec :
  - [x] En-tête : date, version moteur, ruleset version, auteur
  - [x] Tableau des 5+ cas de QA avec la grille des 6 dimensions remplie
  - [x] Section "Anomalies" : liste des anomalies avec code catégorie + note + description
  - [x] Section "Observations générales" : synthèse libre
  - [x] Section "Décision" : `validé pour release` ou `bloquant identifié` + justification

### T4 — Créer le backlog d'ajustements produit (AC4)

- [x] Créer `docs/qa/product-adjustments-backlog.md` avec :
  - [x] En-tête : date, lien vers rapport QA de référence
  - [x] Tableau des ajustements classés P0 / P1 / P2
  - [x] Colonnes : ID, Priorité, Description, Catégorie (Texte / Logique / UI / Template), Statut
  - [x] Section "Ajustements appliqués" (initialement vide, alimentée au fil des itérations)

### T5 — Tests d'intégration automatisés (AC1, AC2, AC3)

- [x] Créer `backend/app/tests/integration/test_daily_prediction_qa.py` :
  - [x] `test_categories_all_present` — appel `/v1/predictions/daily` pour un profil de test, vérifier que toutes les catégories actives attendues sont présentes dans le payload
  - [x] `test_notes_in_valid_range` — toutes les notes de catégories sont dans l'intervalle [1, 20]
  - [x] `test_timeline_no_overlap` — les blocs horaires de la timeline ne se chevauchent pas (fin bloc N <= début bloc N+1)
  - [x] `test_caution_flags_consistent` — si une catégorie a une note <= 5, un flag de prudence est présent dans le payload

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- QA cases generation: `5 profiles processed, all returned neutral tone and 10/20 scores (anomaly identified).`
- Integration tests: `4 passed in 2.12s`

### Completion Notes List
- Création de la structure de QA produit sous `docs/qa/`.
- Implémentation du script `generate_qa_cases.py` pour produire des exemples réels.
- Rédaction du rapport QA initial identifiant un blocage sur la diversité des notes (AN-01).
- Mise en place du backlog d'ajustements produit.
- Validation technique par tests d'intégration (TestClient).
- Mise à jour de `config.py` pour utiliser Reference Version 2.0.0 par défaut (requis par ruleset 1.0.0).

### File List
- `backend/app/jobs/qa/generate_qa_cases.py`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `backend/app/core/config.py` (modifié)
- `docs/qa/daily-prediction-checklist.md`
- `docs/qa/daily-prediction-qa-report-2026-03-08.md`
- `docs/qa/product-adjustments-backlog.md`
- `docs/qa/cases/.gitkeep`

## Change Log

- 2026-03-08: Story créée pour Epic 38.
- 2026-03-08: Implémentation de la phase de QA produit, script de génération de cas et tests d'intégration.
