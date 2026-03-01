# Story 29-N4 — UI : Rendu AstroResponse_v1 + Parcours Upsell

## Contexte & Périmètre

**Epic NATAL-6 / Story N4**
**Chapitre 29** — Interprétation natale via LLMGateway

Le frontend affiche actuellement les données brutes du thème natal (planètes, maisons, aspects) dans `NatalChartPage.tsx`.
Cette story ajoute une section d'interprétation IA au bas de la page, avec deux niveaux :
- **SIMPLE** (`natal_interpretation_short`) : accessible à tous, appel automatique après chargement du chart
- **COMPLETE** (`natal_interpretation`) : payant, déblocable via CTA upsell + sélection d'astrologue

**Dépend de :** Story N2 (endpoint `POST /v1/natal/interpretation`)

---

## Architecture UI cible

```
NatalChartPage
  ├─ [existant] Section données brutes (planètes, maisons, aspects)
  └─ [NOUVEAU] Section interprétation IA
        ├─ Si interpretation SIMPLE disponible :
        │    ├─ InterpretationCard (titre + summary)
        │    ├─ HighlightsChips (highlights[])
        │    ├─ SectionAccordion (sections[] avec clé, heading, content)
        │    ├─ AdviceList (advice[])
        │    ├─ EvidenceTags (evidence[] — discret)
        │    ├─ Disclaimers (disclaimers[])
        │    └─ CTA Upsell → "Débloquer l'interprétation complète"
        │
        ├─ Si COMPLETE débloquée :
        │    ├─ [mêmes composants mais avec plus de contenu]
        │    └─ PersonaSelector (choisir l'astrologue)
        │
        └─ Skeleton pendant le chargement
```

---

## Hypothèses & Dépendances

- L'endpoint `POST /v1/natal/interpretation` existe (N2) et retourne `AstroInterpretationResponse`
- Le frontend utilise React + TypeScript + React Query
- Le projet suit le pattern existant : `useQuery` dans `natalChart.ts`, composants dans `components/`
- Les traductions suivent le pattern de `natalChart.ts` (objet `record<lang, translations>`)
- Il n'y a **pas encore de système de paiement** dans cette story : `use_case_level = "complete"` est déclenché par un flag local (localStorage ou state) pour simuler le déblocage
- La sélection de persona (astrologue) utilise l'API existante `frontend/src/api/astrologers.ts`
- Les styles suivent les classes CSS existantes : `.panel`, `.card`, `.grid`, `.chat-error`

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Afficher AstroResponse_v1 de façon lisible et structurée
- Parcours upsell fonctionnel (free → CTA → complete)
- Sélection de persona intégrée pour le niveau COMPLETE
- Fallback gracieux (si l'interprétation échoue, les données brutes restent visibles)
- Chargement asynchrone non bloquant (ne ralentit pas l'affichage du chart)

**Non-Objectifs :**
- Pas d'intégration Stripe/paiement réel dans cette story
- Pas de cache backend des résultats (à faire dans une story technique séparée)
- Pas d'animation complexe

---

## Acceptance Criteria

### AC1 — Hook `useNatalInterpretation`

**Fichier :** `frontend/src/api/natalChart.ts` (ou nouveau fichier `natalInterpretation.ts`)

```typescript
type AstroSection = {
  key: string
  heading: string
  content: string
}

type AstroInterpretation = {
  title: string
  summary: string
  sections: AstroSection[]
  highlights: string[]
  advice: string[]
  evidence: string[]
  disclaimers: string[]
}

type InterpretationMeta = {
  prompt_version_id: string | null
  persona_id: string | null
  model: string
  latency_ms: number
  validation_status: string
  repair_attempted: boolean
  fallback_triggered: boolean
}

type NatalInterpretationResult = {
  chart_id: string
  use_case: string
  interpretation: AstroInterpretation
  meta: InterpretationMeta
  degraded_mode: string | null
}

function useNatalInterpretation(options: {
  enabled: boolean
  useCaseLevel: "short" | "complete"
  personaId?: string | null
  locale?: string
}): UseQueryResult<NatalInterpretationResult, ApiError>
```

- Appelle `POST /v1/natal/interpretation` avec `use_case_level`, `persona_id`, `locale`
- `enabled` contrôle si l'appel est lancé (ne pas appeler si le chart n'est pas encore chargé)
- `staleTime: 1000 * 60 * 10` (10 minutes — interprétation stable)
- La `queryKey` inclut `[useCaseLevel, personaId]` pour que les deux niveaux soient cachés séparément

### AC2 — Section interprétation SIMPLE affichée automatiquement

Quand le chart est chargé et l'interprétation SIMPLE est disponible :
- Titre `interpretation.title` affiché en `<h2>`
- `interpretation.summary` affiché en paragraphe intro
- `interpretation.highlights` affichés en chips/tags horizontaux
- `interpretation.sections` affichées en accordéon (au moins 3 sections attendues)
- `interpretation.advice` affiché en liste numérotée
- `interpretation.disclaimers` affiché en texte discret sous la liste

### AC3 — Skeleton de chargement
Pendant le chargement de l'interprétation :
- Afficher un placeholder "skeleton" dans la section interprétation
- Le reste de la page (données brutes) reste visible et interactif

### AC4 — CTA Upsell COMPLETE visible
Sous l'interprétation SIMPLE :
- Un bloc CTA avec le texte "Débloquer l'interprétation complète avec un astrologue"
- Bouton : "Choisir mon astrologue"
- En cliquant : ouvre un panneau de sélection de persona

### AC5 — PersonaSelector intégré
Le sélecteur d'astrologue (pour le niveau COMPLETE) :
- Liste les personas disponibles (via `GET /v1/astrologers` ou données statiques de la seed)
- Affiche nom + description de chaque persona
- Bouton "Demander l'interprétation complète" déclenche l'appel avec `use_case_level=complete` et `persona_id`
- Pendant le chargement : spinner + message "Votre astrologue interprète votre thème..."

### AC6 — Niveau COMPLETE remplace le niveau SIMPLE
Quand l'interprétation COMPLETE est chargée :
- Elle remplace l'interprétation SIMPLE (pas de doublon)
- Le nom de la persona est visible : "Interprétation par [Persona Name]"
- Le badge "Complet" indique le niveau

### AC7 — Gestion des erreurs d'interprétation
Si l'appel à `POST /v1/natal/interpretation` échoue :
- Ne pas casser l'affichage des données brutes du chart
- Afficher un message discret : "L'interprétation n'est pas disponible pour le moment."
- Bouton "Réessayer" pour relancer l'appel

### AC8 — Mode dégradé signalé dans l'interprétation
Si `degraded_mode != null` dans la réponse :
- Afficher un badge/notice discrète : "Interprétation partielle (heure de naissance inconnue)"

### AC9 — Evidence tags discrets
`interpretation.evidence` est affiché sous forme de petits tags techniques en bas de la section, visibles mais discrets, pour la traçabilité.

### AC10 — Traductions i18n (fr + en minimum)

Nouvelles clés à ajouter dans `natalChartTranslations` :

```typescript
interpretation: {
  loading: string
  title: string  // "Interprétation de votre thème natal"
  upsellTitle: string  // "Interprétation complète"
  upsellCta: string  // "Choisir mon astrologue"
  upsellDescription: string
  completeBy: string  // "Interprétation par"
  completeBadge: string  // "Complet"
  highlightsTitle: string  // "Points clés"
  adviceTitle: string  // "Conseils"
  evidenceTitle: string  // "Sources astrologiques"
  disclaimerTitle: string  // "Note"
  error: string
  retry: string
  degradedNotice: string
  requestingComplete: string  // "Votre astrologue interprète votre thème..."
  personaSelectorTitle: string  // "Choisissez votre astrologue"
  personaSelectorConfirm: string  // "Demander l'interprétation complète"
  sectionsMap: Record<string, string>  // "overall" → "Vue d'ensemble", etc.
}
```

**Mapping des section keys :**
```typescript
sectionsMap: {
  overall: "Vue d'ensemble",
  career: "Carrière et vocation",
  relationships: "Relations et amour",
  inner_life: "Vie intérieure",
  daily_life: "Vie quotidienne",
  strengths: "Forces",
  challenges: "Défis",
  tarot_spread: "Tirage",
  event_context: "Contexte événementiel",
}
```

---

## Tâches Techniques

### T1 — API client : hook `useNatalInterpretation`

**Fichier :** `frontend/src/api/natalChart.ts`

Ajouter après les hooks existants :
```typescript
async function fetchNatalInterpretation(
  accessToken: string,
  useCaseLevel: "short" | "complete",
  personaId?: string | null,
  locale?: string,
): Promise<NatalInterpretationResult>

export function useNatalInterpretation(options: {
  enabled: boolean
  useCaseLevel: "short" | "complete"
  personaId?: string | null
  locale?: string
}): UseQueryResult<NatalInterpretationResult, ApiError>
```

### T2 — Composants d'affichage

**Fichier :** `frontend/src/components/NatalInterpretation.tsx`

Composants à créer (dans un seul fichier ou dans `components/natal/`) :

```tsx
// Section principale (orchestration)
export function NatalInterpretationSection({ chartLoaded, lang }: {...})

// Sous-composants
function InterpretationSkeleton()
function InterpretationContent({ data, lang }: { data: NatalInterpretationResult, lang: AstrologyLang })
function HighlightsChips({ highlights }: { highlights: string[] })
function SectionAccordion({ sections, sectionsMap }: { sections: AstroSection[], sectionsMap: Record<string, string> })
function AdviceList({ advice }: { advice: string[] })
function EvidenceTags({ evidence }: { evidence: string[] })
function UpsellBlock({ onSelectPersona, lang }: {...})
function PersonaSelector({ onConfirm, lang }: {...})
function InterpretationError({ onRetry, lang }: {...})
```

### T3 — Intégration dans `NatalChartPage.tsx`

Ajouter à la fin du rendu principal (après `<NatalChartGuide>`) :

```tsx
<NatalInterpretationSection
  chartLoaded={Boolean(chart)}
  lang={lang}
/>
```

La section gère elle-même son state interne (niveau, personaId, loading).

### T4 — Traductions

**Fichier :** `frontend/src/i18n/natalChart.ts`

Ajouter le sous-objet `interpretation` dans `NatalChartTranslations` (type + valeurs fr/en/es).

### T5 — Tests

**Fichier :** `frontend/src/tests/natalInterpretation.test.ts`

```typescript
describe("useNatalInterpretation", () => {
  it("fetches short interpretation when enabled", ...)
  it("does not fetch when disabled", ...)
  it("uses correct queryKey for caching", ...)
})

describe("NatalInterpretationSection", () => {
  it("shows skeleton while loading", ...)
  it("shows interpretation content when loaded", ...)
  it("shows error state when API fails", ...)
  it("shows upsell CTA after short interpretation", ...)
})
```

---

## Maquette textuelle (rendu attendu)

```
┌─────────────────────────────────────────────────────────┐
│  Thème natal                                              │
│  [données brutes : planètes, maisons, aspects]            │
│  [Guide]                                                  │
├─────────────────────────────────────────────────────────┤
│  INTERPRÉTATION DE VOTRE THÈME NATAL                      │
│  ─────────────────────────────────────────────────────   │
│  Titre de l'interprétation                               │
│  Résumé introductif du profil natal...                   │
│                                                           │
│  POINTS CLÉS                                             │
│  [Chip 1] [Chip 2] [Chip 3] [Chip 4] [Chip 5]           │
│                                                           │
│  ▼ Vue d'ensemble                                         │
│    Contenu de la section overall...                      │
│  ▶ Carrière et vocation                                  │
│  ▶ Relations et amour                                    │
│  ▶ Vie intérieure                                        │
│  ▶ Vie quotidienne                                        │
│                                                           │
│  CONSEILS                                                 │
│  1. Conseil 1...                                         │
│  2. Conseil 2...                                         │
│  3. Conseil 3...                                         │
│                                                           │
│  Note : L'astrologie est une piste de réflexion...       │
│  Sources : [SUN_TAURUS] [MOON_H8] [ASC_SCORPIO]         │
│                                                           │
│  ╔═══════════════════════════════════════════════════╗   │
│  ║  Débloquez l'interprétation complète              ║   │
│  ║  Choisissez votre astrologue pour une analyse     ║   │
│  ║  approfondie et personnalisée.                    ║   │
│  ║  [Choisir mon astrologue]                         ║   │
│  ╚═══════════════════════════════════════════════════╝   │
└─────────────────────────────────────────────────────────┘
```

---

## Fichiers à Créer / Modifier

| Action | Fichier |
|--------|---------|
| MODIFIER | `frontend/src/api/natalChart.ts` — ajouter types + hook |
| CRÉER | `frontend/src/components/NatalInterpretation.tsx` |
| MODIFIER | `frontend/src/i18n/natalChart.ts` — ajouter clés `interpretation` |
| MODIFIER | `frontend/src/pages/NatalChartPage.tsx` — intégrer `NatalInterpretationSection` |
| CRÉER | `frontend/src/tests/natalInterpretation.test.ts` |

---

## Critères de "Done"

- [ ] L'interprétation SIMPLE se charge automatiquement après le chart (appel API)
- [ ] Skeleton visible pendant le chargement
- [ ] Contenu AstroResponse_v1 affiché correctement (titre, summary, sections, highlights, advice)
- [ ] CTA upsell visible sous l'interprétation SIMPLE
- [ ] PersonaSelector fonctionnel : sélection → appel API avec `complete` + `persona_id`
- [ ] Erreur d'interprétation n'affecte pas les données brutes du chart
- [ ] Tests frontend passent (`npm test` ou `vitest`)
- [ ] Traductions fr + en complètes
