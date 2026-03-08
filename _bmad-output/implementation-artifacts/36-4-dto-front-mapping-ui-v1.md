# Story 36.4 : DTO front et mapping UI V1

Status: ready-for-dev

## Story

As a développeur front-end de l'application horoscope,
I want un contrat TypeScript stable (types, client API, hooks, utilitaires de mapping) et des composants UI de base pour afficher la prédiction quotidienne,
so that la `TodayPage` peut remplacer ses données statiques par la vraie réponse API sans duplication de logique de présentation.

## Acceptance Criteria

### AC1 — Catégories dynamiques depuis l'API

Les catégories affichées correspondent exactement au tableau `categories[]` renvoyé par l'API (code, note_20, summary). Aucun hardcoding de liste de catégories côté front.

### AC2 — Mapping notes 1-20 stable

Les mêmes valeurs numériques `note_20` donnent toujours les mêmes labels et couleurs CSS, selon la table :
- 1–5 : "fragile" → `var(--danger)`
- 6–9 : "tendu" → `var(--warning)`
- 10–12 : "neutre" → `var(--text-2)`
- 13–16 : "porteur" → `var(--success)`
- 17–20 : "très favorable" → `var(--primary)`

### AC3 — Pivots visuellement distingués

Les blocs `turning_point: true` dans la timeline sont visuellement distincts des blocs ordinaires. Les entrées `turning_points[]` sont listées séparément dans `TurningPointsList`.

### AC4 — Affichage brut sans réinterprétation

Le front n'effectue aucun calcul sur les scores. Il affiche uniquement ce que l'API renvoie (`note_20`, `summary`, `overall_tone`, etc.).

### AC5 — Fallback loading/erreur

La `TodayPage` affiche un indicateur visuel pendant le chargement et un message d'erreur explicite si le hook React Query retourne `isError`. Aucun crash sur réponse vide.

### AC6 — Heures au format HH:mm locale

Toutes les heures issues de `start_local` / `end_local` / `occurred_at_local` sont affichées au format HH:mm en locale `fr-FR`.

## Tasks / Subtasks

### T1 — Créer `frontend/src/types/dailyPrediction.ts` (AC1, AC4)

- [ ] Déclarer `DailyPredictionMeta`
- [ ] Déclarer `DailyPredictionCategory`
- [ ] Déclarer `DailyPredictionTimeBlock`
- [ ] Déclarer `DailyPredictionTurningPoint`
- [ ] Déclarer `DailyPredictionSummary` (champ `summary` de la réponse)
- [ ] Déclarer `DailyPredictionResponse` (racine)

### T2 — Créer `frontend/src/api/dailyPrediction.ts` (AC5)

- [ ] Fonction `getDailyPrediction(token: string, date?: string): Promise<DailyPredictionResponse>`
  - `GET /v1/predictions/daily` avec `Authorization: Bearer <token>` et query param `date` optionnel
- [ ] Fonction `getDailyHistory(token: string, from: string, to: string): Promise<DailyPredictionResponse[]>`
  - `GET /v1/predictions/daily/history?from=&to=`

### T3 — Créer `frontend/src/api/useDailyPrediction.ts` (AC5)

- [ ] Hook `useDailyPrediction(token: string | null, date?: string)` via `useQuery`
  - `queryKey: ['daily-prediction', date ?? 'today']`
  - `enabled: Boolean(token)`
  - `staleTime: 1000 * 60 * 5`
- [ ] Hook `useDailyHistory(token: string | null, from: string, to: string)` via `useQuery`

### T4 — Créer `frontend/src/utils/predictionBands.ts` (AC2)

- [ ] Fonction `getNoteBand(note: number): { label: string; colorVar: string }`
- [ ] Mapping `TONE_LABELS`: `steady | push | careful | open | mixed` → libellé fr
- [ ] Mapping `TONE_COLORS`: tone code → variable CSS
- [ ] Mapping `CATEGORY_META`: code → `{ label: string; icon: string }` (icône emoji ou caractère)

### T5 — Créer les composants dans `frontend/src/components/prediction/` (AC1, AC2, AC3, AC4, AC6)

- [ ] `DayPredictionCard.tsx` — carte synthèse du jour
  - Affiche `summary.overall_summary`, `summary.overall_tone` (avec couleur via `TONE_COLORS`)
  - Affiche `meta.date_local` formatée
  - Affiche `summary.best_window` si présent
- [ ] `CategoryGrid.tsx` — grille des catégories
  - Itère sur `categories[]` triées par `rank`
  - Affiche `note_20` avec couleur via `getNoteBand()`
  - Affiche `summary` si non null
  - Utilise `CATEGORY_META[code]` pour l'icône et le label
- [ ] `DayTimeline.tsx` — timeline des blocs horaires
  - Itère sur `timeline[]`
  - Format heure : `toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })`
  - Style distinct pour `turning_point: true` (bordure ou fond différent via inline style)
- [ ] `TurningPointsList.tsx` — liste des pivots
  - Itère sur `turning_points[]`
  - Affiche `occurred_at_local` au format HH:mm
  - Affiche `severity` et `summary`
  - Rendu null si tableau vide

### T6 — Mettre à jour `frontend/src/pages/TodayPage.tsx` (AC1, AC5)

- [ ] Importer `useAccessTokenSnapshot` et `useDailyPrediction`
- [ ] Remplacer `STATIC_HOROSCOPE` par la donnée issue du hook
- [ ] Afficher un spinner ou texte "Chargement…" pendant `isLoading`
- [ ] Afficher un message d'erreur pendant `isError`
- [ ] Intégrer `DayPredictionCard`, `CategoryGrid`, `DayTimeline`, `TurningPointsList`

## Dev Notes

### Pattern hook React Query

Suivre le même pattern que `frontend/src/api/natalChart.ts` :

```typescript
// frontend/src/api/useDailyPrediction.ts
import { useQuery } from '@tanstack/react-query'
import { getDailyPrediction } from './dailyPrediction'

export function useDailyPrediction(token: string | null, date?: string) {
  return useQuery({
    queryKey: ['daily-prediction', date ?? 'today'],
    queryFn: () => getDailyPrediction(token!, date),
    enabled: Boolean(token),
    staleTime: 1000 * 60 * 5,
  })
}
```

### Pattern client API

Utiliser `apiFetch` depuis `frontend/src/api/client.ts` et `API_BASE_URL` :

```typescript
// frontend/src/api/dailyPrediction.ts
import { apiFetch, API_BASE_URL } from './client'
import type { DailyPredictionResponse } from '../types/dailyPrediction'

export async function getDailyPrediction(
  token: string,
  date?: string,
): Promise<DailyPredictionResponse> {
  const url = new URL(`${API_BASE_URL}/v1/predictions/daily`)
  if (date) url.searchParams.set('date', date)
  return apiFetch<DailyPredictionResponse>(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  })
}
```

### Mapping bandes de notes

```typescript
// frontend/src/utils/predictionBands.ts
export function getNoteBand(note: number): { label: string; colorVar: string } {
  if (note <= 5)  return { label: 'fragile',        colorVar: 'var(--danger)' }
  if (note <= 9)  return { label: 'tendu',          colorVar: 'var(--warning)' }
  if (note <= 12) return { label: 'neutre',         colorVar: 'var(--text-2)' }
  if (note <= 16) return { label: 'porteur',        colorVar: 'var(--success)' }
  return            { label: 'très favorable', colorVar: 'var(--primary)' }
}

export const TONE_LABELS: Record<string, string> = {
  steady:  'Stable',
  push:    'Dynamique',
  careful: 'Vigilance',
  open:    'Ouverture',
  mixed:   'Mitigé',
}

export const TONE_COLORS: Record<string, string> = {
  steady:  'var(--text-2)',
  push:    'var(--primary)',
  careful: 'var(--warning)',
  open:    'var(--success)',
  mixed:   'var(--text-2)',
}
```

### Format des heures

```typescript
// Pour start_local / end_local / occurred_at_local (ISO 8601 local)
function formatTime(isoLocal: string): string {
  return new Date(isoLocal).toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
```

### Règle CSS : pas de Tailwind

Ne jamais utiliser de classes Tailwind (`flex`, `gap-2`, `rounded-full`, etc.) — elles n'ont aucun effet dans ce projet. Utiliser uniquement `style={{}}` inline ou les classes CSS existantes (`App.css`, `index.css`, `theme.css`).

### Auth token

```typescript
// Dans TodayPage.tsx
import { useAccessTokenSnapshot } from '../hooks/useAccessTokenSnapshot'

const token = useAccessTokenSnapshot()
const { data, isLoading, isError } = useDailyPrediction(token)
```

### Structure fichiers composants

```
frontend/src/components/prediction/
  DayPredictionCard.tsx
  CategoryGrid.tsx
  DayTimeline.tsx
  TurningPointsList.tsx
```

### Project Structure Notes

- `frontend/src/api/client.ts` — `apiFetch`, `API_BASE_URL` déjà exportés
- `frontend/src/api/natalChart.ts` — pattern de référence pour le client API et les hooks
- `frontend/src/pages/TodayPage.tsx` — fichier à modifier (données statiques `STATIC_HOROSCOPE` à retirer)
- `frontend/src/components/prediction/` — dossier à créer
- `frontend/src/types/dailyPrediction.ts` — fichier à créer
- `frontend/src/utils/predictionBands.ts` — fichier à créer

## References

- [Source: frontend/src/api/client.ts — apiFetch, API_BASE_URL]
- [Source: frontend/src/api/natalChart.ts — pattern hook useQuery et client API]
- [Source: frontend/src/pages/TodayPage.tsx — intégration cible]
- [Source: frontend/src/i18n/ — convention traductions]
- [Source: frontend/src/index.css — variables CSS disponibles (--danger, --warning, --success, --primary, --text-2)]
- [Source: _bmad-output/implementation-artifacts/36-1-service-applicatif-daily-prediction.md — payload DailyPredictionResponse]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/api/dailyPrediction.ts`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/utils/predictionBands.ts`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayTimeline.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/pages/TodayPage.tsx`

## Change Log

- 2026-03-08: Story créée pour l'Epic 36 — Productisation V1.
