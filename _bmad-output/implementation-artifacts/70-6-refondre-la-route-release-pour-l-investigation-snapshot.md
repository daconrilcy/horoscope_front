# Story 70.6: Refondre la route release pour l investigation snapshot

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want une route release dediee pour la timeline et les diffs de snapshots,
so that je puisse comprendre l historique de release sans naviguer dans le catalogue principal.

## Acceptance Criteria

1. Etant donne que l admin ouvre la route `release`, quand la page charge, alors la timeline snapshots est affichee dans une interface autonome orientee investigation, et les preuves, statuts et changements sont hierarchises visuellement.
2. Etant donne que l admin compare deux snapshots, quand il ouvre le diff, alors les changements assembly, execution profile et output contract sont lisibles sans ambiguite, et les metadonnees de comparaison restent visibles sans lire toute la table ligne a ligne.
3. Etant donne qu un bouton de navigation vers une cible canonique est affiche, quand l admin l active, alors il ouvre le detail catalogue approprie, et aucun libelle parasite ou numerique ambigu de type `Ouvrir 66.46` n apparait.
4. Etant donne les flux release deja presents, quand la refonte est livree, alors les hooks `useReleaseSnapshotsTimeline` et `useReleaseSnapshotDiff` restent reemployes, et aucune regression n est introduite sur la selection de snapshots ou la navigation vers le catalogue.
5. Etant donne la couverture admin prompts existante, quand la story est livree, alors les tests Vitest valident le chargement de la route release, la lecture de la timeline, le diff snapshots et la navigation contextuelle vers le catalogue sans casser les stories 70.1 a 70.5.

## Tasks / Subtasks

- [x] Recomposer la route `release` comme surface d investigation dediee (AC: 1, 2)
  - [x] Clarifier l en-tete de page et le modele d interaction de la timeline snapshots
  - [x] Mieux hierarchiser statut courant, historique, raison, rollback et preuves corrélées
  - [x] Eviter une simple accumulation de cartes techniques sans structure d investigation
- [x] Rendre le diff snapshots plus lisible et plus actionnable (AC: 2, 4)
  - [x] Conserver `useReleaseSnapshotDiff` et la selection `fromSnapshotId` / `toSnapshotId`
  - [x] Donner plus de contexte autour de la comparaison source/cible avant la table
  - [x] Rendre les colonnes `assembly`, `execution profile`, `output contract` plus lisibles qu un simple `changed/stable`
- [x] Corriger la navigation contextuelle vers le catalogue (AC: 3, 4)
  - [x] Remplacer le libelle actuel `Ouvrir 66.46` par un libelle francais contextuel explicite
  - [x] Preserver la navigation vers `/admin/prompts/catalog` avec `setSelectedManifestEntryId`
  - [x] Rendre explicite a quelle cible canonique l action renvoie
- [x] Verrouiller les non-regressions de route et de tests (AC: 4, 5)
  - [x] Conserver la route dediee `/admin/prompts/release` livree en `70.1`
  - [x] Preserver le chargement de la timeline et du diff snapshots avec les hooks existants
  - [x] Etendre les tests Vitest existants plutot que creer une seconde strategie de verification

## Dev Notes

- La route `release` existe deja dans `AdminPromptsPage.tsx` avec:
  - une timeline de snapshots,
  - deux selecteurs source/cible,
  - un diff de snapshots en table,
  - une action de navigation vers le catalogue.
  L enjeu de `70.6` est ergonomique et sémantique, pas fonctionnel backend. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Le principal problème déjà visible dans le code est le libellé parasite `Ouvrir 66.46` dans le diff release; il doit être éliminé explicitement par cette story. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Les tests Vitest couvrent déjà le parcours minimal release: ouverture de la route, affichage de la timeline, preuves, et chargement du diff. Il faut étendre cette base pour couvrir le wording et la navigation contextuelle. [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx]
- `70.1` a déjà isolé `release` en route dédiée, `70.5` a relevé le niveau de qualité de `legacy`; `70.6` doit amener `release` au même standard d investigation lisible. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md]

### Technical Requirements

- Ne pas changer le contrat backend des snapshots release ni les endpoints déjà consommés par `useReleaseSnapshotsTimeline` et `useReleaseSnapshotDiff`.
- Conserver le mécanisme de sélection `fromSnapshotId` / `toSnapshotId` déjà piloté par l’état local et les effets existants.
- Ne pas casser la navigation vers le catalogue déjà branchée via `navigate(`${ADMIN_PROMPTS_BASE}/catalog`)` et `setSelectedManifestEntryId(entry.manifest_entry_id)`.
- Si la surface release grossit trop dans `AdminPromptsPage.tsx`, préférer une extraction locale sous `frontend/src/pages/admin/`.
- Cette story reste en lecture/investigation; aucun rollback release ou mutation backend supplémentaire ne doit être inventé ici.

### Architecture Compliance

- Respecter l architecture frontend React/TypeScript du monorepo et la séparation hooks/UI déjà en place. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Respecter `AGENTS.md`: aucun style inline, réutilisation des tokens et classes CSS existants avant création de nouveaux styles, petit delta cohérent, tests mis à jour. [Source: C:/dev/horoscope_front/AGENTS.md]
- Les états `loading`, `error`, `empty` doivent rester explicites sur la route release. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Library / Framework Requirements

- Aucune nouvelle bibliothèque n est requise par défaut pour cette story.
- Réutiliser les briques existantes du projet:
  - `react-router-dom` pour la route dédiée et la navigation vers le catalogue
  - `@tanstack/react-query` pour la lecture des snapshots et du diff
  - les composants/tableaux déjà présents dans `AdminPromptsPage.tsx`
- N introduire un composant tiers de timeline ou de diff que si la lisibilité ciblée ne peut pas être obtenue par une refonte raisonnable du JSX/CSS existant.

### File Structure Requirements

- Fichiers très probablement touchés:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
- Fichiers potentiellement à créer si extraction utile:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsReleaseRoute.tsx`
  - ou sous-composants locaux pour la timeline, les preuves ou le diff
- Garder la logique release dans le domaine `frontend/src/pages/admin/`.

### Testing Requirements

- Étendre les tests Vitest pour vérifier au minimum:
  - l affichage de la route release comme surface dédiée
  - la lecture de la timeline snapshots et des badges de preuve
  - la présence du diff snapshots avec contexte source/cible
  - la disparition du libellé `Ouvrir 66.46` au profit d un libellé contextuel
  - la navigation contextuelle vers le catalogue ou au minimum l intention de navigation correcte
- Préserver le test existant `affiche l'historique release snapshot et le diff` et l enrichir si le DOM change.

### Previous Story Intelligence

- `70.4` a déjà amélioré fortement le détail catalogue; cette story n a pas à réembarquer le graphe logique ou l inspection resolved.
- `70.5` a montré le bénéfice d une vraie hiérarchie d investigation, de métadonnées visibles et de wording produit cohérent. Les mêmes principes doivent être appliqués à `release`.
- La route release est déjà couverte par la sous-navigation dédiée de `70.1`; pas de changement attendu sur le routing primaire.

### Implementation Guardrails

- Ne pas mélanger davantage `release` avec `catalog`, `legacy` ou `consumption`.
- Le flux opérateur doit être clair:
  - lire la timeline,
  - comprendre l état courant d un snapshot,
  - comparer deux snapshots,
  - ouvrir une cible canonique concernée dans le catalogue.
- Les statuts et preuves doivent être visibles sans noyer l opérateur dans la table de diff.
- Le wording FR doit être cohérent sur toute la route; les termes techniques peuvent rester sur les colonnes critiques mais pas les libellés parasites ou internes.
- La table de diff ne doit pas rester une simple matrice `changed/stable` sans contexte si un meilleur résumé peut être apporté sans changer le backend.

### UX Requirements

- L opérateur doit pouvoir répondre rapidement à trois questions:
  - quel snapshot est actuellement en jeu
  - quels changements sont survenus entre deux snapshots
  - quelle entrée canonique ouvrir pour poursuivre l investigation
- La route doit avoir un modèle d interaction propre à l investigation release, distinct du catalogue et du legacy.
- Les preuves corrélées doivent aider à qualifier le snapshot, pas seulement être listées comme badges décoratifs. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]

### Project Structure Notes

- Aucun `project-context.md` n a été détecté dans le workspace.
- Story strictement frontend sur la route `release`.

### References

- Epic 70 et story 70.6: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.1: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]
- Intelligence 70.5: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Implementation release actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Tests release existants: [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx]
- Architecture frontend: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- UX responsive/accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `98f4d761 fix(admin-prompts): story 70.5 — legacy sans actif inventé, i18n complète, tests`
  - `38fd5410 feat(admin-prompts): story 70.5 route legacy, artefact et sprint`
  - `1f245624 test(admin): cover logic graph error boundary remount`
  - `04f91ce0 docs(70-4): précise SHAs correctif + doc`
  - `be4ae6ad docs(70-4): SHA commit correctif dans change log`
- Etat courant release constate dans `AdminPromptsPage.tsx`:
  - timeline snapshots
  - preuves sous forme de badges
  - selecteurs source/cible
  - diff snapshots en table
  - bouton de navigation catalogue avec libellé `Ouvrir 66.46`

### Completion Notes List

- Story créée après analyse de la route `release` actuelle, de la couverture Vitest existante et des refontes déjà livrées sur `70.1` à `70.5`.
- La story verrouille la refonte UX/UI de la route `release` sans changement de contrat backend, avec correction explicite du wording de navigation parasite.

### Completion Notes (implémentation)

- Surface release restructurée : en-tête type investigation (kicker, titre, intro), sections « Chronologie des événements » et « Comparer deux snapshots », cartes timeline avec libellés FR (événement, état courant, rollback, motif, preuves qualité).
- Diff : bandeau source/cible avec versions et identifiants courts, tableau avec badges Modifié/Inchangé par axe, portée du changement mappée en français (`releaseDiffCategoryLabel`), bouton catalogue avec libellé explicite + indice **tous segments** du manifest (`feature · subfeature · plan · locale`, etc.) et `aria-label` canonique (suppression du placeholder `Ouvrir 66.46`).
- Hooks `useReleaseSnapshotsTimeline` et `useReleaseSnapshotDiff` inchangés ; navigation `navigate` + `setSelectedManifestEntryId` conservée.
- Tests Vitest : scénario release enrichi dans `AdminPromptsPage.test.tsx` (région ARIA, titres, synthèse, absence `Ouvrir 66.46`, hint complet, mock `useNavigate` pour l’URL catalogue). **Intégration route** dédiée dans `AdminPromptsPage.releaseCatalog.integration.test.tsx` : `createTestMemoryRouter` + `RouterProvider`, clic bouton catalogue, assertion `pathname` `/admin/prompts/catalog`, onglet catalogue actif, résumé détail avec l’identifiant manifeste sélectionné (catalogue vide + resolved 404).

### Change Log

- 2026-04-18 : Implémentation story 70.6 — refonte UI/CSS route release, helpers de libellés, extension tests `AdminPromptsPage.test.tsx`.
- 2026-04-18 (suivi) : hint manifeste sur tous les segments ; test d’intégration release→catalogue (`AdminPromptsPage.releaseCatalog.integration.test.tsx`) ; correctifs revue P2.

### File List

- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/tests/AdminPromptsPage.test.tsx
- frontend/src/tests/AdminPromptsPage.releaseCatalog.integration.test.tsx
- _bmad-output/implementation-artifacts/70-6-refondre-la-route-release-pour-l-investigation-snapshot.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Review Findings

- [x] [Review][Patch] Horodatage `last_updated` du sprint régressif (passage 23:59 → 20:15 dans le diff) — aligner sur une valeur cohérente / monotone pour éviter une traçabilité sprint confuse. [_bmad-output/implementation-artifacts/sprint-status.yaml:2] — corrigé : `last_updated` remis à une fin de journée cohérente (2026-04-18T23:59:59+02:00).

- [x] [Review][Patch] `releaseDiffCategoryLabel` : toute valeur `category` absente du map (évolution API) s’affiche telle quelle — risque de libellé anglais ou opaque ; prévoir repli explicite (ex. préfixe « Catégorie : » ou libellé neutre). [frontend/src/pages/admin/AdminPromptsPage.tsx — helpers release] — corrigé : repli `Catégorie (API) : …` / chaîne vide → « Catégorie non renseignée ».

- [x] [Review][Defer] Refonte release encore entièrement dans `AdminPromptsPage.tsx` — les Dev Notes suggèrent une extraction locale (`AdminPromptsReleaseRoute` ou sous-composants) si la surface grossit ; non bloquant pour les AC actuels. [frontend/src/pages/admin/AdminPromptsPage.tsx] — deferred, pre-existing / story optionnelle

- [x] [Review][Defer] Tests release : présence du bouton catalogue et `aria-label` vérifiés, mais pas d’assertion sur `navigate` + sélection d’entrée après clic (couverture comportementale partielle vs intention « navigation contextuelle »). [frontend/src/tests/AdminPromptsPage.test.tsx] — **clos** : mock `navigate` dans le test unitaire + fichier `AdminPromptsPage.releaseCatalog.integration.test.tsx` (router réel, URL catalogue, entrée manifeste dans le résumé détail).
