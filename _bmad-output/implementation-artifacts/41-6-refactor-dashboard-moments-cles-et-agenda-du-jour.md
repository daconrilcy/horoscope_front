# Story 41.6: Refactor dashboard intraday en moments clés et agenda du jour

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant `/dashboard`,
I want distinguer clairement les points de bascule réels de la journée et un agenda météo lisible par créneaux,
so that je comprenne rapidement ce qui change, pourquoi cela change, et quelles activités sont les plus propices selon le moment.

## Acceptance Criteria

1. La section actuellement perçue comme redondante entre `Moments clés du jour` et `Moments charnières` est refactorisée en deux blocs clairement distincts:
   - `Moments clés du jour` devient la liste des points de bascule de la journée
   - `Moments charnières` est renommé `Agenda du jour`

2. `Moments clés du jour` n'affiche plus les fenêtres décisionnelles génériques; la section ne présente que les turning points réels de la journée:
   - chaque item est centré sur une heure de bascule réelle issue du backend
   - chaque item affiche un créneau court d'environ 15 à 30 minutes autour de cette bascule
   - chaque item explique en langage utilisateur ce qui change, pourquoi cela change, et quels domaines sont impactés
   - les drivers techniques sont humanisés en événements compréhensibles comme changement de signe, aspect exact ou changement de climat

3. `Agenda du jour` devient une vue “météo du jour” en 12 créneaux fixes de 2 heures:
   - rendu en grille de 4 lignes x 3 colonnes sur desktop
   - rendu responsive cohérent sur mobile
   - chaque créneau indique une à trois activités ou domaines propices via pictogrammes et libellés courts
   - si un turning point tombe dans le créneau, un indicateur visuel dédié le signale

4. Le contenu de `Agenda du jour` est cohérent avec la donnée intraday existante:
   - les pictogrammes/domaines affichés proviennent du signal dominant du créneau
   - l'indicateur de bascule est calculé à partir des `turning_points`
   - aucun créneau ne donne une recommandation contradictoire avec les tops catégories du bloc temporel sous-jacent

5. Le vocabulaire produit est clarifié:
   - le terme `Moments charnières` n'est plus utilisé comme titre de section principale
   - les textes utilisateur évitent l'ambiguïté de `moment de bascule` lorsqu'il s'agit d'une longue fenêtre
   - la sémantique `bascule ponctuelle` vs `créneau de journée` est explicite dans l'UI et les helpers i18n

6. Le refactor reste compatible avec le contrat `/v1/predictions/daily` existant ou l'étend uniquement de manière additive:
   - aucun champ déjà consommé n'est cassé
   - si des champs dérivés sont ajoutés pour simplifier le front, ils restent optionnels et documentés
   - les runs réutilisés (`was_reused=true`) continuent à fournir toutes les données nécessaires au dashboard

7. Les tests frontend et backend couvrent la nouvelle séparation de responsabilités:
   - tests UI sur le renommage, la grille agenda 4x3, les indicateurs de bascule et la non-redondance entre sections
   - tests de mapping ou d'intégration sur la cohérence entre `turning_points`, timeline/blocs et agenda

## Tasks / Subtasks

- [ ] Task 1: Redéfinir le rôle produit des deux sections dashboard (AC: 1, 5)
  - [ ] Remplacer la section actuelle de fenêtres décisionnelles par une section `Moments clés du jour` centrée sur les turning points
  - [ ] Renommer la section `Moments charnières` en `Agenda du jour`
  - [ ] Mettre à jour les libellés i18n FR/EN pour refléter la nouvelle sémantique

- [ ] Task 2: Concevoir le modèle d'affichage des points de bascule (AC: 2, 6)
  - [ ] Déterminer si les `turning_points` actuels suffisent ou si un enrichissement additif du contrat API est requis
  - [ ] Définir une fenêtre courte de rendu autour de chaque turning point (15 ou 30 minutes selon règles explicites)
  - [ ] Produire un message utilisateur composé de: ce qui change, cause principale, impacts métier
  - [ ] Réutiliser les drivers et catégories dominantes existants au lieu d'introduire un second moteur parallèle

- [ ] Task 3: Construire l’`Agenda du jour` en grille météo (AC: 3, 4, 6)
  - [ ] Définir l’algorithme de découpage en 12 créneaux fixes de 2h sur la journée locale
  - [ ] Agréger le signal intraday existant pour chaque créneau sans contradiction avec timeline et blocs
  - [ ] Déterminer le jeu de pictogrammes et la règle d’affichage des activités propices
  - [ ] Ajouter un indicateur de bascule quand au moins un turning point tombe dans le créneau

- [ ] Task 4: Refactoriser les composants React du dashboard (AC: 1, 2, 3, 5)
  - [ ] Adapter ou remplacer `DecisionWindowsSection.tsx`
  - [ ] Adapter `TurningPointsList.tsx` pour le nouveau rendu `Moments clés du jour`
  - [ ] Adapter `DayTimeline.tsx` ou créer un nouveau composant `DayAgenda.tsx` pour la grille 4x3
  - [ ] Réviser l’assemblage de `TodayPage.tsx` pour la nouvelle hiérarchie visuelle

- [ ] Task 5: Durcir la cohérence data-to-UI (AC: 4, 6, 7)
  - [ ] Vérifier que les runs réutilisés exposent encore les données nécessaires au nouvel agenda et aux moments clés
  - [ ] Ajouter les tests backend/unitaires nécessaires si un mapping d’agenda est introduit
  - [ ] Ajouter les tests frontend pour la non-régression du dashboard

## Dev Notes

- Cette story est un refactor produit/UI de l’épic 41, pas une réinvention du moteur intraday.
- La règle principale est de réutiliser la donnée déjà disponible dans `/v1/predictions/daily` autant que possible:
  - `turning_points` pour les bascules réelles
  - `timeline` ou blocs temporels pour l’agenda
  - `decision_windows` uniquement si elles restent utiles comme source secondaire de ton/actionnabilité, pas comme section finale redondante
- Le front ne doit plus présenter deux sections qui racontent la même chose avec des noms différents.
- Le plus petit delta cohérent est préféré:
  - frontend-only si l’agrégation 2h est fiable à partir du contrat existant
  - extension additive backend seulement si nécessaire pour éviter une logique fragile ou dupliquée côté React
- État actuel observé du dashboard:
  - `TodayPage.tsx` affiche aujourd’hui `DecisionWindowsSection`, puis `CategoryGrid`, puis `TurningPointsList`, puis `DayTimeline` dans un `<details>`
  - `DecisionWindowsSection.tsx` montre jusqu’à 6 fenêtres triées par priorité métier puis réordonnées chronologiquement
  - `TurningPointsList.tsx` affiche déjà les pivots réels avec heure, intensité, résumé et drivers humanisés
  - `DayTimeline.tsx` condense les blocs adjacents similaires et marque les pivots, ce qui en fait la meilleure base technique pour dériver un agenda 2h

### Project Structure Notes

- Zone frontend principale:
  - `frontend/src/pages/TodayPage.tsx`
  - `frontend/src/components/prediction/DecisionWindowsSection.tsx`
  - `frontend/src/components/prediction/TurningPointsList.tsx`
  - `frontend/src/components/prediction/DayTimeline.tsx`
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/i18n/predictions.ts`
  - `frontend/src/types/dailyPrediction.ts`
- Zone backend potentiellement concernée si enrichissement additif:
  - `backend/app/api/v1/routers/predictions.py`
  - `backend/app/prediction/decision_window_builder.py`
  - `backend/app/prediction/schemas.py`

### Technical Requirements

- Ne pas casser le contrat de `DailyPredictionResponse`; toute nouvelle structure doit être additive et optionnelle.
- Si une structure `agenda_slots` est ajoutée côté backend, elle doit être:
  - déterministe
  - reconstruisable aussi sur un run réutilisé
  - alignée sur le fuseau `meta.timezone`
- Si l’agenda reste calculé côté frontend:
  - centraliser la logique dans un helper pur et testable
  - ne pas disperser l’agrégation 2h dans plusieurs composants
- Les fenêtres de turning point affichées dans `Moments clés du jour` doivent rester courtes et ponctuelles; ne pas réintroduire des pseudo-fenêtres longues déjà jugées ambiguës.

### Architecture Compliance

- Conserver la séparation actuelle:
  - backend = source de vérité métier intraday
  - frontend = composition UI et agrégations de présentation légères
- Ne pas introduire de logique métier astrologique importante dans les composants React.
- Réutiliser les helpers d’humanisation existants dans `predictionI18n.ts`; éviter les nouveaux dictionnaires parallèles non synchronisés.
- Préserver la compatibilité des runs `was_reused=true`, déjà durcie dans 41.4 et 41.5.

### Library / Framework Requirements

- React + TypeScript existants, sans nouvelle dépendance UI.
- Réutiliser `lucide-react` déjà présent pour les pictogrammes et indicateurs, sauf si le set existant est insuffisant.
- Préserver les patterns de style déjà utilisés sur `TodayPage` et les composants prediction.
- Aucun besoin identifié de recherche web ou d’upgrade de librairie pour cette story; rester sur la stack du repo.

### File Structure Requirements

- Préférer l’adaptation des composants existants avant création de nouveaux composants:
  - `TurningPointsList.tsx` est le meilleur candidat pour `Moments clés du jour`
  - `DayTimeline.tsx` peut soit être refactoré en agenda, soit être laissé comme vue secondaire avec un nouveau `DayAgenda.tsx`
  - `DecisionWindowsSection.tsx` doit être supprimé, remplacé ou redéfini seulement si sa responsabilité finale reste claire et non redondante avec `Moments clés du jour`
- Si un nouveau composant est créé pour l’agenda, le nom attendu est `DayAgenda.tsx` ou équivalent explicite.
- Toute logique de mapping de données vers créneaux 2h doit vivre dans un helper dédié ou dans un composant container testable, pas dans du JSX inline massif.

### Testing Requirements

- Frontend:
  - mettre à jour `frontend/src/tests/TodayPage.test.tsx`
  - ajouter des tests ciblés pour la section `Moments clés du jour`
  - ajouter des tests ciblés pour la grille `Agenda du jour` et l’indicateur de bascule
- Backend si mapping additif:
  - tests unitaires sur la génération des créneaux 2h
  - tests d’intégration sur la cohérence avec `turning_points` et la reconstruction sur run réutilisé
- Conserver les garde-fous Epic 41 déjà présents sur bruit, cohérence timeline et non-régression cache/réutilisation.

### Previous Story Intelligence

- 41.4 a déjà montré que le dashboard souffrait d’un problème de lisibilité sémantique: la nouvelle story doit éviter tout retour à des labels ambigus ou à des sections concurrentes. [Source: _bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md]
- 41.5 a verrouillé la qualité intraday avec un budget de bruit; le refactor dashboard ne doit pas réintroduire plus de bruit visuel ou de répétition que ce budget ne l’autorise. [Source: _bmad-output/implementation-artifacts/41-5-qa-actionability-et-budget-de-bruit-intraday.md]
- Les post-validations du 2026-03-10 ont déjà établi que:
  - les transitions `pivot` neutres doivent rester courtes
  - la timeline et les turning points doivent rester cohérents
  - les messages de calibration doivent venir de la donnée backend quand disponibles
  Ces décisions doivent être conservées dans le refactor. [Source: _bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md]

### Git Intelligence Summary

- `45b1e34 feat(ui): decision-oriented intraday dashboard` a introduit la hiérarchie orientée décision côté `TodayPage`; la story 41.6 doit refactorer cette hiérarchie, pas repartir d’une page vierge.
- `e9e95c2 feat(qa): implement intraday quality gate and noise budget (41-5)` a figé des invariants de lisibilité et de non-bruit qu’il faut préserver.
- `45ef921 Fix reused daily prediction decision windows`, `1a84067 Stabilize local prediction bootstrap and docs` et `9921bdc Stabilize daily prediction dashboard flow` ont ajouté des garanties runtime/backend qu’il ne faut pas contourner côté UI.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md` et des artefacts BMAD existants.

### References

- [Source: user request 2026-03-10 — refactor `/dashboard` avec séparation `Moments clés du jour` / `Agenda du jour`]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-41]
- [Source: _bmad-output/implementation-artifacts/41-3-fenetres-decisionnelles-et-pivots-filtres.md]
- [Source: _bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md]
- [Source: _bmad-output/implementation-artifacts/41-5-qa-actionability-et-budget-de-bruit-intraday.md]
- [Source: frontend/src/pages/TodayPage.tsx]
- [Source: frontend/src/components/prediction/DecisionWindowsSection.tsx]
- [Source: frontend/src/components/prediction/TurningPointsList.tsx]
- [Source: frontend/src/components/prediction/DayTimeline.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story 41.6 absente de `epics.md` et de `sprint-status.yaml` au moment de la création; story fondée sur la demande utilisateur et les artefacts Epic 41 existants.
- Analyse des composants actuels du dashboard réalisée sur `TodayPage.tsx`, `DecisionWindowsSection.tsx` et `DayTimeline.tsx`.

### Completion Notes List

- Story créée en mode ready-for-dev.
- Story volontairement orientée refactor incrémental et réutilisation du contrat daily prediction existant.
- Extension backend laissée additive et conditionnelle, uniquement si l’agrégation agenda 2h s’avère trop fragile côté frontend.

### File List

- `_bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
