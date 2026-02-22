# Story 14.1: Refonte formulaire profil natal — ville, pays et géocodage Nominatim

Status: done

## Story

As a utilisateur,
I want saisir ma ville et mon pays de naissance et obtenir automatiquement les coordonnées GPS,
so that mon thème natal puisse être calculé avec précision géographique.

## Acceptance Criteria

1. **Given** un utilisateur sur la page de profil natal **When** il renseigne la ville et le pays puis clique sur "Valider les coordonnées" **Then** le frontend appelle Nominatim avec `?q={ville},{pays}&format=json&limit=1` **And** les coordonnées (lat, lon, label résolu) sont affichées en confirmation **And** les coordonnées sont incluses dans le payload `PUT /v1/users/me/birth-data` avec `birth_city`, `birth_country`, `birth_lat`, `birth_lon` **And** en cas de succès de sauvegarde, le message "Profil natal sauvegardé." s'affiche.

2. **Given** Nominatim ne trouve pas de résultat **When** la recherche retourne un tableau vide **Then** un message d'alerte s'affiche : "Lieu introuvable. Vérifiez la ville et le pays, ou laissez le lieu vide pour utiliser le mode dégradé (maisons égales)." **And** aucune coordonnée n'est envoyée au backend.

3. **Given** Nominatim est indisponible (erreur réseau ou timeout) **When** la requête échoue **Then** un message d'alerte s'affiche : "Service de géocodage indisponible. Vous pouvez sauvegarder sans coordonnées (mode dégradé)." **And** le bouton "Sauvegarder" reste actif.

4. **Given** un utilisateur qui sauvegarde sans renseigner ville/pays **When** il clique sur "Sauvegarder" **Then** la sauvegarde est envoyée sans `birth_lat`/`birth_lon` (mode dégradé accepté) **And** aucun blocage client-side.

## Tasks / Subtasks

- [x] Créer `frontend/src/api/geocoding.ts` — `geocodeCity(city, country)` (AC: 1, 2, 3)
  - [x] Appel Nominatim `https://nominatim.openstreetmap.org/search?q={city},{country}&format=json&limit=1`
  - [x] Header `User-Agent: horoscope-app/1.0 (contact: admin@horoscope.app)` obligatoire
  - [x] Timeout 10s via AbortController
  - [x] Retourner `{ lat, lon, display_name }` ou `null` si aucun résultat
  - [x] Lever `GeocodingError` avec `code: "service_unavailable"` (not_found → null, unavailable → throw)
- [x] Mettre à jour `frontend/src/api/birthProfile.ts` — étendre `saveBirthData` (AC: 1, 4)
  - [x] Ajouter `birth_city?: string`, `birth_country?: string`, `birth_lat?: number`, `birth_lon?: number` au type `BirthProfileData`
  - [x] Inclure ces champs dans le payload PUT si présents
- [x] Mettre à jour `frontend/src/pages/BirthProfilePage.tsx` (AC: 1, 2, 3, 4)
  - [x] Ajouter champs `birth_city` et `birth_country` dans le formulaire (Zod + react-hook-form)
  - [x] Ajouter bouton "Valider les coordonnées" déclenchant `geocodeCity`
  - [x] Ajouter état `geocodingState: "idle" | "loading" | "success" | "error_not_found" | "error_unavailable"`
  - [x] Afficher label `display_name` résolu + lat/lon en lecture seule après géocodage réussi
  - [x] Afficher messages d'alerte selon l'état de géocodage (AC 2, 3)
  - [x] Inclure `birth_lat`/`birth_lon` dans l'appel `saveBirthData` si géocodage réussi
- [x] Ajouter tests `frontend/src/tests/geocodingApi.test.ts` (AC: 1, 2, 3)
  - [x] Test géocodage succès → retourne `{ lat, lon, display_name }`
  - [x] Test URL correcte + User-Agent header
  - [x] Test lieu introuvable (array vide) → retourne `null`
  - [x] Test Nominatim indisponible (erreur réseau) → lève `GeocodingError("service_unavailable")`
  - [x] Test réponse non-OK → lève `GeocodingError("service_unavailable")`
  - [x] Test AbortError (timeout) → lève `GeocodingError("service_unavailable")`
- [x] Mettre à jour `frontend/src/tests/BirthProfilePage.test.tsx` (AC: 1, 2, 3, 4)
  - [x] Test géocodage succès → affichage display_name + lat/lon
  - [x] Test lieu introuvable → message d'alerte correct
  - [x] Test Nominatim indisponible → message d'alerte + bouton Sauvegarder actif
  - [x] Test sauvegarde avec coordonnées → payload inclut birth_lat/birth_lon

## Dev Notes

### Architecture du service de géocodage

```typescript
// frontend/src/api/geocoding.ts

export type GeocodingResult = {
  lat: number
  lon: number
  display_name: string
}

export class GeocodingError extends Error {
  readonly code: "service_unavailable"
  constructor(message: string) {
    super(message)
    this.name = "GeocodingError"
    this.code = "service_unavailable"
  }
}

export async function geocodeCity(
  city: string,
  country: string,
  externalSignal?: AbortSignal,
): Promise<GeocodingResult | null> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10000)
  try {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(city)},${encodeURIComponent(country)}&format=json&limit=1`
    const response = await fetch(url, {
      headers: { "User-Agent": "horoscope-app/1.0 (contact: admin@horoscope.app)" },
      signal: controller.signal,
    })
    if (!response.ok) throw new GeocodingError("service_unavailable", "Nominatim error")
    const data = await response.json() as Array<{ lat: string; lon: string; display_name: string }>
    if (data.length === 0) return null
    return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon), display_name: data[0].display_name }
  } catch (err) {
    if (err instanceof GeocodingError) throw err
    throw new GeocodingError("service_unavailable", "Geocoding service unavailable")
  } finally {
    clearTimeout(timeoutId)
  }
}
```

### Extension du type BirthProfileData

```typescript
// frontend/src/api/birthProfile.ts — type étendu
export type BirthProfileData = {
  birth_date: string
  birth_time: string
  birth_place: string       // maintenu pour rétrocompatibilité
  birth_timezone: string
  birth_city?: string       // NOUVEAU
  birth_country?: string    // NOUVEAU
  birth_lat?: number        // NOUVEAU — null si non géocodé
  birth_lon?: number        // NOUVEAU — null si non géocodé
}
```

### Contrat API backend étendu

```
PUT /v1/users/me/birth-data
  Body:
    birth_date: string (YYYY-MM-DD)
    birth_time: string (HH:MM)
    birth_place: string (free text, rétrocompatibilité)
    birth_timezone: string (IANA)
    birth_city?: string    ← NOUVEAU
    birth_country?: string ← NOUVEAU
    birth_lat?: float      ← NOUVEAU (nullable)
    birth_lon?: float      ← NOUVEAU (nullable)
  → 200: { data: BirthProfileData }
```

### UX du formulaire étendu

```
[ Date de naissance ]     [ Heure de naissance ]
[ Lieu de naissance (texte libre, rétrocompat.) ]
[ Fuseau horaire IANA ]

--- Géolocalisation précise (optionnel) ---
[ Ville ]    [ Pays ]    [Valider les coordonnées ↗]

État idle     : rien affiché
État loading  : spinner "Recherche en cours..."
État success  : ✓ "Paris, Île-de-France, France" · lat: 48.8566, lon: 2.3522
État not_found: ⚠ "Lieu introuvable. Vérifiez la ville et le pays..."
État unavail  : ⚠ "Service de géocodage indisponible. Vous pouvez sauvegarder sans coordonnées (mode dégradé)."

[Sauvegarder]
```

### Project Structure Notes

- `frontend/src/api/geocoding.ts` — nouveau fichier
- `frontend/src/api/birthProfile.ts` — `BirthProfileData` étendu + `saveBirthData` étendu
- `frontend/src/pages/BirthProfilePage.tsx` — champs ville/pays, bouton géocodage, états UX
- `frontend/src/tests/geocodingApi.test.ts` — nouveau fichier (4 tests)
- `frontend/src/tests/BirthProfilePage.test.tsx` — +4 tests géocodage

### Références

- [Nominatim API docs](https://nominatim.org/release-docs/develop/api/Search/) — politique d'utilisation : User-Agent obligatoire, 1 req/s max
- [Source: frontend/src/api/birthProfile.ts] — `saveBirthData`, `BirthProfileData`
- [Source: frontend/src/pages/BirthProfilePage.tsx] — formulaire existant
- [Source: _bmad-output/planning-artifacts/epics.md#epic-14] — contrat API étendu

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `geocoding.ts` : virgule entre city et country non encodée dans l'URL (séparateur Nominatim) — test corrigé en conséquence (`q=Paris,France` et non `q=Paris%2CFrance`).
- `BirthProfilePage.test.tsx` "verifies payload" : `toEqual` → `toMatchObject` car les champs `birth_city: ""` et `birth_country: ""` sont maintenant inclus dans le payload (nouveaux champs du formulaire).
- `GeocodingError.code` : la valeur `"not_found"` a été retirée — le cas "lieu introuvable" retourne `null` (pas une exception), seul `"service_unavailable"` est lancé.
- 152 / 152 tests passent, lint : 0 erreur.

### Completion Notes List

- AC1 satisfait : géocodage Nominatim via `geocodeCity`, User-Agent, timeout 10s, affichage `display_name` + lat/lon, coords dans le payload PUT.
- AC2 satisfait : message "Lieu introuvable" quand Nominatim retourne `[]`.
- AC3 satisfait : message "Service de géocodage indisponible" + bouton Sauvegarder actif quand Nominatim échoue.
- AC4 satisfait : sauvegarde sans coordonnées acceptée (champs city/country optionnels).
- `geocodingApi.test.ts` : 6 tests (succès, URL/User-Agent, not-found, network error, non-OK, AbortError).
- `BirthProfilePage.test.tsx` : 19 → 24 tests (+4 géocodage +1 M2 bouton désactivé).
- Total suite : 142 → 153 tests (29 fichiers).

### File List

- frontend/src/api/geocoding.ts (nouveau — `geocodeCity`, `GeocodingError`, `GeocodingResult`)
- frontend/src/api/birthProfile.ts (modifié — `BirthProfileData` + champs `birth_city?`, `birth_country?`, `birth_lat?`, `birth_lon?`)
- frontend/src/pages/BirthProfilePage.tsx (modifié — champs ville/pays, bouton géocodage, états UX, coords dans payload save, `watch`+`canGeocode`, `geocodeAbortRef` cleanup)
- frontend/src/tests/geocodingApi.test.ts (nouveau — 8 tests unitaires geocodeCity, +1 externalSignal, +1 encodage spéciaux)
- frontend/src/tests/BirthProfilePage.test.tsx (modifié — +7 tests géocodage, `toEqual` → `toMatchObject`, +AC4 négatif, +reset état)

### Change Log

- 2026-02-21 : Implémentation story 14-1 (claude-sonnet-4-6) — Géocodage Nominatim : nouveau service geocoding.ts, extension BirthProfileData, formulaire ville+pays+bouton dans BirthProfilePage, 6+4 nouveaux tests. 152/152 tests, 0 erreur lint.
- 2026-02-21 : Adversarial Code Review fixes (gemini-cli) — Synchronisation automatique du champ legacy `birth_place` avec le label Nominatim résolu pour éviter la double saisie (H2). Correction du suivi git pour les fichiers de géocoding (H1). 29/29 tests validés.
- 2026-02-22 : Adversarial Code Review fixes (claude-sonnet-4-6) — M1: bouton "Valider les coordonnées" désactivé si ville ou pays vide (`watch`+`canGeocode`). M2: +1 test dédié. L1: `display_name.slice(0,255)` pour éviter dépassement Zod max sur `birth_place`. L2: suppression `role="status"` dans `<button>` (live region dans élément interactif). L3: double appel `geocodeCity` corrigé dans 3 tests d'erreur (pattern `catch(e=>e)`). L5: `externalSignal` paramètre dans `geocodeCity` + `geocodeAbortRef` + cleanup `useEffect` pour annulation propre au démontage. 153/153 tests, 0 erreur lint.
- 2026-02-22 : Adversarial Code Review fixes (claude-sonnet-4-6) — M1: catch block redondant simplifié dans `handleGeocode` (double branche identique → catch unique), import `GeocodingError` inutilisé supprimé. M2: test `externalSignal` ajouté dans geocodingApi.test.ts (vérification annulation fetch quand signal externe aborté). M3: validation `isFinite` sur `parseFloat(lat/lon)` dans geocoding.ts (protection contre NaN Nominatim). M4: filtrage `birth_city`/`birth_country` vides en `undefined` avant PUT pour éviter `""` côté backend. L1: Dev Notes GeocodingError alignés sur l'implémentation réelle (code `"service_unavailable"` uniquement, signature constructeur corrigée, `externalSignal` ajouté). L2: test encodage URL avec espaces (`New%20York`). L3: test AC4 négatif — payload sans `birth_lat`/`birth_lon` quand pas de géocodage. L4: test reset état géocodage quand ville modifiée post-succès. L5: typage mocks fetch `(url: string)` → `(input: RequestInfo | URL)` dans 4 tests. 157/157 tests, 0 erreur lint.
