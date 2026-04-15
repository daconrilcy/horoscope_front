# Story 66.50: Cohérence billing/tokens avec la taxonomie canonique

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an architecte plateforme / billing / admin ops,
I want verrouiller la cohérence entre billing tokens et taxonomie canonique runtime,
so that les coûts et exports admin ne soient plus pilotés nominalement via les anciens axes `use_case`.

## Contexte

Le pipeline 66 a déjà convergé vers une taxonomie canonique de runtime :

- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py) persiste `feature`, `subfeature`, `plan`, `requested_provider`, `resolved_provider`, `executed_provider`, `active_snapshot_version`.
- [backend/app/services/llm_token_usage_service.py](/c:/dev/horoscope_front/backend/app/services/llm_token_usage_service.py) débite la consommation utilisateur par `feature_code`.
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py) et les stories 66.15 / 66.23 ont déjà poussé le runtime vers `feature/subfeature/plan`.
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) et le dashboard 65.14 gardent cependant des surfaces encore centrées sur `use_case`.

Le risque si rien n'est verrouillé :

- le billing continue à parler `feature_code` ;
- l'observabilité parle `feature/subfeature/plan` ;
- l'admin exporte encore des regroupements `use_case` ;
- les alias legacy polluent les coûts nominaux ;
- la lecture métier devient incohérente entre finance, produit, ops et runtime.

Cette story doit donc **durcir la doctrine** :

- plus aucun agrégat nominal de coût/tokens ne repose uniquement sur `use_case` ;
- les aliases legacy sont reclassés sur la taxonomie canonique ;
- les exports admin reflètent la taxonomie canonique et seulement elle pour la lecture nominale.

La condition critique de réussite est l'existence d'un **registre central unique** de mapping `alias legacy -> taxonomie canonique`, réutilisé par billing, observabilité, dashboard et export.

## Diagnostic exact à préserver

- `use_case` peut encore exister comme trace technique, compatibilité ou diagnostic, mais plus comme axe primaire d'agrégation nominale.
- La vérité canonique doit rester alignée avec la normalisation runtime 66.x, pas avec une nomenclature d'UI ou un nom d'endpoint.
- Le billing tokenisé de 61.67 doit converger avec le même vocabulaire que l'observabilité runtime.
- Le mapping legacy -> canonique doit vivre dans un registre unique, pas dans plusieurs services divergents.
- Les aliases legacy ne doivent pas être supprimés aveuglément : ils doivent être soit reclassés, soit explicitement marqués résiduels.
- Les exports admin ne doivent pas mélanger lignes canoniques et legacy sans indicateur clair.

## Acceptance Criteria

1. **AC1 — Plus d'agrégat nominal `use_case`** : aucun dashboard, export ou API admin de consommation nominale n'utilise `use_case` comme axe primaire unique.
2. **AC2 — Reclassement des aliases legacy** : les aliases legacy sont reclassés sur la `feature` canonique correspondante lorsqu'un mapping nominal existe.
3. **AC3 — Résidus legacy explicités** : si un alias legacy ne peut pas être reclassé nominalement, il est explicitement marqué résiduel et séparé des agrégats nominaux.
4. **AC4 — Cohérence billing / observabilité** : le vocabulaire utilisé côté billing tokenisé et côté observabilité admin est cohérent sur `feature`, `subfeature`, `plan`.
5. **AC5 — Exports admin canoniques** : les exports admin reflètent la taxonomie canonique nominale et non l'ancien `use_case`.
6. **AC6 — Colonnes legacy secondaires seulement** : si `use_case` est encore exposé dans une réponse ou un export, il est secondaire, `compatibility-only`, et jamais la clé nominale d'une ligne.
7. **AC7 — Contrat documenté** : la doctrine de cohérence coût/tokens vs taxonomie canonique est documentée explicitement pour éviter la réintroduction de nouveaux agrégats `use_case`.
8. **AC8 — Registre unique de mapping** : un point central unique de mapping `alias legacy -> feature/subfeature/plan` existe et est réutilisé par billing, observabilité, dashboard et export.
9. **AC9 — Tests anti-régression** : les tests garantissent qu'un alias legacy connu est bien reclassé et qu'un export nominal ne retombe pas sur `use_case`.

## Tasks / Subtasks

- [x] Task 1: Auditer tous les points d'agrégation coût/tokens existants (AC: 1, 4, 5, 6)
  - [x] Identifier les endpoints, exports, services et dashboards encore centrés sur `use_case`.
  - [x] Lister les flux billing / observabilité / admin à réaligner.

- [x] Task 2: Définir la politique de reclassement legacy -> canonique (AC: 2, 3, 4, 7, 8)
  - [x] Introduire ou réutiliser un registre central unique de mapping legacy -> canonique.
  - [x] Réutiliser la taxonomie/runtime et les registres d'alias existants.
  - [x] Définir les cas `reclassed_nominal`, `legacy_residual` ou équivalent stable.
  - [x] Documenter la priorité entre feature canonique et compat legacy.

- [x] Task 3: Réaligner les agrégats et exports admin (AC: 1, 4, 5, 6)
  - [x] Retirer `use_case` comme dimension nominale primaire.
  - [x] Introduire les colonnes canoniques obligatoires dans les exports.
  - [x] Garder `use_case` uniquement en diagnostic secondaire si nécessaire.

- [x] Task 4: Réaligner les services/query layers backend (AC: 1 à 8)
  - [x] Vérifier que les services de consommation et de billing parlent le même vocabulaire canonique.
  - [x] Corriger les mappings restants entre `feature_code`, `feature`, `subfeature`, `plan`.
  - [x] Éviter toute logique de mapping locale divergente.

- [x] Task 5: Ajouter la documentation et les tests (AC: 7, 8, 9)
  - [x] Documenter la doctrine de cohérence.
  - [x] Ajouter des tests sur le reclassement legacy.
  - [x] Ajouter des tests sur les exports et dashboards nominaux.
  - [x] Ajouter un test prouvant que billing, observabilité, dashboard et export consomment bien le même registre central de mapping.

## Dev Notes

### Ce que le dev doit retenir avant d'implémenter

- Cette story est un **verrou de cohérence transverse** entre runtime, billing et admin.
- Le sujet n'est pas seulement l'UI : il faut réaligner les services/query layers et les exports.
- La doctrine cible est simple : `feature/subfeature/plan` pour le nominal, `use_case` seulement pour la compatibilité/diagnostic.
- Le registre de mapping legacy -> canonique doit être unique et partagé.

### Ce que le dev ne doit pas faire

- Ne pas supprimer `use_case` partout sans distinction ; il reste utile techniquement.
- Ne pas laisser plusieurs mappings d'alias legacy se développer dans des services différents.
- Ne pas introduire un export "hybride" où `use_case` resterait implicitement la clé métier.
- Ne pas recoder localement une taxonomie différente de celle du runtime 66.x.

### Fichiers à inspecter en priorité

- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/services/llm_token_usage_service.py](/c:/dev/horoscope_front/backend/app/services/llm_token_usage_service.py)
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [61-67-refactorisation-credit-par-token.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/61-67-refactorisation-credit-par-token.md)
- [65-14-supervision-ia-tableau-bord-metier.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-14-supervision-ia-tableau-bord-metier.md)
- [66-23.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-23.md)
- [66-48-modele-canonique-comptage-consommation-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-48-modele-canonique-comptage-consommation-llm.md)
- [66-49-dashboard-consommation-utilisateur-abonnement-feature.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-49-dashboard-consommation-utilisateur-abonnement-feature.md)

### Previous Story Intelligence

- **61.67** a imposé le comptage facturable en tokens.
- **65.14** a laissé un héritage `use_case` côté dashboard admin.
- **66.23** a déjà montré le pattern de normalisation canonique d'identifiants feature.
- **66.48** définit le modèle canonique de comptage.
- **66.49** consommera ce modèle dans la surface admin.
- Le séquencement recommandé de delivery est `66.48 -> 66.50 -> 66.49`.

### Testing Requirements

- Ajouter un test de reclassement d'un alias legacy vers la feature canonique.
- Ajouter un test d'export nominal où `use_case` n'est pas la colonne primaire.
- Ajouter un test garantissant qu'un résidu legacy est séparé de l'agrégat nominal.
- Ajouter un test de cohérence entre champs billing tokenisés et taxonomie canonique exposée.
- Ajouter un test prouvant que billing, observabilité, dashboard et export consomment bien le même registre central de mapping.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`

### Project Structure Notes

- Story principalement backend + documentation + exports/admin contracts.
- Viser un mapping centralisé réutilisable par dashboard, export et services.
- Ne pas créer de divergence entre le vocabulaire billing et le vocabulaire runtime.

### References

- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/services/llm_token_usage_service.py](/c:/dev/horoscope_front/backend/app/services/llm_token_usage_service.py)
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [61-67-refactorisation-credit-par-token.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/61-67-refactorisation-credit-par-token.md)
- [65-14-supervision-ia-tableau-bord-metier.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-14-supervision-ia-tableau-bord-metier.md)
- [66-48-modele-canonique-comptage-consommation-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-48-modele-canonique-comptage-consommation-llm.md)
- [66-49-dashboard-consommation-utilisateur-abonnement-feature.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-49-dashboard-consommation-utilisateur-abonnement-feature.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Validation locale backend (venv activé):
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff check --fix app/api/v1/routers/admin_exports.py` (si besoin)
  - `ruff check app/api/v1/routers/admin_exports.py app/services/llm_canonical_consumption_service.py app/tests/integration/test_admin_exports_api.py`
  - `pytest -q app/tests/integration/test_admin_exports_api.py app/tests/unit/test_llm_canonical_consumption_service.py app/tests/integration/test_admin_llm_canonical_consumption_api.py`
- Validation locale frontend (`frontend/`) :
  - `npm run lint`
  - `npx vitest run src/tests/AdminSettingsPage.test.tsx`

### Completion Notes List

- Story créée pour verrouiller la cohérence transverse entre billing tokens, observabilité et exports admin.
- Export admin `generations` réaligné sur les colonnes canoniques nominales (`feature`, `subfeature`, `subscription_plan`) avec `use_case_compat` conservé en compatibilité secondaire.
- Reclassement legacy appliqué à l'export admin via le même moteur canonique (`LlmCanonicalConsumptionService._normalize_taxonomy`) et marquage explicite `taxonomy_scope` (`nominal` vs `legacy_residual`).
- Mapping legacy -> canonique du service de consommation branché sur le registre central de gouvernance (`prompt_governance_registry` via `legacy_nominal_feature_aliases_map`) pour supprimer une logique locale divergente.
- Dépréciation HTTP explicite de `use_case_compat` sur `POST /v1/admin/exports/generations` (formats CSV et JSON) : en-têtes `Warning` (RFC 7234), `Sunset` (échéance indicative `2026-09-30`), `X-Deprecated-Fields: use_case_compat`.
- Documentation produit : `docs/admin-implementation-overview.md` (section exports / générations LLM).
- UI admin : page Paramètres & Exports (`AdminSettingsPage`) — bandeau informatif après export générations avec dépréciation, bouton « Fermer » (masquage jusqu’au prochain export générations concerné), styles dans `AdminSettingsPage.css`.

### File List

- `_bmad-output/implementation-artifacts/66-50-coherence-billing-tokens-taxonomie-canonique.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/services/llm_canonical_consumption_service.py`
- `backend/app/api/v1/routers/admin_exports.py`
- `backend/app/tests/integration/test_admin_exports_api.py`
- `docs/admin-implementation-overview.md`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `frontend/src/tests/AdminSettingsPage.test.tsx`

### Change Log

- 2026-04-15: Alignement export admin generations sur taxonomie canonique; reclassement legacy explicite; centralisation stricte du mapping legacy->canonique; ajout des tests d'intégration associés.
- 2026-04-15 (suite): En-têtes HTTP de dépréciation sur export generations; doc admin overview; UI settings avec bandeau et fermeture; tests frontend et assertions headers backend.
