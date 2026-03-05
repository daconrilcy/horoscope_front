# Story 29.4: N4 — UI AstroResponse_v1 + upsell

Status: done

## Story

As a utilisateur,
I want voir mon interprétation natale structurée dans l'UI avec une option d'upgrade,
so that je profite d'une lecture claire et je découvre les avantages du mode Premium.

## Acceptance Criteria

1. Un hook `useNatalInterpretation` est ajouté au frontend pour appeler le nouvel endpoint d'interprétation.
2. Une nouvelle section "Interprétation" est ajoutée à la page du thème natal (`NatalChartPage.tsx`).
3. L'interprétation SIMPLE se charge automatiquement après le chargement du thème et s'affiche de manière structurée (titre, résumé, points clés, sections en accordéon, conseils).
4. Un skeleton de chargement est affiché pendant la génération de l'interprétation par l'IA.
5. Un bloc CTA "Upsell" est visible sous l'interprétation SIMPLE, proposant de passer au mode COMPLETE.
6. Un sélecteur de persona (astrologue) permet de choisir l'expert pour l'interprétation COMPLETE.
7. L'interprétation COMPLETE remplace l'interprétation SIMPLE une fois chargée, avec une mention de l'astrologue choisi.
8. Les erreurs d'interprétation sont gérées gracieusement sans impacter l'affichage des données brutes du thème.
9. Les traductions pour tous les nouveaux éléments (signes, maisons, termes d'interprétation) sont disponibles en FR et EN.

## Tasks / Subtasks

- [x] Mettre à jour `frontend/src/api/natalChart.ts`
  - [x] Ajouter les types `AstroInterpretation`, `NatalInterpretationResult`, etc.
  - [x] Implémenter le hook `useNatalInterpretation` avec TanStack Query
- [x] Créer le composant `frontend/src/components/NatalInterpretation.tsx`
  - [x] Implémenter `NatalInterpretationSection` (orchestrateur)
  - [x] Créer les sous-composants : `InterpretationContent`, `HighlightsChips`, `SectionAccordion`, `AdviceList`, `UpsellBlock`, `PersonaSelector`
- [x] Modifier `frontend/src/i18n/natalChart.ts`
  - [x] Ajouter les clés de traduction pour la section `interpretation`
- [x] Intégrer `NatalInterpretationSection` dans `frontend/src/pages/NatalChartPage.tsx`
- [x] Créer les tests frontend dans `frontend/src/tests/natalInterpretation.test.ts`
  - [x] Tester le rendu, le chargement, l'upsell et la gestion des erreurs

## Dev Notes

- L'interprétation est chargée de manière asynchrone pour ne pas bloquer l'affichage du graphique.
- Utiliser les composants UI existants (accordéons, chips, boutons) pour la cohérence visuelle.
- Le mode COMPLETE est simulé via un état local pour cette story (pas de paiement réel).
- Les identifiants de preuves (evidence) sont affichés discrètement pour la traçabilité technique.

### Technical Requirements

- Frontend: React 18 / TypeScript
- State Management: TanStack Query (React Query)
- Styling: Tailwind CSS / CSS Modules existants
- i18n: Système de traduction interne du projet

### File Structure Requirements

- `frontend/src/api/natalChart.ts` (modification)
- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/i18n/natalChart.ts` (modification)
- `frontend/src/pages/NatalChartPage.tsx` (modification)
- `frontend/src/tests/natalInterpretation.test.ts`

### Testing Requirements

- Vitest / React Testing Library.
- Mocking des appels API via MSW ou mocks de hook.

### References

- Epic/Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 29, Story 29.4)
- Context documentation: `docs/agent/story-29-N4-ui-rendu-upsell.md`

## Post-Delivery Fixes

### Correctif UX `/natal` (2026-03-03)
- Problème observé: dans le sélecteur d'astrologue (upgrade interprétation complète), aucune option disponible => bouton principal grisé => parcours bloqué.
- Correctif frontend:
  - remplacement du sélecteur inline par une superposition `modal` (mode card) réutilisant la grille catalogue (`AstrologerGrid`) de la page `/astrologers`
  - sélection d'un astrologue par clic sur sa carte, ce qui lance immédiatement l'interprétation complète avec `persona_id=<id>`
  - conservation d'un état vide explicite si aucun astrologue n'est disponible.
- Correctif auth connexe:
  - nettoyage automatique du token expiré (`token_expired`) côté client,
  - redirection explicite vers `/login` quand le JWT local est expiré (guards),
  - évite les boucles d'appels API 401 silencieuses depuis `/natal`.
- Fichiers:
  - `frontend/src/components/NatalInterpretation.tsx`
  - `frontend/src/api/client.ts`
  - `frontend/src/app/guards/AuthGuard.tsx`
  - `frontend/src/app/guards/RootRedirect.tsx`
  - `frontend/src/utils/authToken.ts`
  - `frontend/src/tests/natalInterpretation.test.tsx`
  - `frontend/src/tests/authToken.test.ts`

### Correctif UX interprétation premium (2026-03-04)
- Problème observé: mélange conceptuel entre "traçabilité evidence" et "mentions légales", plus rendu evidence trop brut (doublons, faible lisibilité).
- Correctif frontend:
  - déplacement des mentions légales dans un footer dédié de l'interprétation (hors panneau audit).
  - transformation du bloc evidence en panneau audit pliable "Ce qui a été utilisé pour écrire cette interprétation".
  - déduplication automatique des éléments evidence, puis regroupement par catégories (angles, planètes personnelles, planètes lentes, maisons dominantes, aspects majeurs, autres).
  - ajout d'une micro-explication de transparence dans le panneau audit.
  - renommage du label Maison VI en "Routines / hygiène de vie" (FR/EN/ES) pour éviter la connotation médicale.
- Fichiers:
  - `frontend/src/components/NatalInterpretation.tsx`
  - `frontend/src/i18n/natalChart.ts`
  - `frontend/src/i18n/astrology.ts`
  - `frontend/src/tests/natalInterpretation.test.tsx`
  - `frontend/src/tests/astrology-i18n.test.ts`
