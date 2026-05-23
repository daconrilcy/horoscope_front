# Story CS-232 remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases: Remove Legacy Runtime Surfaces And Aspect Compatibility Aliases
Status: done

## 1. Objective

Supprimer ou confiner les surfaces legacy qui ne doivent plus servir de sources metier internes apres la migration vers `chart_objects`,
le graphe de calcul et les contrats d'aspects separes.
La story conserve les projections publiques uniquement via serializers ou adapters publics nommes, avec preuves API, front et tests.

## 2. Trigger / Source

- Source type: architecture-runtime-cleanup.
- Source reference: `_story_briefs/cs-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases.md`.
- Reason for change: CS-229, CS-230 et CS-231 preparent la separation, mais les aliases et champs legacy peuvent rester faciles a consommer.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: story de suppression backend-domain avec controle API/front, sans DB, prompt, score, auth, i18n, style ou dependance.

## References

- `_story_briefs/cs-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases.md`.
- `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/00-story.md`.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md`.
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/00-story.md`.
- `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/00-story.md`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102|RG-103|RG-145|RG-147|RG-148`.

## 3. Domain Boundary

Cette story appartient au domaine astrologie runtime et aux projections publiques chart:

- Domain: `backend/app/domain/astrology`.
- Integration surfaces:
  - `backend/app/services/chart/json_builder.py` pour les projections publiques natal/chart;
  - `backend/app/domain/prediction` et `backend/app/services/prediction` pour les contrats de valence dedies;
  - `backend/app/infra/db/repositories` pour les vues de referentiel structurelles et interpretatives;
  - `frontend/src` seulement pour verifier une compatibilite de payload expose.
- In scope:
  - produire l'inventaire final des lectures legacy internes;
  - migrer les consommateurs internes vers `chart_objects`, structural runtime, interpretive hints ou graph outputs;
  - supprimer les aliases d'aspects temporaires crees par CS-230;
  - retirer les champs interpretatifs des resultats structurels d'aspects;
  - confiner les projections publiques a un serializer ou adapter public nomme;
  - mettre a jour `docs/architecture/astrology-runtime-surfaces.md`;
  - comparer `app.routes`, `app.openapi()` et les usages frontend quand une surface publique est touchee;
  - renforcer les tests d'architecture anti-retour;
  - supprimer ou justifier les allowlists temporaires issues de CS-229 a CS-231.
- Out of scope:
  - supprimer un champ public sans preuve d'absence d'usage front/API;
  - supprimer des tables DB de reference;
  - changer les textes d'interpretation;
  - changer les scores de prediction;
  - migrer des domaines non lies aux surfaces natal/aspect;
  - refactoriser massivement des fichiers non concernes;
  - creer une nouvelle branche Git.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas conserver un alias legacy non borne;
  - ne pas transformer une projection publique en source metier interne;
  - ne pas modifier volontairement DB, migrations, prompt, auth, i18n, style ou build.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime des surfaces runtime legacy et confine les projections publiques, avec controles API/front.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: suppression d'aliases internes legacy sans consommateur public;
  - autorise: migration des consommateurs internes vers surfaces canoniques;
  - autorise: confinement public via serializer ou adapter nomme;
  - autorise: reduction d'allowlists temporaires avec preuve;
  - interdit: suppression publique sans preuve front/API, changement DB, score, doctrine, prompt, auth, style, build ou dependance.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une sortie publique, un contrat front/API, une migration DB, un score, un prompt ou une dependance doit changer.
- Additional validation rules:
  - aucune lecture metier interne ne consomme `planet_positions`, `houses`, `advanced_conditions`, `dignities` ou `fixed_star_conjunctions` comme source canonique;
  - `AspectRuntimeData.interpretation` est supprime ou confine a un adapter legacy public borne;
  - `AspectCalculationResult` structurel ne porte pas `default_valence`, `interpretive_valence` ou `energy_type`;
  - `AspectModifierRuntimeData` ne porte pas `interpretive_weight` hors contrat de hints ou adapter dedie;
  - les calculateurs structurels ne consomment pas de definition d'aspect qui oblige une valence ou un energy type;
  - prediction consomme un contrat dedie ou une projection, jamais le runtime structurel hybride;
  - les projections publiques restantes sont produites par serializer ou adapter public;
  - les allowlists temporaires restantes nomment chemin, champ, raison et story de sortie;
  - toute suppression de champ expose est accompagnee d'un diff `app.openapi()`, d'une recherche `frontend/src` et d'un test public;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent le delta public autorise.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `chart_objects`, structural runtime et interpretive hints sont les sources canoniques. |
| Baseline Snapshot | yes | Les hits legacy doivent etre classes avant suppression. |
| Ownership Routing | yes | Calculateurs, serializers, adapters legacy, prediction et tests ont des owners distincts. |
| Allowlist Exception | yes | Les surfaces conservees doivent rester bornees, nommees et justifiees. |
| Contract Shape | yes | Les champs supprimes, conserves et projetes doivent etre explicites. |
| Batch Migration | yes | Inventaire, migration, confinement, suppression et preuves sont livres par lots controlables. |
| Reintroduction Guard | yes | Les tests bloquent le retour des lectures legacy internes et champs hybrides. |
| Persistent Evidence | yes | Scans, OpenAPI, front, tests et decisions d'allowlist doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `NatalResult.chart_objects`;
  - `ChartObjectRuntimeData.payloads`;
  - structural aspect runtime;
  - interpretive hints;
  - calculation graph outputs;
  - public serializers et adapters nommes pour les projections exposees.
- Runtime/domain artifacts:
  - inventaire cible des lectures legacy;
  - tests AST anti-lecture legacy interne;
  - tests AST anti-champs interpretatifs dans les contrats structurels;
  - tests de projection publique;
  - evidence `app.routes`, `app.openapi()` et `TestClient`;
  - evidence frontend cible quand un payload expose change.
- Secondary evidence:
  - `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`;
  - `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`;
  - `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`;
  - `pytest -q backend/app/tests/unit/test_chart_json_builder.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni la compatibilite publique, ni la forme OpenAPI, ni le routage prediction.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - recherche ciblee `planet_positions|astral_points|houses|advanced_conditions|dignities|fixed_star_conjunctions`;
  - recherche ciblee `AspectRuntimeData.interpretation|default_valence|interpretive_valence|energy_type|interpretive_weight`;
  - classification des hits dans `backend/app/domain/prediction`, `backend/app/services/prediction`, `backend/app/infra/db/repositories` et `frontend/src`;
  - lecture ciblee de `docs/architecture/astrology-runtime-surfaces.md`;
  - `Select-String "RG-098|RG-099|RG-100|RG-101|RG-102|RG-103|RG-145|RG-147|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres migration;
  - tests CS-232 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - recherche frontend ciblee quand une cle publique change;
  - diff adjacent sur DB, migrations, prompts, scores, auth, i18n, style et build.
- Expected invariant:
  - les flux internes lisent `chart_objects`, runtime structurel, hints ou graph outputs;
  - les champs publics conserves sont produits par serializer ou adapter public;
  - les champs interpretatifs ne reviennent pas dans les contrats structurels;
  - prediction garde sa valence par contrat dedie;
  - aucun endpoint public ne change sans preuve explicite.
- Allowed differences:
  - suppressions d'aliases internes non publics;
  - migrations de consommateurs internes vers surfaces canoniques;
  - allowlists reduites;
  - documentation d'architecture alignee;
  - evidence persistante CS-232;
  - Registry gap: un invariant global dedie a l'extinction des aliases legacy runtime pourra etre ajoute ulterieurement.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Source natal interne | `NatalResult.chart_objects` | collections legacy comme source metier |
| Faits d'aspects structurels | structural aspect runtime | contrats avec valence ou energy type |
| Hints interpretatifs | resolver ou adapter de hints | calculateur structurel |
| Projection publique | serializer ou adapter public | calculateur metier |
| Legacy transitoire | adapter legacy nomme | alias libre sur contrat structurel |
| Prediction | contrat prediction dedie | lecture du runtime structurel hybride |
| Reference aspect | vues structurelle et interpretative separees | vue hybride obligatoire |
| Compatibilite front | client/API public testes | changement silencieux de payload |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/services/chart/json_builder.py` | champs publics historiques | Projection publique compatible. | Permanent tant que le contrat public existe. |
| adapters legacy nommes | alias legacy borne | Transition publique explicite. | Temporary; exit condition: story de retrait approuvee. |
| `backend/app/domain/prediction` | valence et energy type dedies | Contrat prediction hors runtime structurel. | Permanent selon contrat prediction. |
| tests et fixtures | donnees historiques | Non-regression et comparaison. | Borne aux tests, fixtures et evidence. |

Validation rule:

- Toute allowlist restante doit contenir chemin, champ, raison et sortie ou decision de permanence.

## 4f. Contract Shape

- Contract type:
  - contrats Python runtime;
  - serializers et adapters publics;
  - tests d'architecture AST;
  - documentation markdown;
  - aucune nouvelle API HTTP.

Fields:

- surface;
- statut avant;
- statut cible;
- action;
- owner;
- preuve;
- classification de suppression;
- remplacement canonique.

Required fields:

  - surface;
  - statut avant;
  - statut cible;
  - action;
  - owner;
  - preuve.
- Required surfaces:
  - `NatalResult.chart_objects`;
  - `NatalResult.planet_positions`;
  - `NatalResult.houses`;
  - `NatalResult.advanced_conditions`;
  - `dignities`;
  - `fixed_star_conjunctions`;
  - `AspectRuntimeData.interpretation`;
  - `AspectCalculationResult.default_valence`;
  - `AspectCalculationResult.interpretive_valence`;
  - `AspectCalculationResult.energy_type`;
  - `AspectModifierRuntimeData.interpretive_weight`;
  - `AspectDefinitionRuntimeData.default_valence`;
  - `AstrologyRuntimeReference.aspects`.
- Required structural fields:
  - identifiants;
  - corps astrologiques;
  - positions;
  - angles;
  - orbes;
  - forces techniques;
  - payloads factuels;
  - provenance du graphe.
- Forbidden structural fields:
  - `default_valence`;
  - `interpretive_valence`;
  - `energy_type`;
  - `interpretive_weight`;
  - alias `interpretation` comme source metier;
  - narration, prompt ou LLM.

Optional fields:

- story de sortie;
- preuve OpenAPI;
- preuve frontend;
- adapter public;
- projection legacy bornee.

Status codes:

- no HTTP endpoint, method or status code is changed without explicit public contract evidence.
- Serialization names:
  - les noms JSON publics restent inchanges sans preuve OpenAPI/front et decision explicite.
- Frontend type impact:
  - verifier `frontend/src` si une surface publique est modifiee.
- Generated contract impact:
  - `app.routes`, `app.openapi()` et `TestClient` doivent documenter le delta public autorise ou l'absence de delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | lectures legacy non classees | inventaire CS-232 | aucun runtime | evidence scan | classification complete | hit non classe |
| 2 | sources natal historiques | `chart_objects` et payloads | consommateurs internes | architecture/unit | AST guard | usage metier restant |
| 3 | aliases aspect legacy | structural runtime + hints | aspects/prediction | unit/integration | zero alias interne | consommateur public non prouve |
| 4 | champs hybrides structurels | contrats separes | calculators/reference | architecture | zero field structurel | score change |
| 5 | projections publiques implicites | serializer/adapter public | chart JSON | API/public tests | app.openapi | front casse |
| 6 | allowlists temporaires | allowlist reduite | tests guardrails | architecture | sortie documentee | alias sans sortie |
| 7 | docs obsoletes | doc runtime alignee | docs only | doc test | matrice a jour | invariant absent |

Completion rule: chaque batch conserve `pytest`, `app.routes`, `app.openapi()`, scores, orbes, doctrine et contrats publics autorises.

## 4h. Reintroduction Guard

- Guard target:
  - aucune lecture metier interne des collections natal legacy comme source canonique;
  - aucun alias `AspectRuntimeData.interpretation` non borne;
  - aucun champ de valence ou energy type dans un contrat structurel d'aspect;
  - aucune projection publique produite par un calculateur metier;
  - aucune allowlist temporaire sans sortie;
  - aucun changement public sans preuve `app.openapi()` et recherche frontend.
- Guard mechanism:
  - architecture guard explicite contre tout symbole legacy reintroduced dans les zones structurelles;
  - deterministic source: forbidden symbols;
  - deterministic source: generated openapi paths;
  - tests d'architecture AST sur chemins backend-domain explicites;
  - scan cible des tokens legacy et champs hybrides;
  - tests unitaires de projection publique;
  - tests de contrats aspect structurels et hints;
  - preuve `app.routes`, `app.openapi()` et `TestClient`;
  - recherche ciblee `frontend/src` pour les cles publiques touchees.
- Guard owner:
  - `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`;
  - `backend/tests/architecture/test_chart_interpretation_input_boundary.py`;
  - `backend/tests/architecture/test_structural_runtime_boundary.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`;
  - chemin complet `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`;
  - chemin complet `pytest -q backend/app/tests/unit/test_chart_json_builder.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Legacy surface inventory | `evidence/legacy-surface-inventory.md` | Classer chaque hit legacy et son owner cible. |
| Public contract evidence | `evidence/public-contract.md` | Conserver `app.routes`, `app.openapi()`, TestClient et recherche front. |
| Validation evidence | `evidence/validation.md` | Conserver lint, tests, scans et decisions d'allowlist. |

## 5. Current State Evidence

- Le brief indique que plusieurs surfaces sont deja documentees comme projections de compatibilite.
- Le brief indique que CS-230 peut avoir conserve des aliases temporaires d'aspects.
- CS-224 a deja pose `chart_objects` comme surface runtime canonique du theme natal.
- CS-229 et CS-230 separent structural runtime, interpretive hints, projection publique et legacy adapters.
- CS-231 demande des guards de frontiere structural versus interpretive.
- Evidence 1: `_story_briefs/cs-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases.md` - demande une suppression progressive.
- Evidence 2: `backend` - existe dans l'arborescence courante.
- Evidence 3: `frontend` - existe dans l'arborescence courante.
- Evidence 4: `docs/architecture/astrology-runtime-surfaces.md` - existe.
- Evidence 5: `backend/tests/architecture` - existe.
- Evidence 6: `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` - existe.
- Evidence 7: `.agents/skills/condamad-story-writer/scripts/condamad_story_lint.py` - existe.
- Evidence 8: `.agents/skills/condamad-story-writer/SKILL.md` - absent, comme le cheatsheet demande et `resolve_guardrails.py`.

## 6. Target State

- Les surfaces legacy ne sont plus lues comme sources metier internes.
- Les aliases temporaires d'aspects sont supprimes ou confinees a un adapter public nomme.
- Les resultats structurels d'aspects ne portent plus de valence, energy type ou poids interpretatif.
- Les hints interpretatifs centralisent valence, energy type, axes semantiques et poids interpretatifs.
- Les projections publiques restantes sont produites par serializer ou adapter public.
- Les allowlists temporaires de CS-229 a CS-231 sont supprimees ou reliees a une story de sortie.
- `docs/architecture/astrology-runtime-surfaces.md` documente le statut final des surfaces.
- `app.routes`, `app.openapi()`, `pytest`, `TestClient` et la recherche frontend prouvent la compatibilite publique.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- runtime-contracts: yes;
- astrology structural calculators: yes;
- chart public projection: yes;
- prediction boundary: limited;
- frontend contract check: limited;
- API: no silent public delta;
- DB/migrations: no;
- auth/i18n/style/build: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-098 | local | Les faits runtime d'aspect restent produits par runtime et evaluator dedies. |
| RG-099 | local | Les champs publics d'aspects viennent du runtime canonique ou d'une projection dediee. |
| RG-100 | local | L'assemblage interpretatif reste hors calculateurs et sans appel LLM dans astrology. |
| RG-102 | local | La couche semantique reste separee du renderer editorial et de prediction. |
| RG-103 | local | `interpretive_weight` et les poids prediction restent separes par owner. |
| RG-145 | local | Le moteur d'aspects ne relit pas les collections legacy natal. |
| RG-147 | local | Dignity et dominance restent projetes par payloads, sans retour a `planet_positions`. |
| RG-148 | local | House position et rulership restent portes par payloads, sans second resolver local. |

Non-applicable examples:

- DB/migration guardrails: hors scope, aucune table ni migration Alembic n'est modifiee.
- Frontend/style/build guardrails: seul un controle de contrat front est attendu, aucun refactor React ou CSS n'est vise.
- Auth/i18n guardrails: hors scope, aucune authentification ou localisation n'est modifiee.

Registry gap:

- Aucun guardrail global dedie a l'extinction definitive des aliases legacy runtime n'existe encore.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | Les surfaces legacy ne sont plus lues comme sources metier internes. | `AST guard`; `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`. |
| AC2 | Le runtime structurel d'aspects ne contient plus de champs semi-interpretatifs. | `AST guard`; `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`. |
| AC3 | Les signaux interpretatifs passent par les hints. | `pytest -q backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`. |
| AC4 | Les champs publics conserves sont produits par serializer ou adapter public. | `TestClient`; `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC5 | Les allowlists temporaires ont une sortie. | `AST guard`; `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`. |
| AC6 | Chaque surface exposee touchee conserve son contrat API/front. | `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; `app.openapi()`. |
| AC7 | Les calculateurs structurels ne consomment pas une definition d'aspect hybride. | `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`. |
| AC8 | Prediction conserve sa valence via un contrat dedie ou une projection. | `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`. |

## 8. Implementation Tasks

- [x] Task: inventorier les lectures legacy par recherche ciblee et classer chaque hit. (AC: AC1)
- [x] Task: migrer les consommateurs internes natal vers `chart_objects`, payloads ou graph outputs. (AC: AC1)
- [x] Task: supprimer ou confiner `AspectRuntimeData.interpretation` dans un adapter public borne. (AC: AC2)
- [x] Task: retirer les champs de valence, energy type et poids interpretatif des contrats structurels. (AC: AC2)
- [x] Task: router les besoins interpretatifs vers les hints et contrats dedies. (AC: AC3)
- [x] Task: verifier `json_builder` et adapters publics pour les champs exposes conserves. (AC: AC4)
- [x] Task: reduire les allowlists temporaires et documenter les stories de sortie restantes. (AC: AC5)
- [x] Task: comparer `app.routes`, `app.openapi()` et `TestClient` pour les surfaces publiques touchees. (AC: AC6)
- [x] Task: rechercher les usages frontend des cles publiques touchees et adapter les tests front cibles. (AC: AC6)
- [x] Task: ajouter ou renforcer les tests d'architecture sur les definitions d'aspects structurelles. (AC: AC7)
- [x] Task: verifier que prediction lit une projection ou un contrat dedie. (AC: AC8)
- [x] Task: mettre a jour `docs/architecture/astrology-runtime-surfaces.md` et l'evidence CS-232. (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser les tests d'architecture CS-224, CS-230 et CS-231 avant de creer un nouveau helper.
- Reutiliser `docs/architecture/astrology-runtime-surfaces.md` comme documentation canonique.
- Reutiliser les adapters publics existants pour les projections publiques.
- Reutiliser les contrats de hints introduits par CS-230.
- Ne pas creer un second registre global de guardrails.
- Ne pas dupliquer les listes de surfaces legacy dans plusieurs fichiers sans helper local commun.
- Ne pas ajouter de dependance externe.

## 10. No Legacy / Forbidden Paths

- Ne pas utiliser `planet_positions`, `houses`, `advanced_conditions`, `dignities` ou `fixed_star_conjunctions` comme source metier interne.
- Ne pas conserver `AspectRuntimeData.interpretation` comme alias libre.
- Ne pas preserver une surface legacy via un shim non borne.
- Ne pas ajouter une compatibility layer sans owner, preuve publique et sortie.
- Ne pas placer `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` dans un contrat structurel.
- Ne pas lire la valence prediction depuis le runtime structurel.
- Ne pas supprimer une cle publique sans preuve `app.openapi()`, TestClient et recherche frontend.
- Ne pas modifier DB, migrations, prompts, scores, doctrine, auth, i18n, style ou build.
- Ne pas ajouter de fallback silencieux ou shim non borne.
- Ne pas scanner tout le depot dans les guards.
- Ne pas ajouter de `requirements.txt`.
- Ne pas creer de nouvelle branche Git.

## 11. Removal Classification Rules

La classification doit etre deterministe:

- `canonical-active`: l'element est le proprietaire canonique ou reste requis par le runtime cible.
- `external-active`: l'element est reference par API publique, frontend, documentation publique ou client connu.
- `historical-facade`: l'element delegue a une implementation canonique pour preserver une ancienne surface.
- `dead`: l'element n'a aucune reference dans production, tests, documentation, contrats generes ou surfaces externes connues.
- `needs-user-decision`: une ambiguite persiste apres les scans obligatoires et bloque la suppression.

## 12. Removal Audit Format

Chemin obligatoire de la table d'audit:

- `_condamad/stories/CS-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases/evidence/legacy-surface-inventory.md`

Table d'audit obligatoire:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| surface legacy | field/module/alias | classification | owner liste | surface cible | keep/remove/confine | scan/test | risque |

Allowed decisions:

- `delete`;
- `replace-consumer`;
- `confine-public-adapter`;
- `keep-public-contract`;
- `needs-user-decision`.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Source natal interne | `NatalResult.chart_objects` | collections legacy |
| Aspects structurels | structural runtime | champs valence et energy type |
| Hints interpretatifs | resolver ou adapter de hints | calculateur structurel |
| Projection publique | serializer ou adapter public | source metier interne |
| Prediction | contrat prediction dedie | runtime structurel hybride |
| Documentation surfaces | `docs/architecture/astrology-runtime-surfaces.md` | notes dispersees |

## 14. Delete-Only Rule

Les elements classes `dead` doivent etre supprimes, pas repointes.
They must be deleted, not repointed.

Interdit:

- rediriger vers une surface legacy;
- preserver un wrapper;
- preserver un re-export;
- creer un shim;
- ajouter un fallback;
- deplacer le meme alias vers un autre module.

## 15. External Usage Blocker

- External usage blocker: public API and frontend consumers must remain compatible.
- If an item is `external-active`, it must not be deleted without a user decision.
- Required proof:
  - `app.routes`;
  - `app.openapi()`;
  - `TestClient` on the public chart or natal path covered by existing tests;
  - targeted search under `frontend/src`;
  - no voluntary public schema delta unless the decision is documented.

## 16. Generated Contract Check

- Capture before:
  - `app.routes`;
  - `app.openapi()`;
  - smoke `TestClient` OpenAPI;
  - snapshot ou test public natal/chart;
  - recherche ciblee `frontend/src` pour les cles exposees touchees.
- Capture after:
  - memes preuves.
- Expected result:
  - aucun endpoint, method, status code, schema public ou cle JSON publique ne change sans preuve explicite et decision documentee.

## 17. Files to Inspect First

- `docs/architecture/astrology-runtime-surfaces.md`.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- `backend/tests/architecture/test_structural_runtime_boundary.py`.
- `backend/app/domain/astrology/runtime`.
- `backend/app/domain/astrology/calculators`.
- `backend/app/domain/astrology/builders`.
- `backend/app/domain/astrology/interpretation`.
- `backend/app/services/chart/json_builder.py`.
- `backend/app/domain/prediction`.
- `backend/app/services/prediction`.
- `backend/app/infra/db/repositories`.
- `frontend/src` avec recherche ciblee sur les cles publiques touchees.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102|RG-103|RG-145|RG-147|RG-148`.

## 18. Expected Files to Modify

Likely files:

- `docs/architecture/astrology-runtime-surfaces.md`.
- `backend/app/domain/astrology/runtime`.
- `backend/app/domain/astrology/calculators`.
- `backend/app/domain/astrology/builders`.
- `backend/app/domain/astrology/interpretation`.
- `backend/app/services/chart/json_builder.py`.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- `backend/tests/architecture/test_structural_runtime_boundary.py`.
- `_condamad/stories/CS-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases/evidence/legacy-surface-inventory.md`.
- `_condamad/stories/CS-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases/evidence/public-contract.md`.
- `_condamad/stories/CS-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases/evidence/validation.md`.

Likely tests:

- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- `backend/tests/architecture/test_structural_runtime_boundary.py`.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- `backend/app/tests/unit/test_chart_json_builder.py`.
- `backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`.

Files not expected to change:

- `backend/alembic`.
- prompt templates and LLM providers.
- DB models, seeds and migrations.
- frontend files, sauf adaptation testee apres decision de delta public.

## 19. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 20. Validation Plan

Run all Python commands from repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted tests:

```powershell
pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py
pytest -q backend/tests/architecture/test_structural_runtime_boundary.py
pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py
```

Run anti-regression scans:

```powershell
rg -n "planet_positions|astral_points|houses|advanced_conditions|dignities|fixed_star_conjunctions" `
  backend/app/domain/astrology backend/app/services/chart backend/app/domain/prediction backend/app/services/prediction -g "*.py"
rg -n "AspectRuntimeData\.interpretation|default_valence|interpretive_valence|energy_type|interpretive_weight" `
  backend/app/domain/astrology backend/app/services/chart backend/app/domain/prediction backend/app/services/prediction -g "*.py"
if (Test-Path .git) {
  git diff -- backend/app/api backend/alembic frontend/src
} else {
  "Repository is not a Git repository; skip git diff evidence."
}
```

Run API and frontend contract proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
rg -n "planet_positions|houses|advanced_conditions|fixed_star_conjunctions|interpretive_valence|energy_type" frontend/src
```

The dedicated public contract evidence must name `app.routes`, `app.openapi()`, `TestClient`, `pytest` and frontend search results.

## 21. Regression Risks

- Une suppression interne peut etre confondue avec une suppression publique.
- Un alias temporaire peut rester dans un contrat structurel et devenir une nouvelle surface legacy.
- Prediction peut continuer a lire une valence via runtime structurel hybride.
- Un serializer public peut produire une projection depuis un calculateur metier au lieu d'un adapter.
- Une allowlist trop large peut masquer un retour de lecture legacy.
- Un changement OpenAPI peut passer sans recherche frontend ciblee.

## 22. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only CS-232.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Implementer le plus petit delta coherent.
- Garder les commentaires globaux et docstrings en francais dans les nouveaux fichiers applicatifs.
- Ne pas utiliser de style inline, CSS ou frontend sauf adaptation testee d'un delta public approuve.
- Ne pas creer de `requirements.txt`.
- Executer les validations apres activation du venv.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in story evidence.
- Do not preserve legacy behavior through an unbounded fallback, shim or compatibility layer.
- Conserver dans l'evidence les commandes lancees, resultats de tests, scans, `app.routes`, `app.openapi()` et recherche frontend.

## 23. CS-232 Final Evidence Template

```markdown
## CS-232 Final Evidence

### Legacy Surface Inventory
- Each legacy hit is classified as internal source, public projection, adapter, prediction, test, fixture or temporary legacy.
- Internal source reads are migrated or deleted.

### Aspect Cleanup
- Structural contracts do not expose valence, energy type or interpretive weight.
- `AspectRuntimeData.interpretation` is removed or confined to a named adapter.

### Public Compatibility
- Public projections are owned by serializers or adapters.
- app.routes, app.openapi(), TestClient and frontend search are captured.

### Guardrails
- AST guard blocks internal legacy reads.
- Temporary allowlists include exit story or permanence decision.

### Commands
- ruff format backend
- ruff check backend
- pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py
- pytest -q backend/tests/architecture/test_structural_runtime_boundary.py
- pytest -q backend/app/tests/unit/test_chart_json_builder.py
```

## 24. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the brief, adjacent CS-224 and CS-229 to CS-231 structure.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted ID search only.
- No regression guardrail registry update was made.
- First story validation result: FAIL.
- First strict lint result: FAIL.
- Second story validation result: FAIL: missing decisions `delete`, `needs-user-decision`, `replace-consumer`; missing `re-export`; missing deterministic source.
- Second strict lint result: FAIL: same diagnostics as validation.
- Review-fix cycle 2026-05-23: la formulation du guard a ete alignee sur les stories adjacentes avec tests AST, scan cible et OpenAPI.
- Review-fix cycle 2026-05-23: les sources deterministes attendues par le validateur ont ete ajoutees avec les libelles exacts.
- Proof status 2026-05-23: correction non relancee, car validate et lint strict ont deja atteint deux tentatives dans ce cycle.

## 25. References

- Source brief: `_story_briefs/cs-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-098`, `RG-099`, `RG-100`, `RG-102`, `RG-103`, `RG-145`, `RG-147`, `RG-148`).
- Previous story: `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/00-story.md`.
