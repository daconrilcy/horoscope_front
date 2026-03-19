# Story 60.13 : Module Événements Astrologiques du Jour

Status: done

## Story

En tant qu'utilisateur de la page Horoscope du jour,
je veux voir un module factuel des événements astrologiques de la journée (positions planétaires, ingresses, aspects),
afin de comprendre les configurations célestes qui sous-tendent ma prédiction, sans interprétation ajoutée.

## Acceptance Criteria

### Backend — Nouvelle policy `PublicAstroDailyEventsPolicy`

1. La policy extrait les **aspects exacts du jour** (max 4) depuis la source d'événements (evidence pack ou engine_output) et les formate factuellement : `"Vénus Trigone Saturne"`, `"Mercure Sextile Jupiter"` — en utilisant `ASPECT_LABELS` et `PLANET_NAMES_FR` de `public_astro_vocabulary.py`.
2. La policy extrait les événements de type `moon_sign_ingress` et génère une entrée ingresse avec l'heure locale si `occurred_at_local` est disponible : `{"text": "Lune entre en Lion", "time": "14:35"}`.
3. La policy tente d'extraire les **positions planétaires** des planètes lentes (Soleil, Lune, Mercure, Vénus, Mars) depuis les événements de transit (event_type contient `transit_to_natal` ou champs de signe du snapshot), formatées comme `"Soleil en Poissons"`. Si non disponible, cette liste est omise (champ absent du dict, pas `null`).
4. Si aucun événement n'est disponible (liste vide ou absente), la policy retourne `None` — le module n'apparaît pas côté frontend.
5. Le bloc est ajouté au payload V4 sous la clé `astro_daily_events: dict | None` avec structure :
   ```json
   {
     "ingresses": [{"text": "Lune entre en Lion", "time": "14:35"}],
     "aspects": ["Vénus Trigone Saturne", "Mercure Sextile Jupiter"],
     "planet_positions": ["Soleil en Poissons", "Lune en Lion"]
   }
   ```
6. Le DTO Pydantic `DailyPredictionAstroDailyEvents` est ajouté dans `predictions.py` avec annotation complète.
7. Tests unitaires couvrant : aspects extraits correctement, ingresse avec heure, fallback `None` sur événements vides, cas multi-ingresses.

### Frontend — Nouveau composant `AstroDailyEventsModule`

8. Le composant est placé **entre** `DayClimateHero` (Zone 2) et `DomainRankingCard` (Zone 3) dans `DailyHoroscopePage.tsx`.
9. Si `prediction.astro_daily_events` est absent ou null → le composant n'est pas rendu (render-guard explicite).
10. Affichage en liste compacte (pas de carte hero) :
    - **Ingresses** (si présentes) en tête, avec badge horodatage `"14:35"` inline
    - **Aspects** : liste de phrases factuelles (ex. "Vénus Trigone Saturne")
    - **Positions** (si présentes) : liste "Soleil en Poissons, Lune en Lion, ..."
11. Style cohérent avec le système CSS : `var(--glass)`, `var(--text-1)`, `var(--text-2)`, `var(--glass-border)` — aucune classe Tailwind.
12. Nouveau mapper `astroDailyEventsMapper.ts` dans `frontend/src/utils/` qui transforme `DailyPredictionAstroDailyEvents` → model local.
13. Type `DailyPredictionAstroDailyEvents` ajouté dans `frontend/src/types/dailyPrediction.ts`.

## Tasks / Subtasks

- [x] T1 — Backend : créer `PublicAstroDailyEventsPolicy` (AC: 1, 2, 3, 4)
  - [x] T1.1 — Résolution des events : réutiliser le même pattern que `PublicAstroFoundationPolicy` (evidence pack → fallback engine_output.core.events)
  - [x] T1.2 — Extraire aspects (event_type == "aspect" ou "aspect_exact_*"), formater "Planète A Aspect Planète B"
  - [x] T1.3 — Extraire ingresses (event_type == "moon_sign_ingress"), formater avec heure locale si disponible
  - [x] T1.4 — Tenter d'extraire positions planétaires depuis les champs de signe disponibles
  - [x] T1.5 — Retourner `None` si aucune donnée exploitable

- [x] T2 — Backend : intégrer dans l'assembler et le DTO (AC: 5, 6)
  - [x] T2.1 — Appeler `PublicAstroDailyEventsPolicy().build(...)` dans `PublicPredictionAssembler.assemble()`
  - [x] T2.2 — Ajouter `astro_daily_events: DailyPredictionAstroDailyEvents | None` au DTO response
  - [x] T2.3 — Inclure dans le dict final renvoyé par l'assembler

- [x] T3 — Backend : tests unitaires (AC: 7)
  - [x] T3.1 — Créer `backend/tests/unit/prediction/test_public_astro_daily_events.py`
  - [x] T3.2 — Test : aspects extraits et formatés correctement
  - [x] T3.3 — Test : ingresse avec heure locale
  - [x] T3.4 — Test : fallback None sur events vides
  - [x] T3.5 — Test : multi-aspects (max 4) et multi-ingresses

- [x] T4 — Frontend : types et mapper (AC: 12, 13)
  - [x] T4.1 — Ajouter `DailyPredictionAstroDailyEvents` dans `frontend/src/types/dailyPrediction.ts`
  - [x] T4.2 — Créer `frontend/src/utils/astroDailyEventsMapper.ts`

- [x] T5 — Frontend : composant `AstroDailyEventsModule` (AC: 8, 9, 10, 11)
  - [x] T5.1 — Créer `frontend/src/components/AstroDailyEventsModule.tsx`
  - [x] T5.2 — Render-guard si `astro_daily_events` null/undefined
  - [x] T5.3 — Rendu ingresses avec badge horodatage
  - [x] T5.4 — Rendu aspects en liste
  - [x] T5.5 — Rendu positions planétaires (conditionnel)

- [x] T6 — Frontend : intégrer dans la page (AC: 8)
  - [x] T6.1 — Importer `AstroDailyEventsModule` dans `DailyHoroscopePage.tsx`
  - [x] T6.2 — Placer entre Zone 2 (DayClimateHero) et Zone 3 (DomainRankingCard)

- [x] T7 — Vérification finale
  - [x] T7.1 — `ruff check backend/` passe
  - [x] T7.2 — `pytest backend/` passe
  - [x] T7.3 — Le composant ne s'affiche pas si `astro_daily_events` est null

## Dev Notes

### Architecture critique

**Source des événements** — Réutiliser EXACTEMENT le même pattern de résolution que `PublicAstroFoundationPolicy.build()` lignes 244-251 dans `public_projection.py` :
```python
events = []
if evidence and hasattr(evidence, "metadata") and "astro_events" in evidence.metadata:
    events = evidence.metadata["astro_events"]
elif engine_output is not None:
    core = _resolve_core_engine_output(engine_output)
    if hasattr(core, "events"):
        events = core.events
```
**Ne pas dupliquer** la résolution — si besoin, extraire une méthode privée partagée `_resolve_astro_events(evidence, engine_output)` dans le module.

**Types d'événements disponibles** (définis dans `public_projection.py` lignes 43-48) :
```python
"aspect_exact_to_angle", "aspect_exact_to_luminary", "aspect_exact_to_personal",
"moon_sign_ingress"
```
Et dans `EFFECT_LABELS` de `public_astro_vocabulary.py` : `"lunar_sign_change"`, `"exact_aspect"`, etc.

**Différence fondamentale avec AstroFoundationSection (60.7)** :
- `AstroFoundationSection` : add headline + interpretation_bridge + effect_labels interprétatifs
- `AstroDailyEventsModule` : faits bruts uniquement, aucune interpretation, pas de `effect_label`
- Les deux utilisent les mêmes événements source mais produisent des outputs distincts

**Format des aspects** : `get_aspect_label(e.aspect)` → "Trigone", "Sextile", etc. Formater : `f"{PLANET_NAMES_FR.get(e.body, e.body)} {get_aspect_label(e.aspect)} {PLANET_NAMES_FR.get(e.target, e.target)}"`. Filtrer les événements où `e.target` est None.

**Ingresses** : `event_type == "moon_sign_ingress"`. L'objet event a `.body` ("moon"), et potentiellement `.target` (signe en français ou code). L'heure locale est dans `occurred_at_local` ou `local_time`. Si l'heure est disponible, format `"HH:MM"`. Si `.target` est un code de signe, traduire avec `SIGN_NAMES_FR` (à créer dans `public_astro_vocabulary.py` si inexistant).

**Positions planétaires** : Ces données peuvent ne pas être disponibles dans le snapshot ou les événements. Si non disponibles, omettre silencieusement le champ `planet_positions` du dict (ne pas mettre `[]` — mettre l'absence du champ). L'AC3 dit "si non disponible, champ absent".

### Fichiers clés

**À créer :**
- `backend/app/prediction/public_astro_daily_events.py` — nouvelle policy (ou classe inline dans `public_projection.py`)
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`
- `frontend/src/components/AstroDailyEventsModule.tsx`
- `frontend/src/utils/astroDailyEventsMapper.ts`

**À modifier :**
- `backend/app/prediction/public_projection.py` — appel policy + assembler
- `backend/app/api/v1/routers/predictions.py` — DTO `DailyPredictionAstroDailyEvents`
- `frontend/src/types/dailyPrediction.ts` — type `DailyPredictionAstroDailyEvents`
- `frontend/src/pages/DailyHoroscopePage.tsx` — Zone 2.5 entre DayClimateHero et DomainRankingCard

### CSS — Ne pas utiliser Tailwind

Le projet utilise un système de variables CSS custom. Exemples pour ce composant :
```tsx
<section style={{
  background: 'var(--glass)',
  border: '1px solid var(--glass-border)',
  borderRadius: '12px',
  padding: '16px',
  marginBottom: '24px'
}}>
```
Variables disponibles : `--glass`, `--glass-2`, `--glass-border`, `--text-1`, `--text-2`, `--primary`, `--success`.

### Design du composant

Structure visuelle attendue :
```
┌─────────────────────────────────────────┐
│ 🌙 Événements du ciel                   │ ← titre compact
├─────────────────────────────────────────┤
│ ⚡ Lune entre en Lion          [14:35]  │ ← ingresse (badge horodatage)
│ • Vénus Trigone Saturne                 │ ← aspects
│ • Mercure Sextile Jupiter               │
│ Soleil en Poissons · Lune en Lion ...   │ ← positions (ligne condensée)
└─────────────────────────────────────────┘
```

### Dépendances

- Dépend de : **60.7** (vocabulaire réutilisé depuis `public_astro_vocabulary.py`), **60.8** (structure page)
- `public_astro_vocabulary.py` existe déjà avec `PLANET_NAMES_FR`, `ASPECT_LABELS`, `ASPECT_TONALITY`, `get_planet_name_fr()`, `get_aspect_label()`
- Story 60.12 a nettoyé les composants V3 legacy — ne pas les ressusciter

### Project Structure Notes

- Backend : les policies de projection sont dans `backend/app/prediction/public_projection.py` OU dans des fichiers dédiés (ex: `public_domain_taxonomy.py`, `public_score_mapper.py`). Choisir le fichier dédié pour garder `public_projection.py` lisible.
- Frontend : tous les composants V4 dans `frontend/src/components/` (pas de sous-dossier pour ce composant). Les utils dans `frontend/src/utils/`.
- Tests backend : `backend/tests/unit/prediction/` pour les tests unitaires de policy.

### References

- `backend/app/prediction/public_projection.py` lignes 228-333 — `PublicAstroFoundationPolicy` (pattern à réutiliser)
- `backend/app/prediction/public_astro_vocabulary.py` — `PLANET_NAMES_FR`, `ASPECT_LABELS`, `get_aspect_label()`
- `frontend/src/pages/DailyHoroscopePage.tsx` lignes 135-142 — Zone 2 DayClimateHero (insérer après)
- `frontend/src/types/dailyPrediction.ts` — types existants à étendre

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/public_astro_daily_events.py`
- `backend/app/prediction/public_astro_vocabulary.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/api/v1/routers/predictions.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/utils/astroDailyEventsMapper.ts`
- `frontend/src/components/AstroDailyEvents.tsx`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/pages/DailyHoroscopePage.tsx`
