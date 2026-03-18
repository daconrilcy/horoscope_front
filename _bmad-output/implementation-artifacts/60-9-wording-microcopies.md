# Story 60.9 : Réécrire les microcopies et règles de wording

Status: ready-for-dev

## Story

En tant que membre de l'équipe produit,
je veux définir et appliquer un dictionnaire de libellés cohérents et des guidelines de wording,
afin que la page horoscope parle un langage premium, compréhensible et sans doublons sémantiques.

## Acceptance Criteria

1. Un fichier `backend/app/prediction/public_label_catalog.py` centralise tous les dictionnaires de labels utilisés par les policies backend (climate labels, regime labels, action hints, titles, why templates, etc.).
2. Un fichier `frontend/src/i18n/horoscope_copy.ts` centralise les libellés front utilisés dans les nouveaux composants.
3. Le mot "équilibré" n'apparaît plus que dans un seul bloc maximum sur la page (tolérance : day_climate.summary seulement).
4. Aucun libellé vague sans explication immédiate (interdit : "Une journée équilibrée" seul, "Le relief du moment s'apaise" sans contexte).
5. Tous les niveaux (`level`) ont un libellé public défini dans `horoscope_copy.ts` : très_favorable, favorable, stable, mitigé, exigeant.
6. Tous les régimes (`regime`) ont un libellé et un `action_hint` définis.
7. Tous les `change_type` (emergence, recomposition, attenuation) ont un title de fallback défini.
8. Les labels de domaines publics sont cohérents entre backend (`PUBLIC_DOMAINS`) et front (`horoscope_copy.ts`).
9. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Consolider `public_label_catalog.py` (AC: 1)
  - [ ] T1.1 Centraliser tous les dicts éparpillés dans les policies en Story 60.3–60.7 dans ce fichier
  - [ ] T1.2 Structure cible :
    ```python
    # Climate labels
    CLIMATE_LABELS: dict[tuple[str, str], str]  # (tone, intensity_bucket) → label
    # Regime labels
    REGIME_LABELS: dict[str, list[str]]           # regime → pool labels
    REGIME_ACTION_HINTS: dict[str, str]           # regime → action_hint
    # Turning point titles
    TP_TITLE_TEMPLATES: dict[tuple[str, str], str]  # (change_type, domain) → title
    TP_FALLBACK_TITLES: dict[str, str]           # change_type → title fallback
    TP_DO_AVOID: dict[tuple[str, str], tuple[str, str]]  # (change_type, domain) → (do, avoid)
    # Best window
    WINDOW_WHY_TEMPLATES: dict[str, str]         # domain → why text
    WINDOW_ACTIONS: dict[str, list[str]]         # domain → recommended_actions
    ```
  - [ ] T1.3 S'assurer que tous les fallbacks sont définis (aucun KeyError possible)
  - [ ] T1.4 Vérifier couverture : chaque domaine public a une entrée dans chaque dict

- [ ] T2 — Règles de wording à respecter (AC: 3, 4)
  - [ ] T2.1 Implémenter une vérification statique : `"équilibré"` interdit dans `REGIME_LABELS`, `CLIMATE_LABELS`, `REGIME_ACTION_HINTS`
  - [ ] T2.2 Remplacements obligatoires :
    | Avant | Après |
    |-------|-------|
    | "Une journée équilibrée" | "Climat stable et fluide" |
    | "Nuit équilibrée" | "Phase de repos" ou "Recharge tranquille" |
    | "Matin équilibré" | "Mise en mouvement progressive" |
    | "Après-midi équilibrée" | "Rythme fluide" ou "Progression régulière" |
    | "Le relief du moment s'apaise" | "Retour au calme" |
    | "Bascule — Carrière" | "Virage côté pro" |
    | "Communication" (domaine) | "Relations & échanges" |
    | "Santé & Hygiène de vie" | "Énergie & bien-être" |
    | "Carrière" (domaine) | "Pro & Ambition" |
    | "Travail" (domaine) | "Pro & Ambition" |

- [ ] T3 — Créer `frontend/src/i18n/horoscope_copy.ts` (AC: 2, 5, 6, 7, 8)
  - [ ] T3.1 Définir :
    ```typescript
    export const LEVEL_LABELS: Record<string, { fr: string; en: string; color_hint: string }> = {
      "très_favorable": { fr: "Très favorable", en: "Very Favorable", color_hint: "success" },
      "favorable": { fr: "Favorable", en: "Favorable", color_hint: "success-light" },
      "stable": { fr: "Stable", en: "Stable", color_hint: "neutral" },
      "mitigé": { fr: "Mitigé", en: "Mixed", color_hint: "warning" },
      "exigeant": { fr: "Exigeant", en: "Challenging", color_hint: "danger" },
    }
    export const REGIME_LABELS: Record<string, { fr: string; en: string }> = {
      "progression": { fr: "Progression", en: "Momentum" },
      "fluidité": { fr: "Fluidité", en: "Flow" },
      "prudence": { fr: "Prudence", en: "Caution" },
      "pivot": { fr: "Pivot", en: "Turning Point" },
      "récupération": { fr: "Récupération", en: "Rest" },
      "retombée": { fr: "Retombée", en: "Wind Down" },
      "mise_en_route": { fr: "Mise en route", en: "Warm Up" },
      "recentrage": { fr: "Recentrage", en: "Refocus" },
    }
    export const CHANGE_TYPE_LABELS: Record<string, { fr: string; en: string }> = {
      "emergence": { fr: "Montée", en: "Rising" },
      "recomposition": { fr: "Virage", en: "Shift" },
      "attenuation": { fr: "Retombée", en: "Easing" },
    }
    export const DOMAIN_LABELS: Record<string, { fr: string; en: string; icon: string }> = {
      "pro_ambition": { fr: "Pro & Ambition", en: "Work & Ambition", icon: "💼" },
      "relations_echanges": { fr: "Relations & échanges", en: "Relationships", icon: "🤝" },
      "energie_bienetre": { fr: "Énergie & bien-être", en: "Energy & Wellbeing", icon: "⚡" },
      "argent_ressources": { fr: "Argent & ressources", en: "Money & Resources", icon: "💰" },
      "vie_personnelle": { fr: "Vie personnelle", en: "Personal Life", icon: "🌸" },
    }
    ```
  - [ ] T3.2 Exporter un helper `getDomainLabel(key: string, lang: Lang): string`

- [ ] T4 — Mettre à jour les composants pour utiliser `horoscope_copy.ts` (AC: 8)
  - [ ] T4.1 `DomainRankingCard.tsx` → utiliser `DOMAIN_LABELS[domain.key]`
  - [ ] T4.2 `DomainRankingCard.tsx` → utiliser `LEVEL_LABELS[domain.level]` pour badge
  - [ ] T4.3 `DayTimelineSection.tsx` → utiliser `REGIME_LABELS[window.regime]`
  - [ ] T4.4 `TurningPointCard.tsx` → utiliser `CHANGE_TYPE_LABELS[turningPoint.change_type]`

- [ ] T5 — Tests (AC: 9)
  - [ ] T5.1 Test backend : `"équilibré"` absent de tous les dicts dans `public_label_catalog.py`
  - [ ] T5.2 Test backend : tous les domaines publics ont une entrée dans `WINDOW_WHY_TEMPLATES` et `WINDOW_ACTIONS`
  - [ ] T5.3 Test backend : `TP_FALLBACK_TITLES` couvre tous les change_types
  - [ ] T5.4 Test backend : `REGIME_ACTION_HINTS` couvre tous les régimes

## Dev Notes

### Guidelines de copy

**Principes :**
1. Préférer des verbes d'action à des adjectifs flottants
2. Chaque libellé doit pouvoir tenir en 2–4 mots
3. Tonalité : premium mais accessible (pas de jargon astrologique brut)
4. Cohérence entre sections : si day_climate dit "Élan favorable", la best_window ne peut pas dire "journée difficile"

**Interdits :**
- "équilibré" (sauf day_climate.summary)
- Répétition d'un même texte dans deux sections différentes
- Termes purement techniques sans traduction (ex: "trigone de Jupiter en maison X" sans explication)
- Libellés génériques vides ("Journée normale", "Rien de spécial")

### Fichiers existants à consulter
- `frontend/src/i18n/` — vérifier si des fichiers i18n existent déjà (les compléter plutôt que remplacer)
- `frontend/src/utils/predictionI18n.ts` — labels catégories internes actuels
- `backend/app/prediction/public_domain_taxonomy.py` — labels backend (Story 60.1)

### Project Structure Notes
- Fichier backend central: `backend/app/prediction/public_label_catalog.py` (créé en 60.3-60.7, consolidé ici)
- Nouveau fichier front: `frontend/src/i18n/horoscope_copy.ts`
- Pas de modification des algorithmes

### References
- [Source: frontend/src/utils/predictionI18n.ts] — labels existants
- [Source: frontend/src/i18n/] — structure i18n existante
- [Source: backend/app/prediction/public_domain_taxonomy.py] — labels domaines publics (60.1)
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
