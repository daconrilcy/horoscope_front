# Story 13.1: Correction erreur 422 lors de la génération du thème natal

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur ayant sauvegardé ses données de naissance,
I want pouvoir déclencher la génération de mon thème natal sans obtenir une erreur 422,
so that le flux de création du thème fonctionne de bout en bout comme prévu.

## Acceptance Criteria

1. **Given** un utilisateur ayant sauvegardé son profil natal **When** il clique sur "Générer mon thème astral" **Then** la requête `POST /v1/users/me/natal-chart` inclut le header `Content-Type: application/json` **And** le backend répond 200 avec le thème généré.

2. **Given** le backend retourne une erreur 422 (données invalides ou incomplètes) **When** la génération échoue avec code HTTP 422 **Then** un message clair est affiché : "Vos données de naissance sont invalides ou incomplètes. Veuillez vérifier votre profil natal." **And** le bouton de génération redevient actif.

3. **Given** le backend retourne un 422 au format FastAPI natif `{"detail": [...]}` **When** `handleResponse` tente de parser l'erreur **Then** le message est extrait proprement ou un fallback générique est utilisé (pas de crash silencieux ni de `undefined` affiché).

## Tasks / Subtasks

- [x] Corriger `frontend/src/api/natalChart.ts` — `generateNatalChart` (AC: 1)
  - [x] Ajouter `"Content-Type": "application/json"` dans les headers du POST `/v1/users/me/natal-chart`
- [x] Robustifier `handleResponse` dans `frontend/src/api/natalChart.ts` (AC: 3)
  - [x] Ajouter un fallback pour parser `{"detail": [...]}` (format FastAPI natif 422)
  - [x] Mapper vers `code: "unprocessable_entity"` avec message lisible ou fallback générique
- [x] Mettre à jour `frontend/src/pages/BirthProfilePage.tsx` — `generationMutation.onError` (AC: 2)
  - [x] Ajouter la gestion du code `"unprocessable_entity"` (ou status HTTP 422) avec message UX adapté
- [x] Mettre à jour les tests dans `frontend/src/tests/BirthProfilePage.test.tsx` (AC: 2)
  - [x] Ajouter un test pour erreur 422 pendant la génération (message UX vérifié)
- [x] Ajouter un test unitaire pour `handleResponse` 422 FastAPI (AC: 3) dans `frontend/src/tests/natalChartApi.test.tsx`

## Dev Notes

### Diagnostic précis du bug

**Cause primaire :** La fonction `generateNatalChart` envoie un POST **sans** `Content-Type: application/json` :

```typescript
// AVANT — BUG
export async function generateNatalChart(accessToken: string): Promise<LatestNatalChart> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/natal-chart`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` }, // ← pas de Content-Type
  })
  return handleResponse<LatestNatalChart>(response)
}
```

FastAPI (Pydantic v2) retourne **systématiquement 422** pour les POST sans `Content-Type: application/json`, même si le corps est vide, car il interprète le body comme non-JSON.

**Cause secondaire :** Le format 422 natif FastAPI est `{"detail": [{...}]}`, mais `handleResponse` attend `{"error": {"code": "...", "message": "..."}}`. Si le backend retourne le format natif FastAPI, le code `payload?.error?.code` sera `undefined`, et l'erreur remontera comme `ApiError("unknown_error", "Request failed with status 422", 422)`.

### Fix principal — `generateNatalChart`

```typescript
// APRÈS — CORRIGÉ
export async function generateNatalChart(accessToken: string): Promise<LatestNatalChart> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/natal-chart`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  })
  return handleResponse<LatestNatalChart>(response)
}
```

### Fix secondaire — `handleResponse` robustesse 422

Ajouter la gestion du format FastAPI natif dans le try/catch de `handleResponse` :

```typescript
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null
    try {
      const raw = await response.json()
      // Format standard API : { error: { code, message, request_id? } }
      if (raw?.error) {
        payload = raw as ErrorEnvelope
      } else if (Array.isArray(raw?.detail)) {
        // Format FastAPI natif 422 : { detail: [{ loc, msg, type }] }
        const firstDetail = raw.detail[0]
        payload = {
          error: {
            code: "unprocessable_entity",
            message: firstDetail?.msg ?? "Données invalides",
          },
        }
      }
    } catch {
      payload = null
    }
    throw new ApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.request_id,
    )
  }

  const payload = (await response.json()) as { data: T }
  return payload.data
}
```

### Fix UX — `BirthProfilePage.tsx` `onError`

Ajouter le cas 422 dans la gestion d'erreur de `generationMutation` :

```typescript
onError: (err) => {
  const requestId = err instanceof ApiError ? err.requestId : undefined
  setGenerationErrorRequestId(requestId || null)

  const code = err instanceof ApiError ? err.code : undefined
  const status = err instanceof ApiError ? err.status : undefined
  if (code === "natal_generation_timeout") {
    setGenerationError("La génération a pris trop de temps, veuillez réessayer.")
  } else if (code === "natal_engine_unavailable") {
    setGenerationError("Le service de génération est temporairement indisponible.")
  } else if (code === "unprocessable_entity" || status === 422) {
    setGenerationError("Vos données de naissance sont invalides ou incomplètes. Veuillez vérifier votre profil natal.")
  } else {
    setGenerationError("Une erreur est survenue. Veuillez réessayer.")
  }
},
```

### Project Structure Notes

- `frontend/src/api/natalChart.ts` — fonctions `generateNatalChart` et `handleResponse`
- `frontend/src/pages/BirthProfilePage.tsx` — `generationMutation.onError` (lignes 71–83)
- `frontend/src/tests/BirthProfilePage.test.tsx` — ajouter test 422 génération (après les tests timeout/unavailable, ~ligne 178)
- `frontend/src/tests/natalChartApi.test.tsx` — fichier existant pour les tests unitaires de l'API natal

### Contexte des stories précédentes

- **Story 12-1** : formulaire profil natal + `saveBirthData` (utilise `Content-Type: application/json` correctement — référence pour la correction)
- **Story 12-2** : génération depuis UI via `generationMutation` — fichier `BirthProfilePage.tsx` lines 62–84
- **Code review 12-2** : 18 tests dans `BirthProfilePage.test.tsx` (16 sauvegarde + 2 réseau génération, pas encore de test 422)
- Le pattern `Content-Type: application/json` est présent dans `saveBirthData` (ligne 55 de `birthProfile.ts`) — reproduire ce pattern dans `generateNatalChart`

### Contrat API documenté

```
POST /v1/users/me/natal-chart
  Auth: Bearer {token}
  Content-Type: application/json  ← REQUIS (fix story 13-1)
  Body: {} (vide)
  → 200: { "data": { chart_id, result, metadata, created_at }, "meta": {...} }
  → 422: validation failed (données de naissance invalides/manquantes)
  → 503 (natal_generation_timeout): délai dépassé (≤ 2min30)
  → 503 (natal_engine_unavailable): moteur natal indisponible
```

### References

- [Source: frontend/src/api/natalChart.ts] — `generateNatalChart`, `handleResponse`, `ApiError`
- [Source: frontend/src/api/birthProfile.ts#L55] — pattern `Content-Type: application/json` (référence)
- [Source: frontend/src/pages/BirthProfilePage.tsx#L62-84] — `generationMutation`
- [Source: frontend/src/tests/BirthProfilePage.test.tsx] — suite de tests existante (18 tests)
- [Source: _bmad-output/implementation-artifacts/12-2-...md] — story précédente, Dev Notes

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Fix appliqué : ajout `"Content-Type": "application/json"` dans `generateNatalChart` (pattern identique à `saveBirthData` dans `birthProfile.ts`).
- `handleResponse` robustifié : détection du format FastAPI natif `{"detail": [...]}` → mapping vers `code: "unprocessable_entity"`.
- `BirthProfilePage.tsx` `onError` : ajout du cas `unprocessable_entity` / status 422 avec message UX explicite.
- 4 nouveaux tests dans `natalChartApi.test.tsx` (Content-Type vérifié, 422 FastAPI natif, 422 format standard, fallback corps imparseable).
- 1 nouveau test dans `BirthProfilePage.test.tsx` (422 pendant génération → message UX vérifié).
- Suite complète : **142 / 142 tests passent**, lint : **0 erreur**.

### Completion Notes List

- Tous les AC satisfaits : AC1 (Content-Type), AC2 (message UX 422), AC3 (parsing FastAPI natif).
- `handleResponse` amélioré sans régression — les formats d'erreur existants (`{error:{...}}`) continuent de fonctionner (test dédié ajouté).
- `BirthProfilePage.test.tsx` : 18 → 19 tests. `natalChartApi.test.tsx` : 2 → 6 tests.

### File List

- frontend/src/api/natalChart.ts (modifié — `generateNatalChart` + `"Content-Type": application/json`, `handleResponse` + fallback FastAPI 422)
- frontend/src/pages/BirthProfilePage.tsx (modifié — `generationMutation.onError` + cas `unprocessable_entity` / status 422)
- frontend/src/tests/BirthProfilePage.test.tsx (modifié — +1 test 422 génération)
- frontend/src/tests/natalChartApi.test.tsx (modifié — +4 tests : Content-Type, 422 FastAPI, 422 standard, fallback)

### Change Log

- 2026-02-21 : Implémentation story 13-1 (claude-sonnet-4-6) — Fix erreur 422 : Content-Type manquant sur generateNatalChart, robustification handleResponse pour FastAPI natif 422, gestion UX dans BirthProfilePage. 142/142 tests, 0 erreur lint.
- 2026-02-21 : Code review (claude-sonnet-4-6) — 2 findings corrigés : M1 (assertion bouton ré-activé manquante dans test 422, AC2 explicite), L1 (`??` → `||` dans handleResponse pour filtrer msg vide). 142/142 tests, 0 erreur lint.
- 2026-02-21 : Hotfix (claude-sonnet-4-6) — Body `{}` manquant dans generateNatalChart (backend retourne `invalid_request_payload` avec `loc: ["body"]`). Ajout de `body: JSON.stringify({})` et assertion `init.body === "{}"` dans le test Content-Type. 142/142 tests, 0 erreur lint.

## Code Review Record

### Senior Developer Review (AI) — claude-sonnet-4-6

| ID | Sévérité | Fichier | Description | Statut |
|----|----------|---------|-------------|--------|
| M1 | MEDIUM | `BirthProfilePage.test.tsx:185` | Test 422 ne vérifiait pas que le bouton est ré-activé après erreur (AC2 explicite : "le bouton redevient actif") | Corrigé |
| L1 | LOW | `natalChart.ts:86` | `??` ne protège pas contre `msg: ""` (chaîne vide) — remplacé par `\|\|` | Corrigé |
