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
  - [x] Remplacer `item.planet_code` par `translatePlanet(item.planet_code, lang)`
  - [x] Remplacer `item.sign_code` par `translateSign(item.sign_code, lang)`
  - [x] Remplacer `"Maison ${item.number}"` par `translateHouse(item.number, lang)`
  - [x] Remplacer `item.aspect_code` par `translateAspect(item.aspect_code, lang)`

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

### Dictionnaire des aspects (5 majeurs)

| Code | FR | EN | ES |
|------|-----|-----|-----|
| conjunction | Conjonction | Conjunction | Conjunción |
| sextile | Sextile | Sextile | Sextil |
| square | Carré | Square | Cuadratura |
| trine | Trigone | Trine | Trígono |
| opposition | Opposition | Opposition | Oposición |

### Implémentation recommandée `astrology.ts`

```typescript
export type AstrologyLang = "fr" | "en" | "es"

const SIGNS: Record<string, Record<AstrologyLang, string>> = {
  aries: { fr: "Bélier", en: "Aries", es: "Aries" },
  taurus: { fr: "Taureau", en: "Taurus", es: "Tauro" },
  gemini: { fr: "Gémeaux", en: "Gemini", es: "Géminis" },
  cancer: { fr: "Cancer", en: "Cancer", es: "Cáncer" },
  leo: { fr: "Lion", en: "Leo", es: "Leo" },
  virgo: { fr: "Vierge", en: "Virgo", es: "Virgo" },
  libra: { fr: "Balance", en: "Libra", es: "Libra" },
  scorpio: { fr: "Scorpion", en: "Scorpio", es: "Escorpio" },
  sagittarius: { fr: "Sagittaire", en: "Sagittarius", es: "Sagitario" },
  capricorn: { fr: "Capricorne", en: "Capricorn", es: "Capricornio" },
  aquarius: { fr: "Verseau", en: "Aquarius", es: "Acuario" },
  pisces: { fr: "Poissons", en: "Pisces", es: "Piscis" },
}

const PLANETS: Record<string, Record<AstrologyLang, string>> = {
  sun: { fr: "Soleil", en: "Sun", es: "Sol" },
  moon: { fr: "Lune", en: "Moon", es: "Luna" },
  mercury: { fr: "Mercure", en: "Mercury", es: "Mercurio" },
  venus: { fr: "Vénus", en: "Venus", es: "Venus" },
  mars: { fr: "Mars", en: "Mars", es: "Marte" },
  jupiter: { fr: "Jupiter", en: "Jupiter", es: "Júpiter" },
  saturn: { fr: "Saturne", en: "Saturn", es: "Saturno" },
  uranus: { fr: "Uranus", en: "Uranus", es: "Urano" },
  neptune: { fr: "Neptune", en: "Neptune", es: "Neptuno" },
  pluto: { fr: "Pluton", en: "Pluto", es: "Plutón" },
}

const HOUSES: Record<number, Record<AstrologyLang, string>> = {
  1: { fr: "Maison I — Identité", en: "House I — Identity", es: "Casa I — Identidad" },
  2: { fr: "Maison II — Valeurs", en: "House II — Values", es: "Casa II — Valores" },
  // ... (12 maisons)
}

const ASPECTS: Record<string, Record<AstrologyLang, string>> = {
  conjunction: { fr: "Conjonction", en: "Conjunction", es: "Conjunción" },
  sextile: { fr: "Sextile", en: "Sextile", es: "Sextil" },
  square: { fr: "Carré", en: "Square", es: "Cuadratura" },
  trine: { fr: "Trigone", en: "Trine", es: "Trígono" },
  opposition: { fr: "Opposition", en: "Opposition", es: "Oposición" },
}

export function translateSign(code: string, lang: AstrologyLang): string {
  const entry = SIGNS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

export function translatePlanet(code: string, lang: AstrologyLang): string {
  const entry = PLANETS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

export function translateHouse(number: number, lang: AstrologyLang): string {
  const entry = HOUSES[number]
  if (!entry) {
    const prefix = lang === "en" ? "House" : lang === "es" ? "Casa" : "Maison"
    return `${prefix} ${number}`
  }
  return entry[lang]
}

export function translateAspect(code: string, lang: AstrologyLang): string {
  const entry = ASPECTS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

function detectLang(): AstrologyLang {
  const stored = typeof localStorage !== "undefined" ? localStorage.getItem("lang") : null
  if (stored && ["fr", "en", "es"].includes(stored)) {
    return stored as AstrologyLang
  }
  const nav = typeof navigator !== "undefined" ? navigator.language?.substring(0, 2) : "fr"
  if (["fr", "en", "es"].includes(nav)) {
    return nav as AstrologyLang
  }
  return "fr"
}

export function useAstrologyLabels() {
  const lang = detectLang()
  return {
    lang,
    translateSign: (code: string) => translateSign(code, lang),
    translatePlanet: (code: string) => translatePlanet(code, lang),
    translateHouse: (number: number) => translateHouse(number, lang),
    translateAspect: (code: string) => translateAspect(code, lang),
  }
}
```

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
2. Ajouter les entrées dans chaque dictionnaire :

```typescript
aries: { fr: "Bélier", en: "Aries", es: "Aries", de: "Widder" },
```

3. Aucune modification des composants n'est nécessaire.

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
- **Hook `useAstrologyLabels`** : détection automatique de langue via `localStorage.getItem("lang")` > `navigator.language` > fallback `"fr"`
- **Normalisation case-insensitive** : tous les codes API en MAJUSCULES sont convertis en lowercase pour correspondance robuste
- **Fallback gracieux** : codes inconnus retournés tels quels (pas d'erreur)
- **NatalChartPage mis à jour** : planètes, signes, maisons et aspects maintenant traduits dynamiquement
- **20 tests unitaires i18n** : couverture complète des 4 fonctions de traduction + cas edge
- **4 tests d'intégration** : validation de l'affichage en français dans NatalChartPage
- **Extensibilité AC2** : ajouter une langue = modifier le type + ajouter les entrées dans les dictionnaires, aucun composant à modifier

### File List

| Fichier | État | Description |
|---------|------|-------------|
| `frontend/src/i18n/astrology.ts` | Nouveau | Module i18n avec dictionnaires et hook |
| `frontend/src/pages/NatalChartPage.tsx` | Modifié | Utilise les traductions pour planètes, signes, maisons, aspects |
| `frontend/src/tests/astrology-i18n.test.ts` | Nouveau | 27 tests unitaires du module i18n (20 translate + 7 hook) |
| `frontend/src/tests/NatalChartPage.test.tsx` | Modifié | +4 tests i18n, mock `navigator.language` |

### Change Log

- **2026-02-22** : Implémentation story 14.3 — module i18n astrology (FR/EN/ES), hook `useAstrologyLabels`, intégration dans NatalChartPage. 199/199 tests OK, 0 erreur lint.
- **2026-02-22** : Code review AI round 1 — Corrigé M1 (hook conditionnel), M2 (retour fonctions pures), L1 (tests hook), L2 (status done). +7 tests useAstrologyLabels.
- **2026-02-22** : Code review AI round 2 — Corrigé M1 (doc priorité localStorage/navigator), L1 (test count 27), L2 (change log 199 tests).
