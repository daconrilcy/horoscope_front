# Story 20.13: UI natal — aspects avancés (orb/orb_used) et rétrograde

Status: ready-for-dev

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

- [ ] Task 1 (AC: 1, 4) Étendre le contrat frontend natal pour aspects enrichis
  - [ ] Ajouter `orb_used?: number` au type d'aspect
  - [ ] Prévoir fallback de rendu si champ absent
- [ ] Task 2 (AC: 1-3) Mettre à jour le rendu `NatalChartPage`
  - [ ] Afficher `orb` + `orb_used`
  - [ ] Préserver indicateur `℞`
  - [ ] État vide explicite quand aucun aspect
- [ ] Task 3 (AC: 1-4) Renforcer les tests frontend
  - [ ] Test rendu aspect enrichi
  - [ ] Test état vide aspects
  - [ ] Test non-régression rétrograde
  - [ ] Test payload legacy sans `orb_used`

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

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List
