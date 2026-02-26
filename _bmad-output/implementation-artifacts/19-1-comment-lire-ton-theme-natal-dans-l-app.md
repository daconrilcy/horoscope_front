# Story 19.1: Comment lire ton thème natal dans l'app

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur qui consulte son thème natal,
I want une section claire "Comment lire ton thème natal dans l'app" avec des conventions explicites et des exemples,
so that je comprenne ce que j'observe et pourquoi chaque planète est placée dans un signe et une maison.

## Acceptance Criteria

1. **Given** la page thème natal est affichée **When** l'utilisateur ouvre la section pédagogique **Then** les trois briques sont décrites clairement: signes, maisons, planètes.
2. **Given** une longitude planétaire est disponible **When** l'exemple de conversion est affiché **Then** l'app montre la forme `Soleil 34.08° -> Taureau 4°05'` et précise que Taureau commence à 30°.
3. **Given** les maisons sont affichées **When** l'utilisateur lit les conventions **Then** la règle d'intervalle semi-ouvert `[debut, fin)` est explicitée, avec la conséquence "si planète == cuspide de fin, alors maison suivante".
4. **Given** une maison traverse 360° **When** l'intervalle est rendu **Then** l'app explique le wrap (`348.46° -> 360° puis 0° -> 18.46°`) avec un exemple lisible.
5. **Given** le profil natal n'a pas d'heure de naissance **When** la section Ascendant est affichée **Then** l'app indique explicitement que l'ascendant n'est pas calculé.
6. **Given** la section métadonnées en haut de page **When** les infos de calcul sont rendues **Then** l'app affiche date/heure de génération, version de référentiel, version de ruleset, et système de maisons.
7. **Given** la liste des planètes et la roue des maisons **When** les données sont affichées **Then** la représentation est cohérente entre les deux vues (même longitude, même maison, même conventions).

## Tasks / Subtasks

- [x] Task 1 — Concevoir le bloc pédagogique "Comment lire ton thème natal" (AC: 1, 2, 3, 4, 5)
  - [x] Structurer le contenu en sections: Signes, Maisons, Planètes, Signe solaire & Ascendant.
  - [x] Ajouter les exemples numériques demandés avec formatage homogène (`°`, `'`, longitudes).
  - [x] Ajouter un encart explicite sur la convention `[debut, fin)`.

- [x] Task 2 — Intégrer le bloc dans la page thème natal (AC: 1, 5, 6)
  - [x] Identifier le composant/page cible de rendu principal du thème natal.
  - [x] Afficher le mode dégradé "heure de naissance manquante" sans ambiguïté.
  - [x] Vérifier l'accessibilité (titres, ordre de lecture, contraste, responsive).

- [x] Task 3 — Aligner la cohérence données UI (AC: 2, 4, 7)
  - [x] Vérifier que les valeurs affichées dans la liste des planètes et la roue des maisons utilisent les mêmes champs source.
  - [x] Afficher l'intervalle de maison de chaque planète pour expliquer l'appartenance.
  - [x] Vérifier les cas limites de cuspides et de wrap 360->0.

- [x] Task 4 — Métadonnées de traçabilité (AC: 6)
  - [x] Afficher en haut de page: date/heure génération, `reference_version`, `ruleset_version`, `house_system`.
  - [x] Garantir des labels stables et explicites côté UI.

- [x] Task 5 — Tests front et non-régression (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] Ajouter tests unitaires/composants sur le bloc pédagogique.
  - [x] Ajouter tests sur le mode sans heure de naissance.
  - [x] Ajouter test de cohérence des valeurs entre liste planètes et roue.

## Dev Notes

### Contraintes techniques

- Réutiliser les contrats API existants exposant `metadata.reference_version`, `metadata.ruleset_version`, `metadata.house_system`.
- Ne pas dupliquer de logique de conversion longitude->signe entre composants; centraliser dans les utilitaires existants ou dans un helper dédié.
- Conserver la convention actuelle d'intervalle maison `[debut, fin)` et la documenter textuellement dans l'UI.

### Project Structure Notes

- Front principal attendu:
  - `frontend/src/pages/NatalChartPage.tsx`
  - `frontend/src/components/` (nouveau composant pédagogique si nécessaire)
  - `frontend/src/utils/` (helper de formatage si extraction nécessaire)
  - `frontend/src/tests/` (tests Vitest + Testing Library)
- Backend: aucune nouvelle route attendue pour cette story sauf correction mineure si un champ metadata manque.

### References

- [Source: _bmad-output/planning-artifacts/epic-19-comment-lire-theme-natal-dans-l-app.md]
- [Source: _bmad-output/planning-artifacts/epic-18-astro-profile.md]
- [Source: _bmad-output/implementation-artifacts/18-3-astro-profile-ui-hero-profile-natal-svg-css.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Story créée manuellement selon le template BMAD `create-story`.
- AC convertis en format BDD à partir du contenu métier fourni.
- Régressions de test liées au guide pédagogique corrigées: `getByRole("heading", { name: /Planètes/i })` et `getByText(/Gémeaux/)` retournaient plusieurs éléments car les mêmes termes apparaissent dans le guide. Fixes: exact string matching pour les headings, `getAllByText` pour les termes ambigus.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- **NatalChartGuide** (`frontend/src/components/NatalChartGuide.tsx`): nouveau composant `<details>/<summary>` avec 4 sections pédagogiques (Signes, Planètes, Maisons, Ascendant) et traductions fr/en/es complètes.
- **Wrap 360→0**: `getHouseIntervalLabel` dans `NatalChartPage` enrichi pour afficher explicitement `348.46° -> 360° puis 0° -> 18.46°` quand une maison traverse 0°.
- **Métadonnées** (AC 6): déjà implémentées en story 18-3 (`generated_at`, `reference_version`, `ruleset_version`, `house_system`).
- **10 nouveaux tests** AC-19-1 ajoutés: guide pédagogique (7 tests), wrap interval (2 tests), non-régression (1 test).
- Suite complète: **1070/1070 tests verts**.

### File List

- `frontend/src/components/NatalChartGuide.tsx` (new)
- `frontend/src/pages/NatalChartPage.tsx` (modified)
- `frontend/src/i18n/natalChart.ts` (modified)
- `frontend/src/tests/NatalChartPage.test.tsx` (modified)
- `_bmad-output/implementation-artifacts/19-1-comment-lire-ton-theme-natal-dans-l-app.md` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

## Change Log

- 2026-02-26: Implémentation complète story 19-1 — NatalChartGuide, wrap 360->0, traductions i18n, 10 nouveaux tests, 1070/1070 verts.
