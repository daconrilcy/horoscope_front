# Story 38.3 : QA produit sur cas réels

Status: ready-for-dev

## Story

As a product owner de l'application horoscope,
I want une phase de QA métier documentée avec des cas de test sur profils variés et une grille d'évaluation structurée,
so that la feature de prédiction quotidienne est validée en usage réel avant release, avec un backlog d'ajustements et une décision explicite de go/no-go.

## Acceptance Criteria

### AC1 — Au moins 5 cas de QA sur profils variés

Le script `generate_qa_cases.py` génère au minimum 5 cas de test couvrant des signes différents et des dates différentes. Chaque cas produit un payload complet de prédiction.

### AC2 — Checklist remplie sur 6 dimensions

Le rapport QA rempli évalue chaque cas sur les 6 dimensions : compréhensible, cohérent avec la journée, trop vague, trop alarmiste, pivots crédibles, timeline utile. Chaque dimension est notée (OK / KO / N/A) avec commentaire libre.

### AC3 — Anomalies documentées avec code catégorie, note, et description

Toute anomalie identifiée lors de la QA est enregistrée avec : code catégorie (`VAGUE`, `ALARME`, `INCOHERENT`, `PIVOT_FAIBLE`, `TIMELINE_VIDE`, `AUTRE`), note (1-20), et description en langage naturel.

### AC4 — Backlog d'ajustements produit créé

`docs/qa/product-adjustments-backlog.md` liste les ajustements produit identifiés, classés par priorité (P0 bloquant / P1 important / P2 amélioration).

### AC5 — Décision explicite go/no-go

Le rapport QA contient une section "Décision" avec une des deux valeurs : `validé pour release` ou `bloquant identifié`, suivie d'une justification d'une phrase.

## Tasks / Subtasks

### T1 — Créer la checklist QA (AC2)

- [ ] Créer `docs/qa/daily-prediction-checklist.md` avec :
  - [ ] Introduction : objectif, date de la QA, profils testés
  - [ ] Grille des 6 dimensions pour chaque cas de test :
    - `compréhensible ?` — le texte est lisible et clair pour un non-astrologue
    - `cohérent avec la journée ?` — les conseils semblent plausibles pour la date testée
    - `trop vague ?` — le texte ne dit rien d'actionnable
    - `trop alarmiste ?` — le ton inquiète sans raison proportionnée
    - `pivots crédibles ?` — les pivots horaires semblent plausibles et utiles
    - `timeline utile ?` — la répartition des blocs horaires apporte de la valeur
  - [ ] Colonne de décision par cas : `validé` / `à retravailler` / `bloquant`

### T2 — Créer le script de génération des cas QA (AC1) — via couche service, pas API publique

**CRITIQUE** : le script ne peut pas appeler directement `GET /v1/predictions/daily` avec des "profils simplifiés". Cet endpoint exige un utilisateur authentifié avec un natal réellement persisté en DB. Il faut donc soit :
- **(Option A — recommandée)** Appeler `DailyPredictionService.get_or_compute()` directement depuis le script en Python, avec des utilisateurs de test seedés en DB via les fixtures de test existantes.
- **(Option B)** Créer de vrais utilisateurs de test avec natal seedé via la commande de seed existante, puis appeler l'endpoint avec leurs tokens.

- [ ] Créer `backend/app/jobs/qa/generate_qa_cases.py` (Option A) :
  - [ ] S'appuyer sur les fixtures de test (`conftest.py`) ou sur un script de seed dédié pour avoir 5+ utilisateurs de test avec natal persisté en DB
  - [ ] Pour chaque utilisateur de test : appeler `DailyPredictionService.get_or_compute()` directement (pas via HTTP)
  - [ ] Dump les résultats en JSON dans `docs/qa/cases/` (un fichier par profil/utilisateur)
  - [ ] Afficher un résumé console : profil, note globale, tons, nombre de pivots
  - [ ] **Ne pas appeler l'endpoint HTTP** depuis ce script — risque de dépendance à un serveur en fonctionnement
- [ ] Créer le dossier `docs/qa/cases/` (avec `.gitkeep`)

### T3 — Remplir le rapport QA initial (AC2, AC3, AC5)

- [ ] Créer `docs/qa/daily-prediction-qa-report-2026-03-08.md` avec :
  - [ ] En-tête : date, version moteur, ruleset version, auteur
  - [ ] Tableau des 5+ cas de QA avec la grille des 6 dimensions remplie
  - [ ] Section "Anomalies" : liste des anomalies avec code catégorie + note + description
  - [ ] Section "Observations générales" : synthèse libre
  - [ ] Section "Décision" : `validé pour release` ou `bloquant identifié` + justification

### T4 — Créer le backlog d'ajustements produit (AC4)

- [ ] Créer `docs/qa/product-adjustments-backlog.md` avec :
  - [ ] En-tête : date, lien vers rapport QA de référence
  - [ ] Tableau des ajustements classés P0 / P1 / P2
  - [ ] Colonnes : ID, Priorité, Description, Catégorie (Texte / Logique / UI / Template), Statut
  - [ ] Section "Ajustements appliqués" (initialement vide, alimentée au fil des itérations)

### T5 — Tests d'intégration automatisés (AC1, AC2, AC3)

- [ ] Créer `backend/app/tests/integration/test_daily_prediction_qa.py` :
  - [ ] `test_categories_all_present` — appel `/v1/predictions/daily` pour un profil de test, vérifier que toutes les catégories actives attendues sont présentes dans le payload
  - [ ] `test_notes_in_valid_range` — toutes les notes de catégories sont dans l'intervalle [1, 20]
  - [ ] `test_timeline_no_overlap` — les blocs horaires de la timeline ne se chevauchent pas (fin bloc N <= début bloc N+1)
  - [ ] `test_caution_flags_consistent` — si une catégorie a une note <= 5, un flag de prudence est présent dans le payload

## Dev Notes

### Rôle de la checklist QA

La checklist est un document **semi-manuel** : le script génère les payloads techniques, l'évaluateur métier remplit les colonnes de jugement. Les tests automatisés vérifient uniquement les propriétés mécaniques (plages de valeurs, structure), pas la qualité rédactionnelle.

### Structure du script generate_qa_cases.py

```python
# backend/app/jobs/qa/generate_qa_cases.py
import httpx, json
from pathlib import Path
from datetime import date

QA_PROFILES = [
    {"sign": "aries",       "date": "2026-03-08", "timezone": "Europe/Paris",    "lat": 48.85, "lon": 2.35},
    {"sign": "leo",         "date": "2026-03-09", "timezone": "America/New_York","lat": 40.71, "lon": -74.00},
    {"sign": "scorpio",     "date": "2026-03-10", "timezone": "Asia/Tokyo",      "lat": 35.68, "lon": 139.69},
    {"sign": "aquarius",    "date": "2026-03-11", "timezone": "Europe/London",   "lat": 51.50, "lon": -0.12},
    {"sign": "pisces",      "date": "2026-03-12", "timezone": "Australia/Sydney","lat": -33.87,"lon": 151.21},
]

OUTPUT_DIR = Path("docs/qa/cases")
API_BASE = "http://localhost:8001"

def generate():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for profile in QA_PROFILES:
        # appel API, dump JSON, affichage résumé
        ...
```

### Test timeline non-chevauchante

```python
def test_timeline_no_overlap(prediction_payload):
    blocks = prediction_payload["timeline"]["blocks"]
    for i in range(len(blocks) - 1):
        end_current = blocks[i]["end_hour"]
        start_next = blocks[i + 1]["start_hour"]
        assert end_current <= start_next, f"Overlap: block {i} ends at {end_current}, block {i+1} starts at {start_next}"
```

### Test notes en plage valide

```python
def test_notes_in_valid_range(prediction_payload):
    for cat in prediction_payload["categories"]:
        note = cat["note_20"]
        assert 1 <= note <= 20, f"Note hors plage pour {cat['code']}: {note}"
```

### Convention de catégories d'anomalie

| Code | Signification |
|------|--------------|
| `VAGUE` | Texte trop générique, pas d'action possible |
| `ALARME` | Ton trop alarmiste, disproportionné par rapport à la note |
| `INCOHERENT` | Incohérence interne entre note, ton et texte |
| `PIVOT_FAIBLE` | Pivot horaire peu plausible ou mal formulé |
| `TIMELINE_VIDE` | Bloc horaire sans contenu utile |
| `AUTRE` | Autre problème non catégorisé |

### Project Structure Notes

- Endpoint à appeler : `GET /v1/predictions/daily` (story 36-2)
- `DailyPredictionService` : `backend/app/services/daily_prediction_service.py` (story 36-1)
- Dossier docs/qa/ à créer s'il n'existe pas
- Les tests d'intégration nécessitent un serveur backend actif ou un client de test FastAPI (`TestClient`)

## References

- [Story: 36-1 — DailyPredictionService]
- [Story: 36-2 — Endpoint /v1/predictions/daily]
- [Story: 36-4 — DTO front et mapping UI v1]
- [Story: 38-1 — EditorialTemplateEngine]
- [Source: backend/app/services/daily_prediction_service.py]
- [Source: backend/app/tests/integration/ — patterns tests d'intégration existants]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-03-08: Story créée pour Epic 38.
