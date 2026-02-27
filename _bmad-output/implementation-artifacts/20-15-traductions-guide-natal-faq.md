# Story 20.15: Traductions du guide natal enrichi et de la FAQ

Status: done

## Story

As a utilisateur multilingue,
I want lire le guide "Comment lire ton thème natal" et sa FAQ dans ma langue,
so that je comprends les explications sans ambiguïté en `fr`, `en` ou `es`.

## Acceptance Criteria

1. **Given** la story 20.14 est implémentée **When** la langue active est `fr` **Then** le contenu guide + FAQ correspond au texte canonique français validé.
2. **Given** la langue active est `en` **When** l'utilisateur ouvre le guide/FAQ **Then** toutes les sections et Q/R sont traduites en anglais avec le même sens métier.
3. **Given** la langue active est `es` **When** l'utilisateur ouvre le guide/FAQ **Then** toutes les sections et Q/R sont traduites en espagnol avec le même sens métier.
4. **Given** une clé i18n manquante en `en` ou `es` **When** le guide est rendu **Then** le fallback de traduction s'applique sans crash ni section vide.
5. **Given** les tests frontend i18n sont exécutés **When** les cas `fr/en/es` et fallback sont validés **Then** les assertions passent et couvrent sections + FAQ.

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 2, 3) Traduire toutes les nouvelles clés guide + FAQ
  - [x] Étendre le typage des traductions guide dans `frontend/src/i18n/natalChart.ts`
  - [x] Ajouter les textes `en` et `es` alignés sur le sens FR
  - [x] Vérifier cohérence terminologique astro entre langues
- [x] Task 2 (AC: 4) Sécuriser le fallback i18n
  - [x] Vérifier/renforcer le comportement fallback si clé absente
  - [x] Garantir un rendu robuste (pas de crash, pas de placeholder cassé)
- [x] Task 3 (AC: 5) Ajouter les tests de couverture i18n guide/FAQ
  - [x] Tests de rendu sections + FAQ en `fr`
  - [x] Tests de rendu sections + FAQ en `en`
  - [x] Tests de rendu sections + FAQ en `es`
  - [x] Test explicite de fallback quand une clé manque

### AI Review Follow-ups

- [x] [AI-Review][Medium] Refactor `getGuideTranslations` fallback to use `DEFAULT_ASTRO_LANG` constant.
- [x] [AI-Review][Medium] Export `NatalChartFaqItem` and `DEFAULT_ASTRO_LANG` for better reuse.
- [x] [AI-Review][Low] Use more robust keys (index + question) in `NatalChartGuide` FAQ list.
- [x] [AI-Review][Low] Add integration test in `NatalChartPage.test.tsx` for browser language propagation.
- [x] [AI-Review][Medium] Stage untracked story file to implementation record.

## Dev Notes

- Dépend de la structure guide/FAQ introduite en story 20.14.
- Cibles frontend:
  - `frontend/src/i18n/natalChart.ts`
  - `frontend/src/components/NatalChartGuide.tsx`
  - `frontend/src/tests/NatalChartPage.test.tsx`
- Conserver l'API de traduction existante (`natalChartTranslations`) et éviter toute duplication de dictionnaires.

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-2015--traductions-du-guide-natal-enrichi-et-faq]
- [Source: _bmad-output/implementation-artifacts/20-14-guide-natal-clarification-faq.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Story créée via workflow BMAD `create-story` (ciblée 20.15).
- Implémentée via workflow BMAD `dev-story` (20.15).

### Completion Notes List

- **Task 1 (AC 1/2/3)** : Traductions `fr`/`en`/`es` déjà complètes depuis story 20.14 — 6 sections métier + 8 FAQ dans les 3 langues. Type `NatalChartGuideTranslations` exporté depuis `natalChart.ts`.
- **Task 2 (AC 4)** : Ajout de `getGuideTranslations(lang)` dans `natalChart.ts` (après le dictionnaire pour éviter la référence circulaire). Utilise `natalChartTranslations[lang]?.guide ?? natalChartTranslations.fr.guide` — garantit un fallback FR sans crash si la langue n'est pas dans le dictionnaire. `NatalChartGuide.tsx` utilise désormais `getGuideTranslations(lang)` au lieu de l'accès direct.
- **Task 3 (AC 5)** : 5 nouveaux tests dans `describe("Story 20-15")` : guide EN (6 sections + 8 FAQ EN), guide ES (6 sections + 8 FAQ ES), non-régression FR, fallback runtime (lang="pt"), message ascendant manquant EN+ES. Tests directs sur `NatalChartGuide` (sans passer par `NatalChartPage`) pour isolation maximale.
- Résultat : **1096/1096 tests passent**, zéro régression.

### File List

- `frontend/src/i18n/natalChart.ts`
- `frontend/src/components/NatalChartGuide.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `_bmad-output/implementation-artifacts/20-15-traductions-guide-natal-faq.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-02-27: Implémentation story 20-15 — helper `getGuideTranslations` avec fallback FR, type `NatalChartGuideTranslations` exporté, 5 nouveaux tests i18n EN/ES/FR/fallback. 1096/1096 tests verts.
