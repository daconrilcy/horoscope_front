# CS-385 — notes de clôture et correctifs associés

Date: 2026-05-29  
Utilisateur de référence: `daconrilcy@hotmail.com` (plan `basic`)

## 1. Correctif principal — faux `degraded` sur projections persistées (backend)

### Symptôme

Bandeau frontend « Lecture partielle : des données de naissance manquent. » alors que
le profil et le thème sont complets.

### Cause

- `NatalResult.chart_objects` absent après désérialisation DB
- `structured_facts_v1` vide → inférence `no_time` via `empty_collections=["houses"]`

### Correction

- Rehydratation via `build_chart_object_runtime_data` dans `ChartInterpretationInputBuilder`
- `birth_time_missing_from_structured_facts()` préfère `birth_time: "available"`

### Preuve

- Snapshots `before-persisted-chart-projection.json` / `after-persisted-chart-projection.json`
- Tests backend ciblés (structured facts, builders, API projections)
- Vérification runtime sur chart `2a5c914a-6922-4be1-bca1-55561bd79b4d` → `state=normal`
- Vérification navigateur `/natal` connecté — absence du bandeau « Partial reading »

---

## 2. Correctif associé — régénération LLM à chaque visite `/natal` (frontend)

### Symptôme

À chaque retour sur `/natal`, l'interprétation short Basic était regénérée (skeleton +
`POST /v1/natal/interpretation`) au lieu d'être relue depuis l'historique persisté.

### Cause

- Effet `isSingleAstrologerPlan` remettait `selectedInterpretationId = null`
- `mainQuery` restait armé malgré une interprétation short déjà en historique

### Correction

- Réutiliser `latestShortInterpretation.id` via `useNatalInterpretationById`
- Bloquer `mainQuery` tant que l'historique n'est pas résolu ou qu'un candidat persisté existe
- Protéger le choix explicite d'une génération `complete`

### Preuve

- `frontend/src/tests/natalInterpretation.test.tsx` —
  `reutilise l'interpretation short persistee en Basic sans relancer la generation`
- Vérification navigateur dashboard → `/natal` — contenu immédiat sans skeleton LLM

---

## 3. Correctif associé — sélection d'astrologue bloquée dans le modal (frontend)

### Symptôme

Modal « Choisissez votre astrologue » : clic sur une carte sans effet.

### Cause

- `AstrologerCard` n'attachait `onClick` que si `showProfileCta={true}`
- `PersonaSelector` utilisait `AstrologerGrid` sans CTA cliquable

### Correction

- Prop `selectionMode` + bouton « Demander l'interprétation complète » sur `AstrologerCard`
- `NatalInterpretationPersonaSelector` active `selectionMode`

### Preuve

- `frontend/src/tests/AstrologersPage.test.tsx` — `expose un bouton de selection quand selectionMode est actif`
- `frontend/src/tests/natalInterpretation.test.tsx` —
  `selectionne un astrologue dans le modal et lance la generation complete`

---

## 4. Correctif associé — deuxième interprétation complète Basic (frontend)

### Symptôme

Nouvelle demande d'interprétation complète en Basic → erreur API 429 affichée comme
erreur générique « L'interprétation n'est pas disponible » + Réessayer.

### Cause

- Pas de garde client quand une interprétation complète (`natal_interpretation`) existe déjà
- CTA en-tête redirigeait vers l'abonnement au lieu d'informer

### Correction

- `isBasicCompleteLimitReached = single_astrologer && hasCompleteInterpretation`
- Bandeau `ni-quota-notice` avec `basicCompleteLimitMessage` (i18n fr/en/es)
- Blocage modal / génération LLM ; mapping 429 vers le même message sans retry

### Preuve

- `frontend/src/tests/natalInterpretation.test.tsx` —
  `affiche un message explicite quand le quota Basic complet est deja consomme`
- `frontend/src/tests/NatalChartPage.test.tsx` —
  `affiche un message explicite depuis l'en-tete quand le quota Basic complet est deja consomme`

---

## 5. Commandes de validation exécutées

```bash
# Backend
cd backend
pytest -q tests/unit/domain/astrology/test_structured_facts_v1_builder.py -k "persisted or birth_time_missing"
pytest -q tests/unit/domain/astrology/test_beginner_summary_v1_builder.py -k persisted
pytest -q tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py -k persisted
pytest -q tests/api/test_projection_real_conditions.py -k "persisted_chart or no_time"
ruff format .
ruff check app/domain/astrology/interpretation/

# Frontend
cd frontend
npm run test -- --run src/tests/natalInterpretation.test.tsx src/tests/NatalChartPage.test.tsx src/tests/AstrologersPage.test.tsx
```
