# Story 70.7: Refondre la route consumption pour le pilotage operable

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want une route consommation dediee plus claire pour les vues, filtres et drill-down,
so that je puisse analyser les usages LLM sans surcharge cognitive.

## Acceptance Criteria

1. Etant donne que l admin ouvre la route `consumption`, quand la page charge, alors les vues `utilisateur`, `abonnement` et `feature/subfeature` sont presentes dans un ecran autonome, et les filtres temporels, la granularite et l export sont clairement regroupes.
2. Etant donne que la table de consommation est rendue sur mobile ou sur largeur contrainte, quand la surface devient dense, alors elle se replie en composants lisibles sans perdre l acces au drill-down, et les actions `Voir logs recents` restent disponibles.
3. Etant donne qu un drill-down de consommation est ouvert, quand l admin consulte les appels recents, alors les logs correles sont affiches dans une presentation claire et distincte de la table d agregats, et l operateur conserve son contexte de filtre courant.
4. Etant donne les flux consommation deja presents, quand la refonte est livree, alors les hooks `useAdminConsumption`, `useAdminConsumptionDrilldown` et `useDownloadAdminConsumptionCsv` restent reemployes, et aucune regression n est introduite sur les filtres UTC, la pagination ou l export CSV.
5. Etant donne la couverture admin prompts existante, quand la story est livree, alors les tests Vitest valident l affichage de la route consommation, la commutation de vue, le drill-down recent et les filtres temporels sans casser les stories 70.1 a 70.6.

## Tasks / Subtasks

- [x] Recomposer la route `consumption` comme ecran de pilotage autonome (AC: 1, 3)
  - [x] Structurer clairement l en-tete, les filtres, la table d agregats et la zone drill-down
  - [x] Regrouper la vue, la granularite, les bornes temporelles, la recherche et l export dans une toolbar lisible
  - [x] Eviter l impression actuelle d un bloc unique de controles et de tableau
- [x] Ameliorer la lisibilite des aggregats et du drill-down (AC: 1, 3, 4)
  - [x] Conserver `useAdminConsumption` et `useAdminConsumptionDrilldown` comme source de verite
  - [x] Rendre la relation entre ligne d agregat selectionnee et logs correles plus explicite
  - [x] Mieux separer la lecture macro (agrégats) de l investigation micro (logs récents)
- [x] Traiter le responsive et la densite de la surface (AC: 2, 5)
  - [x] Prevoir un repli mobile ou largeur contrainte pour la table dense
  - [x] Preserver l acces a l action `Voir logs récents` dans ce mode replie
  - [x] Eviter de dupliquer la meme information entre table et drill-down
- [x] Verrouiller les non-regressions de filtres, pagination et export (AC: 4, 5)
  - [x] Conserver les conversions UTC via `toUtcIsoFromDateTimeInput`
  - [x] Preserver la pagination serveur et les parametres de requete existants
  - [x] Conserver le comportement d export CSV via `useDownloadAdminConsumptionCsv`

## Dev Notes

- La route `consumption` existe deja dans `AdminPromptsPage.tsx` avec:
  - un select de vue (`user`, `subscription`, `feature`),
  - un select de granularite (`day`, `month`),
  - deux bornes `datetime-local`,
  - une recherche texte,
  - un bouton `Export CSV`,
  - une table d agregats,
  - un drill-down `Voir logs récents`.
  La story `70.7` vise a rendre cet ensemble operable et plus lisible, pas a redefinir le backend. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Les tests Vitest couvrent deja le socle critique:
  - affichage de l onglet consommation,
  - changement de vue,
  - drill-down recent,
  - conversion explicite des dates en UTC.
  La story doit s appuyer sur ces tests plutot que repartir de zero. [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx]
- `70.5` et `70.6` ont releve le niveau de lisibilite des routes `legacy` et `release`; `70.7` doit amener `consumption` au meme standard de surface operable et orientee investigation. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-6-refondre-la-route-release-pour-l-investigation-snapshot.md]

### Technical Requirements

- Ne pas changer le contrat backend des agregats ou du drill-down consommation ni les endpoints deja consommes par `useAdminConsumption`, `useAdminConsumptionDrilldown` et `useDownloadAdminConsumptionCsv`.
- Preserver la conversion UTC des filtres temporels via `toUtcIsoFromDateTimeInput`.
- Conserver la pagination serveur (`page`, `page_size`, `count`) et la logique de reset de pagination lors d un changement de filtre ou de vue.
- Conserver la cle de selection `selectedDrilldownKey` ou un mecanisme equivalent tant que le comportement de drill-down reste stable.
- Si la surface consumption grossit trop dans `AdminPromptsPage.tsx`, preferer une extraction locale sous `frontend/src/pages/admin/`.

### Architecture Compliance

- Respecter l architecture frontend React/TypeScript du monorepo et la separation hooks/UI deja en place. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Respecter `AGENTS.md`: aucun style inline, reutilisation des tokens et classes CSS existants avant creation de nouveaux styles, petit delta coherent, tests mis a jour. [Source: C:/dev/horoscope_front/AGENTS.md]
- Les etats `loading`, `error`, `empty` doivent rester explicites sur la route consommation. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Library / Framework Requirements

- Aucune nouvelle bibliotheque n est requise par defaut pour cette story.
- Reutiliser les briques existantes du projet:
  - `react-router-dom` pour la route dediee
  - `@tanstack/react-query` pour la lecture des agregats, du drill-down et l export
  - les composants/tableaux deja presents dans `AdminPromptsPage.tsx`
- N introduire un composant tiers de data-grid ou de charting que si la lisibilite ciblee ne peut pas etre obtenue par une refonte raisonnable du JSX/CSS existant.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
- Fichiers potentiellement a creer si extraction utile:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsConsumptionRoute.tsx`
  - ou sous-composants locaux pour toolbar, table agregats et drill-down
- Garder la logique consommation dans le domaine `frontend/src/pages/admin/`.

### Testing Requirements

- Etendre les tests Vitest pour verifier au minimum:
  - l affichage de la route consommation comme surface dediee
  - la commutation entre vues `utilisateur`, `abonnement`, `feature/subfeature`
  - le maintien du drill-down et de l action `Voir logs récents`
  - la persistance des filtres temporels et de la pagination
  - le maintien du comportement d export CSV
- Preserver les tests existants sur les bornes UTC et le drill-down recent, et les enrichir si le DOM change.

### Previous Story Intelligence

- `70.1` a deja isole `consumption` en route dediee; aucun changement attendu sur le routing primaire.
- `70.5` et `70.6` ont montre que l effort principal sur les routes secondaires est la hierarchie de lecture, le wording FR coherent et la separation claire entre lecture et actions.
- `70.4` n impacte pas directement cette route, sauf comme precedent de densite UI maitrisée et de couverture de tests admin approfondie.

### Implementation Guardrails

- Ne pas melanger davantage `consumption` avec `catalog`, `legacy` ou `release`.
- Le flux operateur doit etre clair:
  - cadrer la vue et la periode
  - lire les agregats
  - ouvrir un drill-down recent
  - conserver son contexte d investigation
- La table dense ne doit pas rester le seul mode de lecture si la largeur est contrainte.
- Le drill-down doit etre visiblement distinct des agregats, sans donner l impression d un appendice improvisé sous la table.
- Le wording FR doit etre coherent sur toute la route; seuls les identifiants techniques strictement necessaires peuvent rester bruts.

### UX Requirements

- L operateur doit pouvoir repondre rapidement a trois questions:
  - quel axe d analyse je consulte
  - quelle periode et quelle granularite sont actives
  - quels appels recents expliquent une ligne d agregat
- La route doit avoir un modele d interaction propre au pilotage de la consommation, distinct du catalogue, du legacy et de la release.
- Le responsive doit permettre d exploiter la surface sans tableau horizontal illisible ni perte du drill-down. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story strictement frontend sur la route `consumption`.

### References

- Epic 70 et story 70.7: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.1: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]
- Intelligence 70.6: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-6-refondre-la-route-release-pour-l-investigation-snapshot.md]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Implementation consumption actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Tests consumption existants: [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx]
- Architecture frontend: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- UX responsive/accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `b4bea5ff test(admin-prompts): intégration release→catalogue et hint manifeste complet`
  - `cf4b3eef feat(admin-prompts): story 70.6 — route release investigation, revue code`
  - `98f4d761 fix(admin-prompts): story 70.5 — legacy sans actif inventé, i18n complète, tests`
  - `38fd5410 feat(admin-prompts): story 70.5 route legacy, artefact et sprint`
  - `1f245624 test(admin): cover logic graph error boundary remount`
- Etat courant consumption constate dans `AdminPromptsPage.tsx`:
  - toolbar de filtres brute
  - table d agregats dense
  - action `Voir logs récents`
  - drill-down sous la table
  - export CSV et bornes `datetime-local`

### Completion Notes List

- Story creee apres analyse de la route `consumption` actuelle, de la couverture Vitest existante et des refontes deja livrees sur `70.1` a `70.6`.
- La story verrouille une refonte UX/UI de la route `consumption` sans changement de contrat backend ni redefinition des hooks d agregats/drill-down.
- Implementation livree : surface `admin-prompts-consumption` (en-tete, toolbar par groupes, section agrégats, panneau investigation distinct), i18n `adminPromptsConsumption` (FR/EN/ES), bascule table/cartes via `matchMedia` (pas de double DOM), helpers `consumptionRowKey` / `formatConsumptionAxisLabel`, tests Vitest etendus (region, heading agrégats, viewport etroit).
- Post-revue code : hook `useMatchMediaMaxWidth` reloge apres les imports ; export CSV avec `try/catch` et message d erreur ; etat vide agrégats (`emptyAggregates`) + test Vitest dédié.
- Durcissement final : reinitialisation du drill-down (`selectedDrilldownKey`) sur tout changement de périmètre d’agrégats (vue, granularité, période, recherche, pagination) ; `URL.revokeObjectURL` différé après export CSV pour fiabilité navigateur.
- Fermeture du risque résiduel : tests Vitest explicites sur la disparition du drill-down après changement de granularité et sur la révocation différée du blob d export CSV (pas seulement une couverture indirecte).

### File List

- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/i18n/adminPromptsConsumption.ts
- frontend/src/i18n/admin.ts
- frontend/src/tests/AdminPromptsPage.test.tsx
- _bmad-output/implementation-artifacts/70-7-refondre-la-route-consumption-pour-le-pilotage-operable.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-04-18 : refonte route consommation admin (pilotage operable, responsive, tests).
- 2026-04-18 : code review BMAD (étapes 2–3) — constats consignés dans « Review Findings ».
- 2026-04-18 : correctifs post-revue (imports, export CSV, état vide + test Vitest) — story et sprint passés en **done**.
- 2026-04-18 : cloture — reset drill-down sur périmètre agrégats + revoke blob CSV différé ; artefacts et dépôt alignés (**done**).
- 2026-04-18 : couverture complémentaire — tests ciblés sur reset drill-down après changement de granularité et cleanup différé de l export CSV ; risque résiduel fermé.

### Review Findings (AI)

- [x] [Review][Patch] Réorganiser le module : placer `useMatchMediaMaxWidth` après tous les `import` (ou fichier dédié) — fonction insérée entre le premier bloc d’imports et les suivants, fragile pour conventions et outillage. [frontend/src/pages/admin/AdminPromptsPage.tsx:L3-L23] — **Corrigé** (hook après imports).
- [x] [Review][Patch] Export CSV : entourer `exportCsvMutation.mutateAsync` d’un `try/catch` (ou gestion d’erreur TanStack) pour éviter rejet non géré et donner un retour opérateur. [frontend/src/pages/admin/AdminPromptsPage.tsx:L1869-L1883] — **Corrigé** (`try/catch` + `consumptionExportError`, reset sur changement de filtres).
- [x] [Review][Patch] État vide agrégats : quand `consumptionQuery.data` existe mais `data.length === 0`, afficher un message explicite (loading/error déjà là ; Dev Notes / UX exigent empty explicite). [frontend/src/pages/admin/AdminPromptsPage.tsx:L1903+] — **Corrigé** (`emptyAggregates` + classe CSS).
- [x] [Review][Defer] Compatibilité `MediaQueryList.addEventListener` sur navigateurs très anciens [frontend/src/pages/admin/AdminPromptsPage.tsx:L18-L19] — différé, risque faible admin-only (voir `67-To-69-deferred-work.md`).
