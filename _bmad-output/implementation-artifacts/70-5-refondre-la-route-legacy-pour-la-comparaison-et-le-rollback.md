# Story 70.5: Refondre la route legacy pour la comparaison et le rollback

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want une route legacy dediee avec comparaison et rollback plus lisibles,
so that je puisse investiguer l historique legacy sans polluer l experience du catalogue canonique.

## Acceptance Criteria

1. Etant donne que l admin ouvre la route `legacy`, quand la page charge, alors l univers legacy est presente comme un ecran autonome avec son propre contexte de lecture, et le choix du use case ainsi que des versions a comparer est immediatement comprehensible.
2. Etant donne que l admin compare deux versions legacy, quand il ouvre le diff, alors le diff est lisible, clairement annote et dissocie de l inspection canonique, et les informations critiques de version (statut, auteur, date, modele) restent visibles sans lire le texte du prompt en entier.
3. Etant donne qu une action de rollback legacy est disponible, quand l admin la declenche, alors la confirmation explicite reste obligatoire, et le libelle de l action ainsi que ses consequences sont formules en francais produit coherent.
4. Etant donne les flux legacy deja presents, quand la refonte est livree, alors les hooks `useAdminLlmUseCases`, `useAdminPromptHistory` et `useRollbackPromptVersion` restent reemployes, et aucune regression n est introduite sur la comparaison ou le rollback effectif.
5. Etant donne la couverture admin prompts existante, quand la story est livree, alors les tests Vitest valident le chargement de la route legacy, la comparaison de versions et le dialogue de rollback sans casser les stories 70.1 a 70.4.

## Tasks / Subtasks

- [x] Recomposer la route `legacy` comme surface d investigation dediee (AC: 1, 2)
  - [x] Clarifier le cadrage de page avec un header, un sous-texte et une hiérarchie propre a l historique legacy
  - [x] Rendre le choix du use case et des versions comparees plus explicite que le simple select brut actuel
  - [x] Eviter que la route paraisse comme un simple appendice technique de `AdminPromptsPage.tsx`
- [x] Ameliorer la lisibilite du diff legacy (AC: 2, 4)
  - [x] Conserver `buildDiffRows` comme base tant qu aucun moteur de diff plus robuste n est necessaire
  - [x] Mettre en avant les metadonnees de la version comparee et de la version active
  - [x] Distinguer clairement lecture du diff et actions de mutation
- [x] Isoler et expliciter le rollback legacy (AC: 3, 4)
  - [x] Garder `LegacyRollbackModal` et `useRollbackPromptVersion` comme mecanisme nominal de confirmation
  - [x] Remplacer les libelles mixtes ou trop techniques (`Use case legacy`, `Rollback`) par un francais produit coherent
  - [x] Afficher plus explicitement l impact du rollback sur la version active et le use case cible
- [x] Verrouiller les non-regressions de route et de tests (AC: 4, 5)
  - [x] Conserver la route dediee `/admin/prompts/legacy` livree en `70.1`
  - [x] Preserver les invalidations React Query apres rollback et le message de succes
  - [x] Etendre les tests Vitest existants plutot que creer une strategie parallele

## Dev Notes

- La route `legacy` existe deja dans `AdminPromptsPage.tsx`, mais elle reste une surface tres brute: select `Use case legacy`, liste lineaire de versions, bouton `Rollback`, diff texte basique en deux colonnes. Cette story vise a la rendre operable et lisible, sans reintroduire de logique catalogue. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Les hooks utiles sont deja en place:
  - `useAdminLlmUseCases`
  - `useAdminPromptHistory`
  - `useRollbackPromptVersion`
  - ainsi que `buildDiffRows` pour le diff ligne a ligne
  Cette story doit reemployer ces briques avant d envisager toute extraction plus profonde. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- La couverture de tests actuelle valide deja le parcours minimal legacy: ouverture de la route, affichage du diff, ouverture du dialogue de rollback et message de succes. Il faut s appuyer dessus et l etendre. [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx]
- `70.1` a deja sorti `legacy` du catalogue via une route dediee. `70.5` traite maintenant l ergonomie propre de cette route, pas la navigation globale. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]

### Technical Requirements

- Ne pas changer le contrat backend de l historique legacy ni les endpoints deja consommes par `useAdminLlmUseCases`, `useAdminPromptHistory` et `useRollbackPromptVersion`.
- Preserver la confirmation modale avant rollback; aucune action destructive ou mutative ne doit devenir directe.
- Conserver l invalidation React Query deja etablie apres rollback (`admin-llm-prompt-history`, `admin-llm-catalog`).
- Si l ergonomie legacy grossit trop dans `AdminPromptsPage.tsx`, preferer extraire un sous-composant local sous `frontend/src/pages/admin/`.
- Rester dans une logique de lecture/investigation: pas d edition de prompt canonique ici, pas de workflow `draft/published` qui appartient aux stories `70.9` et `70.10`.

### Architecture Compliance

- Respecter l architecture frontend React/TypeScript du monorepo et la separation hooks/UI deja en place. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Respecter `AGENTS.md`: aucun style inline, reutilisation des tokens et classes CSS existants avant d en creer de nouveaux, petit delta coherent, tests mis a jour. [Source: C:/dev/horoscope_front/AGENTS.md]
- Les etats `loading`, `error`, `empty` et `success` doivent rester explicites sur la route legacy. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Library / Framework Requirements

- Aucune nouvelle bibliotheque n est requise par defaut pour cette story.
- Reutiliser les briques existantes du projet:
  - `react-router-dom` pour la route dediee
  - `@tanstack/react-query` pour la lecture/mutation
  - les composants/dialog patterns deja presents dans `AdminPromptsPage.tsx`
- N introduire un moteur de diff externe que si le diff texte actuel ne peut pas satisfaire l AC 2 avec une evolution raisonnable.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
- Fichiers potentiellement a creer si extraction utile:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsLegacyRoute.tsx`
  - ou sous-composants locaux equivalents pour l entete, la liste de versions ou le diff
- Garder la logique legacy dans le domaine `frontend/src/pages/admin/` et ne pas l envoyer dans un dossier generique inutile.

### Testing Requirements

- Etendre les tests Vitest pour verifier au minimum:
  - l affichage de la route legacy comme surface dediee
  - la selection d un use case et d une version de comparaison
  - la presence d un diff lisible et annote
  - l ouverture du dialogue de rollback et la conservation du message de succes
- Preserver le test existant `affiche l'onglet historique legacy avec rollback` et l enrichir si le DOM change.
- Verifier que les libelles utilisateurs principaux sont en francais coherent apres refonte.

### Previous Story Intelligence

- `70.2` et `70.3` ont rendu le catalogue plus pedagogique et mieux structure. `70.5` doit atteindre un niveau de lisibilite comparable sur `legacy`, sans recycler aveuglement le master-detail du catalogue.
- `70.4` a deja termine la refonte du graphe logique cote catalogue; cette story n a pas a embarquer React Flow ni de logique resolved.
- La route legacy est deja couverte par la sous-navigation dediee de `70.1`; pas de changement attendu sur le routing primaire.

### Implementation Guardrails

- Ne pas melanger davantage `legacy` avec les univers `catalog`, `release` ou `consumption`.
- Les libelles actuels `Use case legacy`, `Rollback`, `Comparaison legacy` sont fonctionnels mais encore trop techniques ou pas assez harmonises; l effort principal est de les rendre explicites sans perdre la precision operateur.
- Le diff doit montrer clairement "version comparee" versus "version active" avec leurs metadonnees, avant le contenu ligne a ligne.
- La zone de rollback doit etre nettement separee du flux de lecture pour limiter les erreurs de manipulation.
- Garder la compatibilite avec les donnees actuelles de `AdminPromptVersion` et ne pas inventer de nouveaux champs backend.

### UX Requirements

- L operateur doit pouvoir repondre rapidement a trois questions:
  - quel use case legacy je consulte
  - quelle version est active versus comparee
  - quel sera l effet exact du rollback si je le confirme
- La route doit avoir un modele d interaction adapte a l investigation historique et non a l inspection canonique.
- Les actions sensibles doivent etre visibles mais ne pas dominer la lecture du diff. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story strictement frontend sur la route `legacy`.

### References

- Epic 70 et story 70.5: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.1: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]
- Intelligence 70.4: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-4-rendre-le-schema-visuel-des-processus-llm-avec-react-flow.md]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Implementation legacy actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Tests legacy existants: [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx]
- Architecture frontend: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- UX responsive/accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent sprint context:
  - `70.4` et `70.5` sont marquees `done` dans `sprint-status.yaml` (2026-04-18)
  - Artefact relie dans `planning-artifacts/epics.md` (section Story 70.5)
- Etat courant legacy constate dans `AdminPromptsPage.tsx`:
  - select use case
  - liste de versions
  - diff texte en deux colonnes
  - modale de rollback et invalidation queries

### Completion Notes List

- Story creee apres analyse de la route `legacy` actuelle, de la couverture Vitest existante et de la refonte deja livree sur les stories `70.1` a `70.4`.
- La story verrouille une refonte UX/UI de la route `legacy` sans changement de contrat backend ni detour vers l edition canonique.
- Implementation livree : surface `admin-prompts-legacy` avec en-tete dedie, toolbar « Cas d usage », liste de versions avec badge « En production », actions de restauration uniquement sur les versions non actives, diff avec bandeaux de metadonnees (`LegacyVersionMetaStrip`) avant les lignes, modale de restauration en francais produit avec impact sur la version active, message de succes « Restauration effectuée », i18n FR/EN du titre d en-tete de page legacy mis a jour.
- Correctifs P2 (2026-04-18, revue commit / coherence spec) : pas de version « active » inventee quand `active_prompt_version_id` est absent ou non present dans l historique ; colonne droite du diff en mode « peer » (contraste) dans ce cas ; surface legacy entierement i18n FR/EN/ES via `frontend/src/i18n/adminPromptsLegacy.ts` et `tAdmin.promptsLegacy` ; dates legacy formatees selon `useAstrologyLabels().lang` ; message de succes post-rollback corrige (variable capturee avant fermeture modale) ; test Vitest « sans id actif API » (pas de badge production, titre colonne peer).
- Tests : `npm run test -- src/tests/AdminPromptsPage.test.tsx` OK (19 tests). Le lint `tsc` du frontend echoue encore sur `router.tsx` (futures React Router) — preexistant, hors story.
- Revue code (2026-04-18) : correctifs auto — `LegacyVersionMetaStrip` enveloppe `dl` + kicker hors liste de descriptions ; `promptsPageHeader.legacy` ES aligne sur FR/EN. Vitest AdminPromptsPage + AdminPromptsRouting OK (22 tests).

### File List

- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/i18n/admin.ts
- frontend/src/i18n/adminPromptsLegacy.ts
- frontend/src/tests/AdminPromptsPage.test.tsx
- frontend/src/tests/AdminPromptsRouting.test.tsx
- _bmad-output/implementation-artifacts/70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-04-18 : Refonte UX route legacy (comparaison annotée, restauration explicite, tests Vitest étendus). Statut sprint → review.
- 2026-04-18 : Correctifs revue de code — sémantique `dl`/`LegacyVersionMetaStrip`, i18n ES `promptsPageHeader.legacy`. Statut story → done.
- 2026-04-18 : Correctifs P2 — verite sur la version active API, diff peer sans actif resolu, i18n route legacy complete (FR/EN/ES), locales dates, test sans `active_prompt_version_id`.

### Review Findings

- [x] [Review][Patch] Balise `dl` : le bloc « kicker » (`admin-prompts-legacy__meta-strip-kicker`) est un `div` sans paire `dt`/`dd` à l’intérieur de `<dl>`, ce qui est invalide en HTML et peut dégrader le annonceur d’assistive tech — sortir le kicker au-dessus du `dl` ou regrouper uniquement des groupes `dt`/`dd` conformes. [frontend/src/pages/admin/AdminPromptsPage.tsx — `LegacyVersionMetaStrip`] — corrigé : wrapper `admin-prompts-legacy__meta-strip-wrap`, kicker hors du `dl`.
- [x] [Review][Patch] i18n : `promptsPageHeader.legacy` (titre + intro) a été aligné en FR/EN mais pas en ES — incohérence pour `lang === "es"`. [frontend/src/i18n/admin.ts] — corrigé : titre + intro ES alignés sur FR/EN.
- [x] [Review][Patch] `formatLegacyPromptTimestamp` : harmonisation locale UI (`fr-FR` / `en-GB` / `es-ES`) via `useAstrologyLabels().lang` et module `adminPromptsLegacy.ts` — corrigé (2026-04-18).
