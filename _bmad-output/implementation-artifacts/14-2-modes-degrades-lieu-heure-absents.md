# Story 14.2: Modes dégradés — lieu absent et heure de naissance absente

Status: done

## Story

As a utilisateur,
I want pouvoir utiliser l'application même si je ne connais pas mon heure ou mon lieu de naissance exact,
so that j'obtiens quand même un thème natal partiel avec un avertissement clair sur les limitations.

## Acceptance Criteria

1. **Given** un utilisateur qui ne renseigne pas de lieu de naissance (ou dont le géocodage a échoué) **When** il génère son thème natal **Then** le backend utilise le mode Equal House (sans coordonnées géographiques) **And** `metadata.degraded_mode` contient `"no_location"` dans la réponse **And** un bandeau d'avertissement est affiché sur la page du thème natal : "⚠ Thème calculé en maisons égales — lieu de naissance non renseigné ou non trouvé. Pour un calcul précis, renseignez votre ville et pays dans votre profil."

2. **Given** un utilisateur qui ne renseigne pas d'heure de naissance (champ laissé vide ou coché "inconnue") **When** il génère son thème natal **Then** le backend utilise Solar chart (Soleil en Ascendant, heure forcée à 12:00 UTC) **And** `metadata.degraded_mode` contient `"no_time"` dans la réponse **And** un bandeau d'avertissement est affiché : "⚠ Thème calculé en thème solaire — heure de naissance non renseignée. Les positions des maisons et de la Lune peuvent être inexactes."

3. **Given** un utilisateur sans lieu ET sans heure **When** il génère son thème natal **Then** les deux avertissements sont affichés simultanément **And** `metadata.degraded_mode` contient `"no_location_no_time"`

4. **Given** un utilisateur sans date de naissance **When** il tente de sauvegarder son profil natal **Then** le formulaire bloque la soumission avec un message : "La date de naissance est indispensable pour calculer votre thème natal." **And** aucune requête n'est envoyée au backend

## Tasks / Subtasks

- [x] Étendre le type `LatestNatalChart.metadata` dans `natalChart.ts` (AC: 1, 2, 3)
  - [x] Ajouter `degraded_mode?: "no_location" | "no_time" | "no_location_no_time" | null` dans le type `metadata`

- [x] Mettre à jour `BirthProfileData` dans `birthProfile.ts` (AC: 2)
  - [x] Modifier `birth_time: string` → `birth_time: string | null`
  - [x] `saveBirthData` accepte `birth_time: null` dans le payload JSON (JSON.stringify le gère nativement)

- [x] Mettre à jour `BirthProfilePage.tsx` — case "Heure inconnue" (AC: 2, 4)
  - [x] Modifier le schéma Zod : `birth_time` accepte format valide OU chaîne vide via `.or(z.literal(""))`
  - [x] Ajouter le message d'erreur `birth_date` dédié pour le cas vide : "La date de naissance est indispensable pour calculer votre thème natal."
  - [x] Ajouter state `birthTimeUnknown: boolean` (initialisé à `false`)
  - [x] Ajouter checkbox id `birth-time-unknown`, label "Heure inconnue"
  - [x] Quand checkbox cochée : désactiver le champ `birth_time` (`disabled`), vider la valeur via `setValue("birth_time", "")`, masquer les erreurs de validation
  - [x] Dans `onSubmit` : si `birthTimeUnknown` ou `birth_time` vide → inclure `birth_time: null` dans le payload
  - [x] Lors du reset formulaire depuis l'API : si `data.birth_time === null` → cocher la checkbox + `birth_time: ""`

- [x] Mettre à jour `NatalChartPage.tsx` — bandeaux d'avertissement mode dégradé (AC: 1, 2, 3)
  - [x] Lire `chart.metadata.degraded_mode` (peut être absent/null → pas de bandeau)
  - [x] Si `"no_location"` ou `"no_location_no_time"` : afficher bandeau lieu (`role="alert"`)
  - [x] Si `"no_time"` ou `"no_location_no_time"` : afficher bandeau heure (`role="alert"`)
  - [x] Placer les bandeaux avant le contenu du thème (après le `<p>` de métadonnées)

- [x] Tests `BirthProfilePage.test.tsx` (AC: 2, 4)
  - [x] Test : cocher "Heure inconnue" → champ désactivé + `birth_time: null` dans payload PUT
  - [x] Test : décocher "Heure inconnue" → champ réactivé
  - [x] Test : reset depuis API avec `birth_time: null` → checkbox auto-cochée, champ vide
  - [x] Test : soumission sans `birth_date` → blocage + message "La date de naissance est indispensable..."

- [x] Tests `NatalChartPage.test.tsx` (AC: 1, 2, 3)
  - [x] Test : `degraded_mode: "no_location"` → bandeau lieu affiché, bandeau heure absent
  - [x] Test : `degraded_mode: "no_time"` → bandeau heure affiché, bandeau lieu absent
  - [x] Test : `degraded_mode: "no_location_no_time"` → les deux bandeaux affichés
  - [x] Test : `degraded_mode: null` ou absent → aucun bandeau affiché

## Dev Notes

### Résumé implémentation (story done)

Cette story a été complétée avec succès. Les principales modifications apportées :

- **Type `LatestNatalChart.metadata`** : ajout de `degraded_mode?: "no_location" | "no_time" | "no_location_no_time" | null`
- **Type `BirthProfileData`** : `birth_time: string | null` (nullable)
- **`BirthProfilePage.tsx`** : checkbox "Heure inconnue" avec state `birthTimeUnknown`, schéma Zod adapté, helper `syncFormWithProfileData()`
- **`NatalChartPage.tsx`** : bandeaux d'avertissement pour modes dégradés avec `role="alert"` et classe CSS `.degraded-warning`
- **Tests** : 12 tests spécifiques aux AC (6 dans `BirthProfilePage.test.tsx`, 5 dans `NatalChartPage.test.tsx`, 1 test intégration flux no_location)

### Contrat API backend (référence)

```typescript
export type LatestNatalChart = {
  chart_id: string
  result: NatalResult
  metadata: {
    reference_version: string
    ruleset_version: string
    degraded_mode?: "no_location" | "no_time" | "no_location_no_time" | null  // NOUVEAU
  }
  created_at: string
}
```

### Bandeaux dans `NatalChartPage.tsx`

Ajouter **après** le `<p>` de métadonnées et **avant** `<div className="grid">` :

```tsx
{(chart.metadata.degraded_mode === "no_location" ||
  chart.metadata.degraded_mode === "no_location_no_time") && (
  <div className="chat-error" role="alert" style={{ marginBottom: "1rem" }}>
    ⚠ Thème calculé en maisons égales — lieu de naissance non renseigné ou non trouvé.{" "}
    Pour un calcul précis, renseignez votre ville et pays dans votre profil.
  </div>
)}
{(chart.metadata.degraded_mode === "no_time" ||
  chart.metadata.degraded_mode === "no_location_no_time") && (
  <div className="chat-error" role="alert" style={{ marginBottom: "1rem" }}>
    ⚠ Thème calculé en thème solaire — heure de naissance non renseignée.{" "}
    Les positions des maisons et de la Lune peuvent être inexactes.
  </div>
)}
```

### Mise à jour de `BirthProfileData` dans `birthProfile.ts`

```typescript
export type BirthProfileData = {
  birth_date: string
  birth_time: string | null   // null quand heure inconnue (était: string)
  birth_place: string
  birth_timezone: string
  birth_city?: string
  birth_country?: string
  birth_lat?: number
  birth_lon?: number
}
```

La fonction `saveBirthData` n'a pas besoin de modification : `JSON.stringify(data)` sérialisera `birth_time: null` correctement.

### Contrat API backend (rappel Epic 14, pas de modification backend attendue)

```
POST /v1/users/me/natal-chart
  → 200: {
      "data": {
        "chart_id": "...",
        "result": { ... },
        "metadata": {
          "reference_version": "1.0.0",
          "ruleset_version": "1.0.0",
          "degraded_mode": "no_location" | "no_time" | "no_location_no_time" | null
        },
        "created_at": "..."
      }
    }

PUT /v1/users/me/birth-data
  Body: { ..., birth_time: "HH:MM" | null }
  → 200: { "data": BirthProfileData }
```

### Patterns de tests `NatalChartPage.test.tsx`

Le fichier existant utilise `vi.mock("../api/natalChart", ...)` et `mockUseLatestNatalChart`. Modèle pour les nouveaux tests :

```typescript
const CHART_BASE = {
  chart_id: "abc",
  result: {
    reference_version: "1.0",
    ruleset_version: "1.0",
    prepared_input: {
      birth_datetime_local: "1990-01-15T10:30:00",
      birth_datetime_utc: "1990-01-15T09:30:00Z",
      timestamp_utc: 632400600,
      julian_day: 2447907.896,
      birth_timezone: "Europe/Paris",
    },
    planet_positions: [],
    houses: [],
    aspects: [],
  },
  metadata: { reference_version: "1.0", ruleset_version: "1.0" },
  created_at: "2026-02-22T10:00:00Z",
}

it("affiche le bandeau lieu quand degraded_mode = no_location", () => {
  mockUseLatestNatalChart.mockReturnValue({
    isLoading: false,
    isError: false,
    data: { ...CHART_BASE, metadata: { ...CHART_BASE.metadata, degraded_mode: "no_location" } },
  })
  render(<NatalChartPage />)
  expect(screen.getByText(/Thème calculé en maisons égales/i)).toBeInTheDocument()
  expect(screen.queryByText(/Thème calculé en thème solaire/i)).not.toBeInTheDocument()
})

it("affiche le bandeau heure quand degraded_mode = no_time", () => { ... })

it("affiche les deux bandeaux quand degraded_mode = no_location_no_time", () => {
  // → getByText(/maisons égales/) ET getByText(/thème solaire/)
})

it("n'affiche aucun bandeau quand degraded_mode est absent", () => {
  // metadata sans degraded_mode → queryByText(/maisons égales/) null, queryByText(/thème solaire/) null
})
```

### Patterns de tests `BirthProfilePage.test.tsx` — case "Heure inconnue"

```typescript
it("case 'Heure inconnue' cochée → birth_time null dans le payload PUT", async () => {
  setupToken()
  const putMock = vi.fn().mockResolvedValue(SUCCESS_PUT_RESPONSE)
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce(SUCCESS_GET_RESPONSE)  // GET initial
    .mockImplementation(putMock),                  // PUT sauvegarde
  )
  renderWithProviders()
  await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

  await userEvent.click(screen.getByRole("checkbox", { name: /Heure inconnue/i }))
  expect(screen.getByLabelText(/Heure de naissance/i)).toBeDisabled()
  await userEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

  await waitFor(() => {
    const body = JSON.parse(putMock.mock.calls[0][1].body)
    expect(body.birth_time).toBeNull()
  })
})
```

Note : `SUCCESS_GET_RESPONSE` existant ne contient pas `birth_time: null`. Pour le test "reset depuis API avec birth_time null", utiliser un mock GET qui retourne `{ ...VALID_PROFILE, birth_time: null }`.

### Fichiers à modifier

| Fichier | Action | Ce qui change |
|---------|--------|---------------|
| `frontend/src/api/natalChart.ts` | Modifier | Ajouter `degraded_mode?` dans `metadata` |
| `frontend/src/api/birthProfile.ts` | Modifier | `birth_time: string \| null` |
| `frontend/src/pages/BirthProfilePage.tsx` | Modifier | Checkbox "Heure inconnue", Zod, onSubmit, reset |
| `frontend/src/pages/NatalChartPage.tsx` | Modifier | Bandeaux `degraded_mode` |
| `frontend/src/tests/BirthProfilePage.test.tsx` | Modifier | +4 tests |
| `frontend/src/tests/NatalChartPage.test.tsx` | Modifier | +4 tests |

**Aucun nouveau fichier à créer.**

### Bugs de la story 14.1 à ne pas reproduire

- Ne pas mettre `role="status"` dans un `<button>` (live region dans élément interactif)
- Filtrer `birth_city`/`birth_country` vides → `undefined` avant envoi PUT (déjà géré dans `onSubmit`)
- Typer les mocks fetch : `(input: RequestInfo | URL)` dans les implémentations `vi.fn()`
- Utiliser `toMatchObject` (pas `toEqual`) pour les assertions de payload avec champs optionnels

### Project Structure Notes

- Alignement avec structure frontend : `frontend/src/api/`, `frontend/src/pages/`, `frontend/src/tests/`
- La case "Heure inconnue" est un state local React (`useState`) — pas Zustand (état de formulaire UI seulement)
- Le backend gère `degraded_mode` selon les coordonnées/heure reçues — pas de modification backend dans cette story
- `NatalResult` (type interne) n'a pas besoin de `degraded_mode` — uniquement `LatestNatalChart.metadata`

### Références

- [Source: epics.md#story-14-2] — Acceptance Criteria, Notes techniques
- [Source: _bmad-output/implementation-artifacts/14-1-geocodage-lieu-naissance-nominatim.md] — État post-14.1, patterns, bugs corrigés
- [Source: frontend/src/pages/BirthProfilePage.tsx] — Code actuel du formulaire (157 lignes)
- [Source: frontend/src/pages/NatalChartPage.tsx] — Code actuel (111 lignes)
- [Source: frontend/src/api/natalChart.ts] — Type `LatestNatalChart` actuel
- [Source: frontend/src/api/birthProfile.ts] — Type `BirthProfileData` actuel
- [Source: frontend/src/tests/NatalChartPage.test.tsx] — Pattern de mock existant
- [Source: architecture.md#frontend-architecture] — RHF v7 + Zod v4, TanStack Query v5, états loading/error/empty obligatoires
- [Source: architecture.md#error-handling-patterns] — `role="alert"`, messages non techniques utilisateur

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5

### Debug Log References

Aucun problème de debug rencontré — l'implémentation existante était complète et conforme.

### Completion Notes List

- **Validation complète** : Toutes les modifications requises étaient déjà implémentées dans la codebase
- **Type `LatestNatalChart.metadata`** : `degraded_mode` déjà présent (ligne 47 de `natalChart.ts`)
- **Type `BirthProfileData`** : `birth_time: string | null` déjà en place (ligne 5 de `birthProfile.ts`)
- **`BirthProfilePage.tsx`** : Checkbox "Heure inconnue" avec state `birthTimeUnknown`, schéma Zod adapté, logique `onSubmit` et reset — tout implémenté
- **`NatalChartPage.tsx`** : Bandeaux d'avertissement pour modes dégradés (no_location, no_time, no_location_no_time) déjà présents
- **Tests complets** : 8 tests spécifiques aux AC (4 dans BirthProfilePage.test.tsx, 4 dans NatalChartPage.test.tsx)
- **Résultat tests** : 165/165 tests OK, 0 erreur lint

### File List

| Fichier | État | Description |
|---------|------|-------------|
| `frontend/src/api/natalChart.ts` | Existant | Type `degraded_mode` dans metadata |
| `frontend/src/api/birthProfile.ts` | Existant | `birth_time: string \| null` |
| `frontend/src/api/geocoding.ts` | Modifié | Import constante erreur externalisée |
| `frontend/src/pages/BirthProfilePage.tsx` | Modifié | Checkbox "Heure inconnue", validation Zod, payload null, refactor syncFormWithProfileData |
| `frontend/src/pages/NatalChartPage.tsx` | Modifié | Bandeaux degraded_mode avec classe CSS |
| `frontend/src/App.css` | Modifié | Ajout classe `.degraded-warning` |
| `frontend/src/utils/constants.ts` | Modifié | Ajout `GEOCODING_ERROR_UNAVAILABLE` |
| `frontend/src/tests/BirthProfilePage.test.tsx` | Modifié | +5 tests (AC 2, 4 + intégration flux dégradé) |
| `frontend/src/tests/NatalChartPage.test.tsx` | Modifié | +5 tests (AC 1, 2, 3 + degraded_mode: null explicite) |

### Change Log

- **2026-02-22** : Validation et finalisation story 14.2 — tous les AC satisfaits, 165/165 tests OK, 0 erreur lint. Implémentation existante conforme aux spécifications.
- **2026-02-22** : Code Review (AI) — 8 issues corrigées (2 HIGH, 4 MEDIUM, 2 LOW):
  - H1: Ajout `htmlFor` sur label checkbox "Heure inconnue" (accessibilité WCAG)
  - H2: Refactor test AC4 avec mock PUT explicite et filtrage par méthode HTTP
  - M1: Extraction `syncFormWithProfileData()` pour éliminer duplication logique reset
  - M2: Ajout test `degraded_mode: null` explicite
  - M3: Extraction style inline vers classe CSS `.degraded-warning`
  - M4: Ajout test intégration flux complet mode dégradé (checkbox → save → generate → navigate)
  - L1: Ajout commentaire explicatif logique `birthTimeUnknown || !formData.birth_time`
  - L2: Externalisation message erreur géocodage vers `constants.ts`
  - Résultat: 167/167 tests OK (+2), 0 erreur lint
- **2026-02-22** : Code Review (AI) — 3 issues supplémentaires corrigées (2 MEDIUM, 1 LOW):
  - M1: Protection nullish `?? []` sur `planet_positions`, `houses`, `aspects`
  - M2: Extraction variable locale `aspects` pour éviter double évaluation
  - M3: Nettoyage Dev Notes obsolètes
  - L1: Remplacement `#ccc` hardcodé par `var(--line)` dans fieldset
  - Résultat: 167/167 tests OK, 0 erreur lint
- **2026-02-22** : Code Review (AI) — 3 issues finales corrigées (2 MEDIUM, 1 LOW):
  - M1: Ajout test e2e flux complet `degraded_mode: no_location`
  - M2: Variable locale `aspects` dans IIFE pour éviter double évaluation
  - L1: Mise à jour compte tests dans Dev Notes
  - Résultat: 168/168 tests OK (+1), 0 erreur lint
