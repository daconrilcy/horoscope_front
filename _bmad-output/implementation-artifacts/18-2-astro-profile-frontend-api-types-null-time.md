# Story 18.2: Astro Profile Frontend Data Flow — routes/hooks/types et fin de la sentinelle

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur,
I want que le frontend consomme les vraies données `sun sign`/`ascendant` sans routes dupliquées et sans sentinelle ambiguë,
so that l'affichage soit cohérent entre profil, thème natal et hero card.

## Acceptance Criteria

1. **Given** l'existant frontend (`birthProfile.ts`, `natalChart.ts`, pages) **When** l'audit des routes/hooks est réalisé **Then** seuls les endpoints déjà existants sont étendus/réutilisés.
2. **Given** l'envoi du payload vers `/v1/users/me/birth-data` **When** l'heure est inconnue **Then** le frontend envoie `birth_time: null` (stratégie unique).
3. **Given** l'utilisateur saisit `"00:00"` explicitement **When** il sauvegarde **Then** le frontend envoie `"00:00"` comme vraie valeur (pas conversion implicite vers null).
4. **Given** les types TS **When** ils sont mis à jour **Then** `birth_time?: string | null` et `missing_birth_time: boolean` sont disponibles dans les modèles consommés.
5. **Given** les hooks/pages qui lisent les données astro **When** API renvoie `ascendant_sign_code=null` + `missing_birth_time=true` **Then** aucun crash ni `undefined` affiché.

## Tasks / Subtasks

- [x] Task 1 — Audit et cartographie des points d'intégration (AC: 1)
  - [x] Inventorier les routes/hook existants:
    - [x] `frontend/src/api/birthProfile.ts`
    - [x] `frontend/src/api/natalChart.ts`
    - [x] `frontend/src/pages/BirthProfilePage.tsx`
    - [x] `frontend/src/pages/NatalChartPage.tsx`
    - [x] `frontend/src/pages/TodayPage.tsx`
    - [x] `frontend/src/pages/settings/AccountSettings.tsx`
  - [x] Confirmer qu'aucune nouvelle route `/v1/*` n'est créée côté frontend.

- [x] Task 2 — Typages API astro profile (AC: 4, 5)
  - [x] Étendre `BirthProfileData` et/ou type partagé pour inclure:
    - [x] `birth_time?: string | null`
    - [x] `astro_profile?: { sun_sign_code: string | null; ascendant_sign_code: string | null; missing_birth_time: boolean }`
  - [x] Étendre `LatestNatalChart` avec le même bloc `astro_profile` si exposé par backend sur `latest`.
  - [x] Ajuster les guards `null` dans les consumers.

- [x] Task 3 — Suppression de la sentinelle front (AC: 2, 3)
  - [x] Retirer l'usage de `UNKNOWN_BIRTH_TIME_SENTINEL` dans:
    - [x] `frontend/src/utils/constants.ts`
    - [x] `frontend/src/pages/BirthProfilePage.tsx`
    - [x] tests associés.
  - [x] Règle de soumission unique:
    - [x] champ vide / checkbox "heure inconnue" => `birth_time: null`
    - [x] saisie explicite `"00:00"` => `birth_time: "00:00"`

- [x] Task 4 — Mise à jour des tests frontend data flow (AC: 2, 3, 4, 5)
  - [x] `frontend/src/tests/BirthProfilePage.test.tsx`
    - [x] cas heure inconnue => payload `birth_time: null`.
    - [x] cas saisie `"00:00"` explicite => payload `"00:00"`.
    - [x] retirer attentes legacy `00:00` sentinelle automatique.
  - [x] `frontend/src/tests/natalChartApi.test.tsx` et/ou `frontend/src/tests/NatalChartPage.test.tsx`
    - [x] valider typage/consommation `astro_profile` nullable.
  - [x] tests de non-régression sur chargement/erreur/empty states.

## Dev Notes

### Stratégie choisie (sentinelle)

Stratégie unique appliquée partout: inclure `birth_time: null` quand l'heure manque.

### Plan de changements fichier par fichier (frontend data)

- `frontend/src/api/birthProfile.ts`
  - types: `birth_time?: string | null`, bloc `astro_profile` nullable.
- `frontend/src/api/natalChart.ts`
  - type `LatestNatalChart` enrichi avec `astro_profile` (si backend l'expose).
- `frontend/src/pages/BirthProfilePage.tsx`
  - mapping formulaire: vide => null, `"00:00"` explicite conservé.
  - suppression logique `UNKNOWN_BIRTH_TIME_SENTINEL`.
- `frontend/src/utils/constants.ts`
  - suppression de la constante sentinelle si plus utilisée.
- `frontend/src/tests/BirthProfilePage.test.tsx`
  - mise à jour des assertions payload (null vs `"00:00"`).
- `frontend/src/tests/natalChartApi.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

### Project Structure Notes

- Réutiliser le client API central et React Query déjà en place.
- Pas de duplication de hook/route: extension de `getBirthData` et `useLatestNatalChart` uniquement.

### References

- [Source: frontend/src/api/birthProfile.ts]
- [Source: frontend/src/api/natalChart.ts]
- [Source: frontend/src/pages/BirthProfilePage.tsx]
- [Source: frontend/src/utils/constants.ts]
- [Source: frontend/src/tests/BirthProfilePage.test.tsx]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Audit frontend routes/hooks réalisé : `UNKNOWN_BIRTH_TIME_SENTINEL` présent uniquement dans `constants.ts` et `BirthProfilePage.tsx`.
- `BirthProfileData.birth_time` était déjà `string | null` — seul `astro_profile?` manquait.
- `syncFormWithProfileData` traitait `"00:00"` comme sentinel — corrigé pour ne traiter que `null`.
- 46 tests verts sur les fichiers modifiés, 0 régression introduite (6 échecs pré-existants non liés).

### Completion Notes List

- Story dédiée à la couche data/contrat front pour éviter mélange avec la couche UI.
- `AstroProfile` exporté comme type nommé depuis `birthProfile.ts` pour réutilisation en story 18-3.
- Stratégie sentinelle → null : `BirthProfilePage.onSubmit` envoie désormais `birth_time: null` (heure inconnue) ou la valeur saisie (ex: `"00:00"` pour minuit explicite).
- `"00:00"` depuis l'API n'est plus interprété comme heure inconnue — affichage direct dans le champ.
- TypeScript strict : `npx tsc --noEmit` → 0 erreur.
- Durcissement flux frontend natal chart:
  - `useLatestNatalChart` sans refetch/retry automatiques sur cas 4xx attendus (404/422).
  - politique erreurs/logs unifiée: pas de log support pour 4xx fonctionnels, log support pour 5xx techniques.
- Typage metadata côté front aligné avec backend:
  - support de `metadata.house_system` dans `LatestNatalChart`.

### Change Log

- 2026-02-25: Implémentation story 18-2 — types astro_profile, suppression sentinelle front, mise à jour tests.
- 2026-02-26: Correctifs post-story — réduction bruit 404/422, politique logs 5xx only, typage metadata `house_system`.

### File List

- `_bmad-output/implementation-artifacts/18-2-astro-profile-frontend-api-types-null-time.md`
- `frontend/src/api/birthProfile.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/utils/constants.ts`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
