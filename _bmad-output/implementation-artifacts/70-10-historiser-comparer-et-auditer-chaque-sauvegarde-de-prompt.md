# Story 70.10: Historiser, comparer et auditer chaque sauvegarde de prompt

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want que chaque sauvegarde de prompt cree une nouvelle version historisee, comparable et auditée,
so that je puisse suivre les changements, publier explicitement la bonne version et revenir rapidement sur une modification problematique.

## Acceptance Criteria

1. Etant donne qu un prompt canonique est sauvegarde depuis le flux d edition admin, quand la sauvegarde reussit, alors une nouvelle version est creee avec un statut explicite `draft` ou `inactive` non publie, et la version precedente n est jamais ecrasee silencieusement.
2. Etant donne qu une nouvelle version de prompt existe, quand l admin consulte l historique de ce prompt, alors il voit au minimum l identifiant, la date, l auteur, le statut, la date de publication si applicable et un acces au diff avec la version precedente.
3. Etant donne qu une version est publiee explicitement, quand la publication est confirmee, alors cette version passe au statut `published`, l ancienne version `published` passe automatiquement au statut `inactive`, et il n existe jamais plus d une version `published` simultanement pour un meme prompt canonique.
4. Etant donne qu une sauvegarde ou une publication est effectuee, quand l operation est journalisee, alors un audit event persistant est cree avec les metadonnees utiles (acteur, cible, statut, request_id, use_case, version source/cible) et la surface admin confirme visuellement qu une nouvelle version historisee a ete enregistree ou publiee.
5. Etant donne les mecanismes existants de comparaison et de rollback, quand l historique est expose en UI, alors les nouvelles versions restent exploitables par les diff/rollback admin et les tests verifient la coherence du workflow `draft/inactive -> published`, sans regression sur les stories 70.5, 70.6 et 70.9.

## Tasks / Subtasks

- [x] Stabiliser le modele de cycle de vie des versions de prompt (AC: 1, 3, 5)
  - [x] Aligner les statuts backend/frontend des prompts sur la decision produit `draft`, `inactive`, `published`
  - [x] Preserver l invariant de publication unique par `use_case_key`
  - [x] Eviter toute ecriture destructrice de la version precedente lors d une sauvegarde
- [x] Rendre l historique exploitable pour diff, publication et rollback (AC: 2, 3, 5)
  - [x] Exposer ou enrichir la liste des versions avec les metadonnees utiles a la lecture operateur
  - [x] Permettre une comparaison claire avec la version precedente et/ou la version publiee courante
  - [x] Garantir la compatibilite du nouvel historique avec le rollback existant
- [x] Tracer les sauvegardes et publications dans l audit (AC: 4)
  - [x] Journaliser les evenements `create draft`, `publish`, `rollback` et toute transition de statut utile
  - [x] Inclure des details suffisamment precis pour l investigation ops sans fuite de donnees sensibles
  - [x] Reutiliser le systeme d audit existant plutot qu une piste parallele
- [x] Verrouiller les retours UI et la non-regression (AC: 2, 4, 5)
  - [x] Prevoir un feedback explicite apres sauvegarde et apres publication
  - [x] Etendre les tests backend/frontend sur les transitions de statut et l historique
  - [x] Verifier que `legacy`, `release` et le futur flux d edition de `70.9` restent coherents

## Dev Notes

- Le socle backend existe deja pour les prompts admin:
  - `GET /v1/admin/llm/use-cases/{key}/prompts` liste l historique d un use case,
  - `POST /v1/admin/llm/use-cases/{key}/prompts` cree aujourd hui un draft,
  - `PATCH /v1/admin/llm/use-cases/{key}/prompts/{version_id}/publish` publie une version,
  - `POST /v1/admin/llm/use-cases/{key}/rollback` restaure une version.
  `70.10` doit s appuyer sur ces seams reelles et les durcir plutot que redefinir un pipeline parallele. [Source: C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py]
- Le modele de donnees et le frontend sont encore en partie sur `draft | published | archived`, alors que la decision produit validee pour l epic 70 est `draft/inactive -> published`, avec inactivation automatique de l ancienne version publiee. La story doit donc expliciter et traiter cet ecart de semantique, pas le laisser implicite. [Source: C:/dev/horoscope_front/backend/app/infra/db/models/llm_prompt.py, C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts, C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md]
- La base impose deja une unicite de la version `published` par prompt via `ix_llm_prompt_version_active_unique` sur `llm_prompt_versions(use_case_key) WHERE status = 'published'`. Cette contrainte doit etre preservee, y compris apres renomage/metier `archived -> inactive` si la migration est necessaire. [Source: C:/dev/horoscope_front/backend/app/infra/db/models/llm_prompt.py, C:/dev/horoscope_front/backend/horoscope.db]
- Le frontend dispose deja de `useAdminPromptHistory()` et `useRollbackPromptVersion()`, ainsi que d une UI legacy de lecture des versions et rollback dans `AdminPromptsPage.tsx`. `70.10` doit reutiliser cette fondation et la rendre compatible avec les nouveaux statuts et avec le futur flux de sauvegarde de `70.9`. [Source: C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts, C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Le systeme d audit admin existe deja et les endpoints prompts journalisent deja `llm_prompt_create_draft`, `llm_prompt_publish` et `llm_prompt_rollback`. La story doit enrichir et fiabiliser ces traces, pas inventer une seconde piste d audit. [Source: C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py, C:/dev/horoscope_front/backend/app/api/v1/routers/admin_audit.py]

### Technical Requirements

- Conserver les endpoints prompts admin existants comme socle, avec extension ou ajustement minimal si des metadonnees supplementaires sont necessaires.
- Aligner les types frontend/backend et le modele SQLAlchemy sur le workflow valide:
  - sauvegarde => nouvelle version `draft` ou `inactive`
  - publication explicite => nouvelle version `published`
  - ancienne version `published` => `inactive`
- Preserver la contrainte d une seule version `published` par `use_case_key`.
- Garantir que les versions creees restent referenceables par les mecanismes existants de diff, rollback, release snapshots et observabilite (`prompt_version_id`).
- Les evenements d audit doivent inclure au minimum:
  - `use_case_key`
  - `from_version` / `to_version` quand applicable
  - acteur
  - request_id
  - type d action
  - resultat / statut

### Architecture Compliance

- Respecter l architecture monorepo: backend FastAPI/SQLAlchemy/AuditService et frontend React/TypeScript/React Query. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Respecter `AGENTS.md`: petit delta coherent, pas de refactor massif sans necessite, pas de duplication, tests mis a jour, aucun style inline. [Source: C:/dev/horoscope_front/AGENTS.md]
- Preserver les garde-fous runtime et la non-regression 66-69 sur les artefacts prompts canoniques, release snapshots et surfaces admin. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]

### Library / Framework Requirements

- Aucune nouvelle bibliotheque n est requise par defaut.
- Reutiliser:
  - FastAPI + Pydantic pour les contrats API admin prompts
  - SQLAlchemy/Alembic pour l evolution du modele de version
  - `@tanstack/react-query` via `frontend/src/api/adminPrompts.ts`
  - le systeme d audit existant (`AuditService`, `AuditEventCreatePayload`)
- N introduire aucun event store ou systeme de versioning parallele.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py`
  - `C:/dev/horoscope_front/backend/app/infra/db/models/llm_prompt.py`
  - `C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/i18n/adminPromptsCatalog.ts`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
- Fichiers potentiellement touches selon implementation:
  - migration Alembic si le statut `archived` doit etre remappe/metier vers `inactive`
  - services/repository prompts si la logique de transition est deplacee hors router
  - tests backend lies a `admin_llm`

### Testing Requirements

- Backend:
  - test creation d une nouvelle version sans ecrasement de l ancienne
  - test invariant d unicite `published`
  - test transition `published -> inactive` lors d une nouvelle publication
  - test audit event apres creation/publication/rollback
- Frontend:
  - test de lecture de l historique avec statut explicite
  - test de feedback visuel apres sauvegarde/publication
  - test de compatibilite diff/rollback avec les nouveaux statuts
  - test de non-regression des surfaces `legacy` et `release`
- Si une migration de statut est necessaire, couvrir explicitement la compatibilite des anciennes donnees `archived`.

### Previous Story Intelligence

- `70.5` a deja remis au propre la route `legacy` pour la comparaison et le rollback. `70.10` doit s y brancher, pas la contourner.
- `70.6` a rehausse la lecture release snapshot et les preuves de changement. Les versions de prompt historisees doivent rester lisibles dans cette chaine d investigation.
- `70.8` a harmonise les libelles et l accessibilite; tout nouvel affichage de statut/historique doit reutiliser ce vocabulaire et ses conventions.
- `70.9` n est pas encore creee/livree au moment de cette story. `70.10` doit donc preparer un socle backend et UI exploitable par le futur formulaire d edition, sans supposer que le formulaire existe deja.

### Implementation Guardrails

- Ne pas confondre `inactive` avec suppression ou purge: l historique doit rester diffable et roll-backable.
- Ne pas introduire deux nomenclatures de statut visibles en parallele (`archived` cote API et `inactive` cote UI) sans strategie de transition explicite.
- Ne pas casser les versions historiques existantes deja referencees par les snapshots release ou les logs LLM.
- Ne pas enregistrer de details d audit qui exposent des contenus sensibles ou du prompt complet en clair si cela sort du cadre de l audit existant.
- Le flux de sauvegarde doit rester compatible avec l evaluation/golden gate existant avant publication.

### UX Requirements

- L operateur doit pouvoir repondre rapidement a trois questions:
  - quelle version vient d etre creee
  - quelle version est actuellement publiee
  - quelle difference concrete existe entre ces versions
- Le statut de chaque version doit etre visible explicitement et compréhensible sans jargon technique.
- La publication doit rester une action distincte de la sauvegarde, avec consequence lisible sur l ancienne version publiee. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story mixte backend + frontend, centree sur le cycle de vie des versions de prompt.

### References

- Epic 70 et story 70.10: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.5: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md]
- Intelligence 70.8: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-8-harmoniser-les-libelles-l-accessibilite-et-le-responsive.md]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- API prompts admin: [Source: C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py]
- Modele prompt versions: [Source: C:/dev/horoscope_front/backend/app/infra/db/models/llm_prompt.py]
- API frontend prompts admin: [Source: C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts]
- UI admin prompts existante: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `7f6a11b3 fix(admin-prompts): finalize story 70.8 review follow-ups`
  - `2ff7f718 test(admin-prompts): close residual coverage risk on consumption`
  - `f2b5dd79 feat(admin-prompts): story 70.7 — route consommation pilotable et artefacts BMAD`
  - `b4bea5ff test(admin-prompts): intégration release→catalogue et hint manifeste complet`
  - `cf4b3eef feat(admin-prompts): story 70.6 — route release investigation, revue code`
- Constat codebase avant creation:
  - historique prompts admin deja disponible via `list_prompt_history`
  - create/publish/rollback deja exposes par `admin_llm.py`
  - types frontend encore en `draft | published | archived`
  - UI legacy deja branchee sur `useAdminPromptHistory()` et `useRollbackPromptVersion()`

### Completion Notes List

- Cycle de vie normalise sur `draft/inactive/published`, avec compatibilite de lecture pour les anciennes lignes `archived` afin de ne pas casser l historique existant ni le rollback legacy.
- Publication et rollback durcis pour conserver l invariant d une unique version `published` par `use_case_key`, en passant l ancienne version publiee a `inactive` au lieu d un archivage destructif.
- Audit admin enrichi sur `create draft`, `publish` et `rollback` avec `use_case_key`, `from_version`, `to_version` et `result_status`, sans exposer le contenu integral du prompt.
- UI legacy enrichie pour afficher la date de publication dans l historique et rendre plus lisible la nouvelle version historisee apres sauvegarde/publication.
- Invalidation React Query harmonisee apres rollback legacy pour recharger de facon coherente les use cases, l historique et le catalogue sans exiger un refresh manuel de la page.
- Migration Alembic ajoutee pour remapper les statuts persistants `archived` vers `inactive`, afin d eliminer la derive de donnees legacy en base.
- Test frontend etendu pour verifier le scenario complet de rollback legacy avec rechargement de la version active et mise a jour de la date de publication visible.
- Bruit de debug retire des tests backend avant livraison.
- Non-regression backend/frontend couverte par des tests cibles sur les transitions de statut, la compatibilite `archived`, l historique et les messages de feedback operateur.
- Validations executees:
  - `pytest app/llm_orchestration/tests/test_prompt_registry_v2.py app/llm_orchestration/tests/test_admin_llm_api.py -q` -> 12 tests passes
  - `ruff format` puis `ruff check` sur les fichiers backend modifies -> OK
  - `npm test -- --run AdminPromptsPage.test.tsx` -> 30 tests passes
  - `npm run lint` cote frontend -> OK

### File List

- _bmad-output/implementation-artifacts/70-10-historiser-comparer-et-auditer-chaque-sauvegarde-de-prompt.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/api/v1/routers/admin_llm.py
- backend/app/infra/db/models/llm_prompt.py
- backend/migrations/versions/20260419_0070_remap_llm_prompt_archived_to_inactive.py
- backend/app/llm_orchestration/admin_models.py
- backend/app/llm_orchestration/services/prompt_registry_v2.py
- backend/app/llm_orchestration/tests/test_admin_llm_api.py
- backend/app/llm_orchestration/tests/test_prompt_registry_v2.py
- frontend/src/api/adminPrompts.ts
- frontend/src/i18n/adminPromptsLegacy.ts
- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/tests/AdminPromptsPage.test.tsx

## Change Log

- 2026-04-18 : creation de la story 70.10 (historisation, statuts, diff, rollback et audit des sauvegardes de prompt).
- 2026-04-19 : implementation du workflow `draft/inactive/published`, enrichissement de l audit et exposition de la date de publication dans l historique legacy.
- 2026-04-19 : correction des risques residuels de revue avec invalidation complete apres rollback, migration de remap `archived -> inactive`, couverture UI rollback renforcee et nettoyage du bruit de debug.
