# Story 20.13: UI natal — aspects avancés (orb/orb_used) et rétrograde

Status: done

## Story

As a utilisateur de la page natal,
I want voir les aspects avec leur orb effective (`orb_used`) et les rétrogrades,
so that je peux interpréter les écarts d'aspects et la dynamique planétaire plus finement.

## Acceptance Criteria

1. **Given** un thème avec aspects **When** la page `/natal` est affichée **Then** chaque aspect affiche code, planètes, `orb` et `orb_used`.
2. **Given** un thème sans aspects **When** la page est affichée **Then** un état vide explicite est rendu sans erreur runtime.
3. **Given** une planète rétrograde (`is_retrograde=true`) **When** la page est affichée **Then** le symbole `℞` reste visible (non-régression).
4. **Given** un payload legacy sans `orb_used` **When** la page est affichée **Then** le rendu reste stable (fallback discret).

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 4) Étendre le contrat frontend natal pour aspects enrichis
  - [x] Ajouter `orb_used?: number` au type d'aspect
  - [x] Prévoir fallback de rendu si champ absent
- [x] Task 2 (AC: 1-3) Mettre à jour le rendu `NatalChartPage`
  - [x] Afficher `orb` + `orb_used`
  - [x] Préserver indicateur `℞`
  - [x] État vide explicite quand aucun aspect
- [x] Task 3 (AC: 1-4) Renforcer les tests frontend
  - [x] Test rendu aspect enrichi
  - [x] Test état vide aspects
  - [x] Test non-régression rétrograde
  - [x] Test payload legacy sans `orb_used`

## Dev Notes

- Story alignée avec 20.8: conserver UI minimale et robuste.
- Ne pas recalculer d'aspects côté frontend; seulement afficher les données backend.
- Garder i18n actuelle pour labels de sections.

### Project Structure Notes

- Frontend uniquement.
- Impacts: `frontend/src/api/natalChart.ts`, `frontend/src/pages/NatalChartPage.tsx`, tests associés.

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-2013--ui-natal-affichage-avancé-des-aspectsretrograde]
- [Source: _bmad-output/implementation-artifacts/20-8-ui-impact-retrograde-house-system.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `npm run test -- NatalChartPage.test.tsx` (red: 2 nouveaux tests KO avant implémentation du rendu)
- `npm run test -- NatalChartPage.test.tsx` (green: 45/45 OK après implémentation)
- `npm run lint` (OK — tsc --noEmit sans erreur)
- `npm run test` (suite complète 1083/1083 OK — aucune régression)

### Completion Notes List

- `AspectResult` étendu avec `orb_used?: number` (champ optionnel, fallback silencieux si absent).
- `NatalChartTranslations` augmenté de la clé `orbUsed` (fr: "orbe eff.", en: "orb used", es: "orbe efect.").
- Rendu aspect mis à jour : affiche `, orbe eff. X.XX°` conditionnel si `orb_used !== undefined`.
- Indicateur `℞` préservé (non-régression story 20-8).
- État vide aspects déjà présent (`t.noAspects`) confirmé par test dédié.
- 4 nouveaux tests dans `describe("Story 20-13")` : AC 1 (orb+orb_used), AC 2 (vide), AC 3 (retrograde), AC 4 (legacy sans orb_used).

### File List

- `_bmad-output/implementation-artifacts/20-13-ui-aspects-orb-used-retrograde.md`
- `frontend/src/api/natalChart.ts`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

## Change Log

- 2026-02-27: Affichage `orb_used` dans les aspects natal, clé i18n `orbUsed` (3 langues), 4 nouveaux tests, lint et suite complète OK.
- 2026-02-27: Correctif post-review - contrat frontend assoupli sur `orb_used?: number | null` pour refléter les payloads API défensifs déjà supportés au rendu.
