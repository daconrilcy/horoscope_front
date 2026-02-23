# Story 14.3: Table de traduction des termes astrologiques (FR/EN/ES)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur,
I want voir les termes astrologiques (maisons, signes, planètes) dans ma langue,
so that je comprenne facilement mon thème natal sans termes techniques en anglais.

## Acceptance Criteria

1. **Given** un thème natal affiché en français (langue par défaut) **When** l'utilisateur consulte la page `NatalChartPage` **Then** les noms des signes sont affichés en français (ex: "Bélier" au lieu de "aries") **And** les noms des planètes sont affichés en français (ex: "Soleil" au lieu de "sun") **And** les maisons sont affichées avec leur nom traditionnel en français (ex: "Maison I — Identité")

2. **Given** l'architecture i18n des termes astrologiques **When** un développeur veut ajouter une nouvelle langue (ex: allemand) **Then** il suffit d'ajouter une clé de langue dans `frontend/src/i18n/astrology.ts` sans modifier aucun composant

3. **Given** un code inconnu retourné par l'API (ex: nouveau planète ou signe non répertorié) **When** la traduction est absente **Then** le code brut est affiché en fallback (ex: "chiron") sans erreur

## Tasks / Subtasks

- [x] Créer le fichier `frontend/src/i18n/astrology.ts` avec les dictionnaires de traduction (AC: 1, 2, 3)
  - [x] Définir le type `AstrologyLang = "fr" | "en" | "es"`
  - [x] Définir les 12 signes : aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces
  - [x] Définir les 10 planètes : sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto
  - [x] Définir les 12 maisons avec numéro + nom symbolique (ex: "Maison I — Identité")
  - [x] Définir les aspects majeurs : conjunction, sextile, square, trine, opposition
  - [x] Fonction `translateSign(code: string, lang: AstrologyLang): string` avec fallback code brut
  - [x] Fonction `translatePlanet(code: string, lang: AstrologyLang): string` avec fallback code brut
  - [x] Fonction `translateHouse(number: number, lang: AstrologyLang): string` avec fallback `"Maison ${number}"`
  - [x] Fonction `translateAspect(code: string, lang: AstrologyLang): string` avec fallback code brut

- [x] Créer le hook `useAstrologyLabels()` dans `frontend/src/i18n/astrology.ts` (AC: 1, 2)
  - [x] Priorité 1 : `localStorage.getItem("lang")` si défini et valide
  - [x] Priorité 2 : `navigator.language` (préfixe 2 lettres)
  - [x] Fallback final sur `"fr"` si langue non supportée
  - [x] Retourner `{ lang, translateSign, translatePlanet, translateHouse, translateAspect }`

- [x] Mettre à jour `NatalChartPage.tsx` pour utiliser les traductions (AC: 1, 3)
  - [x] Importer `useAstrologyLabels` depuis `../i18n/astrology`
  - [x] Appeler le hook au début du composant
  - [x] Utiliser `translatePlanet(item.planet_code)` (fonction bound, sans param lang)
  - [x] Utiliser `translateSign(item.sign_code)` (fonction bound, sans param lang)
  - [x] Utiliser `translateHouse(item.number)` (fonction bound, sans param lang)
  - [x] Utiliser `translateAspect(item.aspect_code)` (fonction bound, sans param lang)

- [x] Tests unitaires `frontend/src/tests/astrology-i18n.test.ts` (AC: 1, 2, 3)
  - [x] Test : `translateSign("aries", "fr")` → "Bélier"
  - [x] Test : `translateSign("aries", "en")` → "Aries"
  - [x] Test : `translateSign("aries", "es")` → "Aries"
  - [x] Test : `translateSign("ARIES", "fr")` → "Bélier" (case-insensitive)
  - [x] Test : `translateSign("unknown_sign", "fr")` → "unknown_sign" (fallback)
  - [x] Test : `translatePlanet("sun", "fr")` → "Soleil"
  - [x] Test : `translatePlanet("SUN", "fr")` → "Soleil" (case-insensitive)
  - [x] Test : `translatePlanet("chiron", "fr")` → "chiron" (fallback)
  - [x] Test : `translateHouse(1, "fr")` → "Maison I — Identité"
  - [x] Test : `translateHouse(1, "en")` → "House I — Identity"
  - [x] Test : `translateHouse(13, "fr")` → "Maison 13" (fallback)
  - [x] Test : `translateAspect("conjunction", "fr")` → "Conjonction"
  - [x] Test : `translateAspect("TRINE", "fr")` → "Trigone" (case-insensitive)
  - [x] Test : `translateAspect("unknown", "fr")` → "unknown" (fallback)

- [x] Tests d'intégration `frontend/src/tests/NatalChartPage.test.tsx` (AC: 1)
  - [x] Test : les planètes sont affichées en français ("Soleil" pas "SUN")
  - [x] Test : les signes sont affichés en français ("Gémeaux" pas "GEMINI")
  - [x] Test : les maisons sont affichées avec nom symbolique
  - [x] Test : les aspects sont affichés en français ("Trigone" pas "TRINE")

## Dev Notes

### Dictionnaire des signes (12)

| Code | FR | EN | ES |
|------|-----|-----|-----|
| aries | Bélier | Aries | Aries |
| taurus | Taureau | Taurus | Tauro |
| gemini | Gémeaux | Gemini | Géminis |
| cancer | Cancer | Cancer | Cáncer |
| leo | Lion | Leo | Leo |
| virgo | Vierge | Virgo | Virgo |
| libra | Balance | Libra | Libra |
| scorpio | Scorpion | Scorpio | Escorpio |
| sagittarius | Sagittaire | Sagittarius | Sagitario |
| capricorn | Capricorne | Capricorn | Capricornio |
| aquarius | Verseau | Aquarius | Acuario |
| pisces | Poissons | Pisces | Piscis |

### Dictionnaire des planètes (10)

| Code | FR | EN | ES |
|------|-----|-----|-----|
| sun | Soleil | Sun | Sol |
| moon | Lune | Moon | Luna |
| mercury | Mercure | Mercury | Mercurio |
| venus | Vénus | Venus | Venus |
| mars | Mars | Mars | Marte |
| jupiter | Jupiter | Jupiter | Júpiter |
| saturn | Saturne | Saturn | Saturno |
| uranus | Uranus | Uranus | Urano |
| neptune | Neptune | Neptune | Neptuno |
| pluto | Pluton | Pluto | Plutón |

### Dictionnaire des maisons (12)

| # | FR | EN | ES |
|---|-----|-----|-----|
| 1 | Maison I — Identité | House I — Identity | Casa I — Identidad |
| 2 | Maison II — Valeurs | House II — Values | Casa II — Valores |
| 3 | Maison III — Communication | House III — Communication | Casa III — Comunicación |
| 4 | Maison IV — Foyer | House IV — Home | Casa IV — Hogar |
| 5 | Maison V — Créativité | House V — Creativity | Casa V — Creatividad |
| 6 | Maison VI — Santé | House VI — Health | Casa VI — Salud |
| 7 | Maison VII — Relations | House VII — Relationships | Casa VII — Relaciones |
| 8 | Maison VIII — Transformation | House VIII — Transformation | Casa VIII — Transformación |
| 9 | Maison IX — Philosophie | House IX — Philosophy | Casa IX — Filosofía |
| 10 | Maison X — Carrière | House X — Career | Casa X — Carrera |
| 11 | Maison XI — Communauté | House XI — Community | Casa XI — Comunidad |
| 12 | Maison XII — Inconscient | House XII — Unconscious | Casa XII — Inconsciente |

### Dictionnaire des aspects (9 aspects)

| Code | FR | EN | ES |
|------|-----|-----|-----|
| conjunction | Conjonction | Conjunction | Conjunción |
| sextile | Sextile | Sextile | Sextil |
| square | Carré | Square | Cuadratura |
| trine | Trigone | Trine | Trígono |
| opposition | Opposition | Opposition | Oposición |
| semisextile | Semi-sextile | Semi-sextile | Semisextil |
| quincunx | Quinconce | Quincunx | Quincuncio |
| semisquare | Semi-carré | Semi-square | Semicuadratura |
| sesquiquadrate | Sesqui-carré | Sesquiquadrate | Sesquicuadratura |

### Implémentation actuelle `astrology.ts`

Le module utilise un vrai hook React avec `useState`/`useEffect` pour la réactivité :

```typescript
import { useCallback, useEffect, useState } from "react"

export type AstrologyLang = "fr" | "en" | "es"

const HOUSE_FALLBACK_PREFIX: Record<AstrologyLang, string> = {
  fr: "Maison", en: "House", es: "Casa",
}

const SIGNS: Record<string, Record<AstrologyLang, string>> = { /* 12 signes */ }
const PLANETS: Record<string, Record<AstrologyLang, string>> = { /* 10 planètes */ }
const HOUSES: Record<number, Record<AstrologyLang, string>> = { /* 12 maisons */ }
const ASPECTS: Record<string, Record<AstrologyLang, string>> = { /* 5 aspects */ }

const SUPPORTED_LANGS: AstrologyLang[] = ["fr", "en", "es"]
const LANG_STORAGE_KEY = "lang"

// Fonctions de traduction pures (exportées pour tests unitaires)
export function translateSign(code: string, lang: AstrologyLang): string { /* ... */ }
export function translatePlanet(code: string, lang: AstrologyLang): string { /* ... */ }
export function translateHouse(number: number, lang: AstrologyLang): string { /* ... */ }
export function translateAspect(code: string, lang: AstrologyLang): string { /* ... */ }

export function detectLang(): AstrologyLang {
  // Priorité: localStorage > navigator.language > "fr"
}

export function useAstrologyLabels() {
  const [lang, setLangState] = useState<AstrologyLang>(detectLang)

  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === LANG_STORAGE_KEY) setLangState(detectLang())
    }
    window.addEventListener("storage", handleStorageChange)
    return () => window.removeEventListener("storage", handleStorageChange)
  }, [])

  const setLang = useCallback((newLang: AstrologyLang) => {
    localStorage.setItem(LANG_STORAGE_KEY, newLang)
    setLangState(newLang)
  }, [])

  // Fonctions bound avec useCallback (pas besoin de passer lang)
  const boundTranslateSign = useCallback((code: string) => translateSign(code, lang), [lang])
  // ... idem pour planet, house, aspect

  return { lang, setLang, translateSign: boundTranslateSign, /* ... */ }
}
```

**Points clés de l'implémentation :**
- `useState` + `useEffect` pour réactivité React
- `setLang` persiste dans `localStorage` ET met à jour l'état
- Écoute `storage` event pour sync entre onglets
- Fonctions bound via `useCallback` (pas de param `lang` requis à l'appel)
- `HOUSE_FALLBACK_PREFIX` pour extensibilité des langues

### Mise à jour de `NatalChartPage.tsx`

Avant (ligne 88-91 actuel) :

```tsx
{(chart.result.planet_positions ?? []).map((item) => (
  <li key={item.planet_code}>
    {item.planet_code}: {item.sign_code} ({item.longitude.toFixed(2)}°), maison {item.house_number}
  </li>
))}
```

Après :

```tsx
const { translatePlanet, translateSign, translateHouse, translateAspect } = useAstrologyLabels()
// ...
{(chart.result.planet_positions ?? []).map((item) => (
  <li key={item.planet_code}>
    {translatePlanet(item.planet_code)}: {translateSign(item.sign_code)} ({item.longitude.toFixed(2)}°), {translateHouse(item.house_number)}
  </li>
))}
```

Pour les maisons (ligne 99-102) :

```tsx
{(chart.result.houses ?? []).map((item) => (
  <li key={item.number}>
    {translateHouse(item.number)}: cuspide {item.cusp_longitude.toFixed(2)}°
  </li>
))}
```

Pour les aspects (ligne 116-119) :

```tsx
{aspects.map((item) => (
  <li key={`${item.aspect_code}-${item.planet_a}-${item.planet_b}`}>
    {translateAspect(item.aspect_code)}: {translatePlanet(item.planet_a)} - {translatePlanet(item.planet_b)} (angle {item.angle.toFixed(2)}°, orbe {item.orb.toFixed(2)}°)
  </li>
))}
```

### Gestion des codes API

L'API retourne actuellement des codes en MAJUSCULES (ex: `"SUN"`, `"GEMINI"`, `"TRINE"`). Les fonctions de traduction normalisent en lowercase via `code.toLowerCase()` pour une correspondance robuste.

### Extensibilité pour nouvelles langues (AC2)

Pour ajouter l'allemand (`de`) :

1. Modifier le type : `export type AstrologyLang = "fr" | "en" | "es" | "de"`
2. Ajouter `de` dans `SUPPORTED_LANGS` et `HOUSE_FALLBACK_PREFIX`
3. Ajouter les entrées dans chaque dictionnaire :

```typescript
aries: { fr: "Bélier", en: "Aries", es: "Aries", de: "Widder" },
```

4. Aucune modification des composants n'est nécessaire.

### Project Structure Notes

- **Nouveau dossier** : `frontend/src/i18n/` — dédié à l'internationalisation
- **Nouveau fichier** : `frontend/src/i18n/astrology.ts` — dictionnaires et hook
- **Fichier modifié** : `frontend/src/pages/NatalChartPage.tsx` — utilisation des traductions
- **Nouveau test** : `frontend/src/tests/astrology-i18n.test.ts` — tests unitaires du module i18n
- **Tests modifiés** : `frontend/src/tests/NatalChartPage.test.tsx` — assertions sur texte traduit

### Alignment avec l'architecture

- Pattern de nommage : hook `useXxx` conforme aux conventions (`useAstrologyLabels`)
- Pas de logique métier dans les composants UI — le module i18n est dans `src/i18n/`
- Aucune dépendance externe ajoutée — i18n léger sans bibliothèque (conforme KISS)
- Tests obligatoires pour nouveau module

### Bugs de la story 14.2 à ne pas reproduire

- Utiliser `.toLowerCase()` pour normaliser les codes API (case-insensitive)
- Retourner le code brut en fallback, jamais `undefined` ou erreur
- Tester les cas edge (codes inconnus, numéros de maison hors range)

### References

- [Source: epics.md#story-14-3] — Acceptance Criteria, Notes techniques
- [Source: _bmad-output/implementation-artifacts/14-2-modes-degrades-lieu-heure-absents.md] — Patterns de tests, leçons apprises
- [Source: frontend/src/pages/NatalChartPage.tsx] — Code actuel (129 lignes)
- [Source: frontend/src/api/natalChart.ts] — Types PlanetPosition, HouseResult, AspectResult
- [Source: architecture.md#naming-patterns] — Conventions de nommage hooks/fichiers
- [Source: architecture.md#project-structure] — Organisation frontend `src/`
- [Source: docs/recherches astro/01_Langage_astro_signes_planetes_maisons.md] — Terminologie astrologique de référence

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5

### Debug Log References

- Tests i18n : problème initial avec `navigator.language` retournant "en" dans jsdom → résolu avec `vi.stubGlobal("navigator", { language: "fr-FR" })` dans `beforeEach`
- Tests NatalChartPage : "Soleil" apparaissait 2 fois (planète + aspect) → corrigé avec `getAllByText` au lieu de `getByText`

### Completion Notes List

- **Module i18n créé** : `frontend/src/i18n/astrology.ts` avec dictionnaires complets FR/EN/ES pour 12 signes, 10 planètes, 12 maisons, 5 aspects
- **Hook `useAstrologyLabels`** : vrai hook React avec `useState`/`useEffect`, réactif aux changements de localStorage (événement "storage")
- **Détection de langue** : priorité `localStorage.getItem("lang")` > `navigator.language` > fallback `"fr"`
- **Fonctions bound** : le hook retourne des fonctions partiellement appliquées (pas besoin de passer `lang` à chaque appel)
- **Normalisation case-insensitive** : tous les codes API en MAJUSCULES sont convertis en lowercase pour correspondance robuste
- **Fallback gracieux** : codes inconnus retournés tels quels (pas d'erreur)
- **NatalChartPage mis à jour** : planètes, signes, maisons et aspects maintenant traduits dynamiquement
- **69 tests unitaires i18n** : couverture complète avec `it.each` pour tous les dictionnaires (9 aspects) + test persistance localStorage
- **13 tests d'intégration** : validation de l'affichage en français dans NatalChartPage
- **Extensibilité AC2** : ajouter une langue = modifier le type + ajouter entrées dans dictionnaires + `HOUSE_FALLBACK_PREFIX`

### File List

| Fichier | État | Description |
|---------|------|-------------|
| `frontend/src/i18n/astrology.ts` | Modifié | Module i18n avec vrai hook React réactif, JSDoc complet |
| `frontend/src/pages/NatalChartPage.tsx` | Modifié | Utilise les fonctions bound (sans paramètre lang) |
| `frontend/src/tests/astrology-i18n.test.ts` | Modifié | 69 tests avec `it.each`, 9 aspects, tests hook React + persistance |
| `frontend/src/tests/NatalChartPage.test.tsx` | Modifié | 13 tests i18n, mock `navigator.language` |

### Change Log

- **2026-02-22** : Implémentation story 14.3 — module i18n astrology (FR/EN/ES), hook `useAstrologyLabels`, intégration dans NatalChartPage. 199/199 tests OK, 0 erreur lint.
- **2026-02-22** : Code review AI round 1 — Corrigé M1 (hook conditionnel), M2 (retour fonctions pures), L1 (tests hook), L2 (status done). +7 tests useAstrologyLabels.
- **2026-02-22** : Code review AI round 2 — Corrigé M1 (doc priorité localStorage/navigator), L1 (test count 27), L2 (change log 199 tests).
- **2026-02-22** : Code review AI round 3 — Refonte majeure: H1 (vrai hook React useState/useEffect), H2 (test storage event), M1 (JSDoc API), M2 (tests edge navigator vide/undefined), M3 (HOUSE_FALLBACK_PREFIX), L1 (it.each paramétré), L2 (JSDoc complet). 77/77 tests OK, 0 erreur lint.
- **2026-02-22** : Code review AI round 4 — M2 (setLang persiste dans localStorage), M3 (test persistance), L1 (JSDoc example corrigé), M1/L3 (doc story synchronisée avec implémentation). 78/78 tests OK.
- **2026-02-22** : Code review AI round 5 — M2 (guard SSR sur setLang), L1 (+4 aspects mineurs: semisextile, quincunx, semisquare, sesquiquadrate), L3 (export SUPPORTED_LANGS). 82/82 tests OK.
