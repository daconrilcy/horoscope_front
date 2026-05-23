# Story CS-231 runtime-boundary-guardrails-structural-vs-interpretive: Runtime Boundary Guardrails Structural Vs Interpretive
Status: done

## 1. Objective

Ajouter des guardrails d'architecture qui rendent testable la frontiere entre runtime structurel et runtime interpretatif.
La story bloque le retour des champs interpretatifs dans les calculateurs, contrats, builders et graph nodes structurels, sans changer la doctrine.

## 2. Trigger / Source

- Source type: architecture-runtime-guardrails.
- Source reference: `_story_briefs/cs-231-runtime-boundary-guardrails-structural-vs-interpretive.md`.
- Reason for change: CS-229 et CS-230 separent les couches, mais il manque une garde globale structural runtime versus interpretive runtime.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: la story ajoute tests d'architecture et documentation backend-domain, sans endpoint, frontend, DB, prompt, score ou dependance.

## References

- `_story_briefs/cs-231-runtime-boundary-guardrails-structural-vs-interpretive.md`.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md`.
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/00-story.md`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102|RG-145`.

## 3. Domain Boundary

Cette story appartient au domaine astrologie runtime, avec tests d'architecture backend:

- Domain: `backend/app/domain/astrology`.
- In scope:
  - ajouter `test_structural_runtime_does_not_expose_interpretive_fields`;
  - ajouter `test_interpretive_adapters_do_not_recalculate_structural_facts`;
  - ajouter ou completer le test de documentation des couches runtime;
  - proteger les contrats de referentiel consommes par les calculateurs structurels;
  - documenter les chemins autorises pour `default_valence`, `interpretive_valence`, `energy_type` et `interpretive_weight`;
  - definir une allowlist minimale, justifiee et bornee pour projections publiques et adapters legacy;
  - verifier que les fixtures et tests historiques ne rendent pas les scans bruyants;
  - prouver que les futurs calculateurs restent couverts par les zones structurelles explicites.
- Out of scope:
  - migrer les contrats d'aspects restants;
  - supprimer les champs publics du JSON natal;
  - supprimer des tables DB ou creer une migration Alembic;
  - modifier les prompts, les scores, les profils ou la doctrine astrologique;
  - modifier le frontend;
  - ajouter une dependance de lint externe.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas scanner tout le depot dans les tests;
  - ne pas imposer une interdiction globale au domaine prediction;
  - ne pas convertir les adapters interpretatifs en calculateurs structurels.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la story ajoute des tests d'architecture et une documentation de frontiere backend-domain sans contrat HTTP dedie.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: tests d'architecture AST et scans cibles par zones structurelles;
  - autorise: allowlist explicite pour projections publiques, adapters legacy, tests et fixtures;
  - autorise: mise a jour de `docs/architecture/astrology-runtime-surfaces.md`;
  - autorise: preuves `app.routes`, `app.openapi()`, `pytest` et `TestClient` de neutralite API;
  - interdit: changement volontaire de route, OpenAPI, JSON public, DB, frontend, score, doctrine, prompt ou dependance externe.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'implementation veut supprimer un champ public, modifier une migration DB, toucher le frontend, changer un prompt ou reduire une surface legacy.
- Additional validation rules:
  - les zones structurelles scannees couvrent calculators, runtime, builders, dominance, fixed stars, dignities et advanced planetary conditions;
  - les tokens interpretatifs listes dans `Contract Shape` sont interdits hors allowlist structurelle;
  - les adapters interpretatifs ne rappellent aucun calculateur structurel liste;
  - les projections publiques restent des lectures/projections et ne deviennent pas sources metier;
  - les chemins prediction restent classes par contrat dedie et ne sont pas bloques par le guard structurel;
  - les fixtures et tests historiques sont exclus par chemins explicites, pas par silence global;
  - les contrats de referentiel structurel ne forcent pas `default_valence`, `interpretive_valence` ou `energy_type`;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta API volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les calculateurs structurels doivent rester proprietaires des faits runtime, pas des hints interpretatifs. |
| Baseline Snapshot | yes | Les chemins structurels et interpretatifs doivent etre classes avant d'ecrire les guards. |
| Ownership Routing | yes | Calculateurs, adapters interpretatifs, projections publiques, prediction et legacy ont des owners distincts. |
| Allowlist Exception | yes | Chaque surface autorisee doit lister chemin, champ, raison et sortie si temporaire. |
| Contract Shape | yes | Les champs autorises et interdits par couche doivent etre explicites. |
| Batch Migration | yes | Tests, docs, allowlist et preuves doivent etre livres par lots controlables. |
| Reintroduction Guard | yes | Les guards bloquent le retour des champs interpretatifs dans les zones structurelles. |
| Persistent Evidence | yes | Les resultats de tests, scans, OpenAPI et decisions d'allowlist doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - runtime structurel sous `backend/app/domain/astrology/runtime`;
  - calculateurs sous `backend/app/domain/astrology/calculators`;
  - builders structurels sous `backend/app/domain/astrology/builders`;
  - `docs/architecture/astrology-runtime-surfaces.md`;
  - tests d'architecture sous `backend/tests/architecture`.
- Runtime/domain artifacts:
  - guard AST des champs interpretatifs interdits dans les zones structurelles;
  - guard des adapters interpretatifs sans recalcul structurel;
  - test de documentation des couches runtime;
  - test ou import cible du contrat de referentiel structurel;
  - allowlist minimale et justifiee;
  - preuves `app.routes`, `app.openapi()` et `TestClient`.
- Secondary evidence:
  - `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`;
  - `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas la neutralite API, la forme des contrats runtime importables ni le routage des adapters.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content docs/architecture/astrology-runtime-surfaces.md`;
  - recherche ciblee des champs interdits dans les zones structurelles explicites;
  - recherche ciblee des appels de recalcul dans les adapters interpretatifs;
  - recherche ciblee des contrats `runtime_reference.py`, `astrology_runtime_reference_mapper.py` et `reference_repository.py`;
  - `Select-String "RG-098|RG-099|RG-100|RG-101|RG-102|RG-145" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres implementation;
  - tests d'architecture CS-231;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend, prompts et scores.
- Expected invariant:
  - les calculateurs structurels ne produisent pas de pre-interpretation;
  - les adapters interpretatifs ne recalculent pas les faits structurels;
  - les projections publiques restent isolees;
  - les surfaces legacy restent allowlistees et bornees;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - nouveaux tests d'architecture;
  - documentation de matrice des couches;
  - allowlist locale des projections publiques et legacy;
  - evidence persistante CS-231;
  - Registry gap: un invariant global dedie structural runtime versus interpretive runtime pourra etre ajoute ulterieurement.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Faits structurels | calculateurs et contrats runtime structurels | adapters interpretatifs |
| Hints interpretatifs | adapters ou resolvers interpretatifs | calculateurs structurels |
| Textes narratifs | prompt/LLM services ou renderer editorial | runtime structurel |
| Providers LLM | services LLM dedies | domain astrology structurel |
| Projection publique | `backend/app/services/chart/json_builder.py` | source metier structurelle |
| Projection legacy | adapter allowliste borne | nouveau calculateur |
| Prediction | contrat prediction dedie | guard structurel global non cible |
| Reference runtime | vues separees structurelle et interpretative | vue hybride obligatoire pour calculateurs |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/services/chart/json_builder.py` | champs publics historiques | Projection publique compatible. | Permanent pour payload public existant. |
| `chart_interpretation_input_builder.py` | hints interpretatifs | Owner des profils et hints pre-narratifs. | Permanent hors recalcul structurel. |
| `aspect_interpretation_facts.py` | faits semantiques d'aspects | Adaptation semantique depuis faits structurels. | Permanent hors recalcul structurel. |
| `backend/app/domain/prediction/contracts.py` | contrats prediction | Usage dedie hors runtime structurel. | Permanent selon contrat prediction. |
| `backend/app/services/prediction/prediction_service.py` | orchestration prediction | Hors runtime structurel. | Permanent selon contrat prediction. |
| tests et fixtures | donnees historiques | Baseline et non-regression volontaire. | Borne aux tests, fixtures et evidence. |
| adapters legacy nommes | champs legacy autorises | Compatibilite transitoire documentee. | Temporary; exit condition: story de suppression dediee. |

Validation rule:

- Toute nouvelle allowlist doit contenir chemin, champ autorise, raison et sortie ou decision de permanence.

## 4f. Contract Shape

- Contract type:
  - tests d'architecture Python;
  - documentation markdown;
  - allowlist locale typée ou constante de test;
  - aucune nouvelle API HTTP.
- Required functions/classes:
  - `test_structural_runtime_does_not_expose_interpretive_fields`;
  - `test_interpretive_adapters_do_not_recalculate_structural_facts`;
  - test de documentation mentionnant `structural runtime`, `interpretive runtime`, `public projection` et `legacy projection`;
  - test de contrat referentiel structurel sans champs interpretatifs obligatoires.

Fields:

- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `interpretive_weight`;
- `meaning`;
- `narrative`;
- `prompt`;
- `llm`;
- `OpenAI`;
- `AIEngineAdapter`.

Required fields:

- structural zone path;
- forbidden token;
- allowlist path;
- allowlist field;
- allowlist reason;
- expiry or permanence decision;
- recalculation call symbol;
- documentation layer term.

Required structural fields:

- faits calculatoires;
- identifiants runtime;
- positions, objets, orbes, angles, forces techniques, dignites, dominance et conditions factuelles.

Forbidden structural fields:

- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `interpretive_weight`;
- `meaning`;
- `narrative`;
- `prompt`;
- `llm`;
- `OpenAI`;
- `AIEngineAdapter`.

Allowed interpretive fields:

- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `interpretive_weight`;
- axes semantiques;
- sources de profil.

Optional fields:

- source story id;
- legacy exit story id;
- evidence artifact path;
- migration note.

- Required output surfaces:
  - tests d'architecture stables;
  - documentation runtime alignee;
  - allowlist locale minimale;
  - evidence persistante.
- Required behavior:
  - structurel: calculer et exposer des faits;
  - interpretatif: enrichir depuis les faits sans recalcul structurel;
  - public: projeter sans devenir source metier;
  - legacy: rester nomme, justifie et borne.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-231.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | zones runtime implicites | zone list structurelle | architecture tests | boundary tests | chemins explicites | scan global bruyant |
| 2 | champs interpretatifs disperses | interdiction structurelle | calculateurs/builders | AST guard | zero hit hors allowlist | champ structurel detecte |
| 3 | adapters ambigus | adapters projection/enrichissement | interpretation adapters | recalcul guard | no calculator call | appel calculateur detecte |
| 4 | docs partielles | matrice runtime | docs architecture | doc test | termes obligatoires | couche manquante |
| 5 | reference hybride | vues separees | repository contracts | contract test | no required valence | champ force |
| 6 | allowlists informelles | registre local borne | tests architecture | allowlist test | raison + sortie | allowlist non justifiee |
| 7 | preuve manuelle API | `app.routes` et `app.openapi()` | aucun public | TestClient smoke | zero public delta | route/schema modifie |

Completion rule: chaque batch conserve les sorties publiques, les scores, les orbes, la doctrine, `pytest`, `app.routes` et `app.openapi()`.

## 4h. Reintroduction Guard

- Guard target:
  - aucun signal interpretatif dans calculators, runtime contracts, builders, graph nodes structurels, dominance, dignities, fixed stars ou conditions structurelles;
  - aucun appel de calculateur structurel depuis un adapter interpretatif;
  - aucune projection publique ne devient source metier;
  - aucune vue de referentiel structurel n'oblige des champs interpretatifs;
  - aucune modification volontaire de `app.routes`, `app.openapi()` ou payload public;
  - aucun changement DB, migration, frontend, prompt, score ou feature flag permanent.
- Guard mechanism:
  - tests d'architecture AST sur chemins structurels explicites;
  - scan cible des tokens interdits avec allowlist locale;
  - test AST des appels de recalcul interdits dans adapters interpretatifs;
  - doc test des quatre couches runtime/projection;
  - test ou import cible du contrat de referentiel structurel;
  - preuve OpenAPI par `app.routes`, `app.openapi()` et `TestClient`.
- Guard owner:
  - `backend/tests/architecture/test_astrology_runtime_boundary.py`;
  - `backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - `backend/tests/architecture/test_chart_interpretation_input_boundary.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`;
  - chemin complet `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - chemin complet `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `evidence/validation.md` | Conserver tests, lint et scans CS-231. |
| Boundary evidence | `evidence/runtime-boundary.md` | Prouver separation structural/interpretive. |
| API neutrality evidence | `evidence/openapi-routes.md` | Conserver routes, OpenAPI et TestClient. |

## 5. Current State Evidence

- Le brief indique que les tests d'architecture existants couvrent deja surfaces legacy, branches par `object_type`, builders specialises et input interpretatif.
- Le brief indique qu'il manque une garde explicite `structural runtime` versus `interpretive runtime`.
- CS-229 a defini les contrats structural runtime, interpretive runtime, public projection et legacy projection.
- CS-230 migre les aspects vers structurel et hints, mais la frontiere doit devenir durable.
- Evidence 1: `_story_briefs/cs-231-runtime-boundary-guardrails-structural-vs-interpretive.md` - demande guardrails d'architecture.
- Evidence 2: `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md` - fournit les couches cibles.
- Evidence 3: `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/00-story.md` - fournit la migration adjacente.
- Evidence 4: `backend` existe dans l'arborescence courante.
- Evidence 5: `docs/architecture/astrology-runtime-surfaces.md` existe.
- Evidence 6: `backend/tests/architecture` existe.
- Evidence 7: `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` existe.
- Evidence 8: `.agents/skills/condamad-story-writer/scripts/condamad_story_lint.py` existe.
- Evidence 9: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` sont absents.

## 6. Target State

- Un test d'architecture echoue si un token interpretatif revient dans une zone structurelle non allowlistee.
- Un test d'architecture echoue si un adapter interpretatif appelle un calculateur structurel.
- La documentation contient la matrice `structural runtime`, `interpretive runtime`, `public projection` et `legacy projection`.
- Les chemins autorises pour valence, energy type et poids interpretatif sont documentes.
- Les allowlists nomment chemin, champ, raison et sortie ou decision de permanence.
- Les tests ignorent les fixtures et tests historiques par chemins explicites.
- Les contrats de referentiel consommes par les calculateurs structurels ne forcent pas les champs interpretatifs.
- Les preuves `app.routes`, `app.openapi()`, `pytest` et `TestClient` montrent la neutralite API.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- runtime-contracts: yes;
- astrology structural calculators: yes;
- interpretation adapters: yes;
- public projection: limited;
- prediction boundary: limited;
- API: no public delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-098 | local | Les raisons de force d'aspect restent techniques et sans dependance prediction. |
| RG-099 | local | La projection publique conserve les champs historiques depuis runtime canonique ou projection dediee. |
| RG-100 | local | L'assemblage interpretatif reste owner des profils et ne met pas de LLM dans le domaine astrology. |
| RG-101 | local | Dominance et inter-chart reutilisent les referentiels existants sans duplication produit. |
| RG-102 | local | La couche semantique reste separee du renderer editorial, des appels LLM et de prediction. |
| RG-145 | local | Les calculateurs d'aspects restent sur chart objects et ne reviennent pas aux collections legacy. |

Non-applicable examples:

- DB/migration guardrails: hors scope, aucune table ni migration Alembic n'est modifiee.
- Frontend/style/build guardrails: hors scope, aucun fichier React, CSS ou build n'est touche.
- Auth/i18n guardrails: hors scope, aucune authentification ou localisation n'est modifiee.

Registry gap:

- Aucun guardrail global dedie a la frontiere runtime structurel versus runtime interpretatif n'existe encore.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | Bloque les champs interpretatifs dans les zones structurelles. | `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC2 | Bloque le recalcul structurel depuis les adapters interpretatifs. | `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC3 | Les entrees d'allowlist utilisent le format complet. | `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC4 | La documentation contient la matrice des couches. | `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC5 | Les fixtures historiques sont exclues par chemins explicites. | `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC6 | Les contrats de referentiel structurel ne forcent pas les champs interpretatifs. | `test_astrology_runtime_boundary.py`; runtime pytest. |
| AC7 | Les futurs calculateurs restent couverts. | `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC8 | Aucun delta API public volontaire n'est introduit. | `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`. |

## 8. Implementation Tasks

- [x] Task: lire les tests d'architecture runtime existants et la documentation runtime surfaces. (AC: AC1, AC4)
- [x] Task: definir les chemins structurels scannes et les chemins interpretatifs autorises. (AC: AC1, AC2, AC7)
- [x] Task: creer l'allowlist locale avec chemin, champ, raison et sortie ou permanence. (AC: AC3)
- [x] Task: ajouter `test_structural_runtime_does_not_expose_interpretive_fields`. (AC: AC1, AC5, AC7)
- [x] Task: ajouter `test_interpretive_adapters_do_not_recalculate_structural_facts`. (AC: AC2)
- [x] Task: ajouter le test de documentation des quatre couches runtime/projection. (AC: AC4)
- [x] Task: ajouter le test de contrat referentiel structurel sans champs interpretatifs forces. (AC: AC6)
- [x] Task: verifier que les fixtures, tests legacy et evidence sont exclus par chemins explicites. (AC: AC5)
- [x] Task: mettre a jour `docs/architecture/astrology-runtime-surfaces.md` avec la matrice et les chemins autorises. (AC: AC4)
- [x] Task: collecter l'evidence `AST guard`, scans cibles, `app.routes`, `app.openapi()` et `TestClient`. (AC: AC1, AC2, AC8)
- [x] Task: conserver les resultats finaux dans les artefacts CS-231. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser les tests d'architecture existants avant de creer un nouveau helper.
- Reutiliser les helpers de scan AST existants dans `backend/tests/architecture` quand ils existent.
- Reutiliser `docs/architecture/astrology-runtime-surfaces.md` comme documentation canonique.
- Reutiliser les contrats CS-229 et CS-230 pour nommer les couches.
- Ne pas creer un second registre global de guardrails.
- Ne pas dupliquer les listes de chemins dans plusieurs fichiers sans helper local commun.
- Ne pas scanner les fixtures par defaut.
- Ne pas ajouter de dependance externe.

## 10. No Legacy / Forbidden Paths

- Ne pas modifier le frontend.
- Ne pas ajouter de migration Alembic.
- Ne pas changer de route FastAPI, schema public, serializer public ou OpenAPI.
- Ne pas ajouter de dependance externe.
- Ne pas ajouter de compatibility layer non borne.
- Ne pas creer de legacy adapter non nomme dans l'allowlist.
- Ne pas changer les scores, orbes, profils, dominance, dignites, conditions, fixed stars ou doctrine astrologique.
- Ne pas supprimer les champs publics `interpretive_valence` et `energy_type`.
- Ne pas modifier les prompts ou providers LLM.
- Ne pas ajouter de fallback silencieux.
- Ne pas scanner tout le depot dans le guard.
- Ne pas bloquer globalement le domaine prediction hors contrat dedie.
- Ne pas autoriser une allowlist sans raison et sortie ou permanence.
- Ne pas placer `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` dans un contrat structurel.
- Ne pas placer `meaning`, `narrative`, `prompt`, `llm`, `OpenAI` ou `AIEngineAdapter` dans une zone structurelle.
- Ne pas appeler un calculateur structurel depuis un adapter interpretatif.

## 11. Generated Contract Check

- Capture before:
  - `app.routes`;
  - `app.openapi()`;
  - un smoke `TestClient` sur OpenAPI;
  - un endpoint natal public couvert par les tests existants.
- Capture after:
  - memes preuves.
- Expected result:
  - aucun endpoint, method, status code, schema public ou cle JSON publique ne change volontairement.

## 12. Files to Inspect First

- `backend/tests/architecture`.
- `backend/tests/architecture/test_aspect_runtime_boundary.py`.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- `docs/architecture/astrology-runtime-surfaces.md`.
- `backend/app/domain/astrology/runtime`.
- `backend/app/domain/astrology/calculators`.
- `backend/app/domain/astrology/builders`.
- `backend/app/domain/astrology/dominance`.
- `backend/app/domain/astrology/fixed_stars`.
- `backend/app/domain/astrology/dignities`.
- `backend/app/domain/astrology/planetary_conditions`.
- `backend/app/domain/astrology/advanced_conditions`.
- `backend/app/domain/astrology/interpretation`.
- `backend/app/domain/astrology/interpretation_adapters`.
- `backend/app/services/chart/json_builder.py`.
- `backend/app/domain/prediction`.
- `backend/app/services/prediction`.
- `backend/app/domain/astrology/runtime/runtime_reference.py`.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`.
- `backend/app/infra/db/repositories/reference_repository.py`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102|RG-145`.

## 13. Expected Files to Modify

Likely files:

- `docs/architecture/astrology-runtime-surfaces.md`.
- `backend/tests/architecture/test_astrology_runtime_boundary.py`.
- `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/evidence/validation.md`.
- `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/evidence/runtime-boundary.md`.
- `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/evidence/openapi-routes.md`.

Likely tests:

- `backend/tests/architecture/test_astrology_runtime_boundary.py`.
- `backend/tests/architecture/test_aspect_runtime_boundary.py`.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.

Files not expected to change:

- `frontend/src`.
- `backend/alembic`.
- `backend/app/api`.
- prompt templates and LLM providers.
- DB models, seeds and migrations.

## 14. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 15. Validation Plan

Run all Python commands from repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted tests:

```powershell
pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py
pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py
pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run anti-regression scans:

```powershell
rg -n "default_valence|interpretive_valence|energy_type|interpretive_weight|meaning|narrative|prompt|llm|OpenAI|AIEngineAdapter" `
  backend/app/domain/astrology/calculators backend/app/domain/astrology/runtime backend/app/domain/astrology/builders `
  backend/app/domain/astrology/dominance backend/app/domain/astrology/fixed_stars backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/planetary_conditions backend/app/domain/astrology/advanced_conditions -g "*.py"
rg -n `
  -e "calculate_major_aspects|calculate_interchart_aspects|resolve_orb" `
  -e "PlanetDominanceEngine\\.calculate|FixedStarConjunctionCalculator" `
  -e "EssentialDignityCalculator|AccidentalDignityCalculator" `
  backend/app/domain/astrology/interpretation backend/app/domain/astrology/interpretation_adapters -g "*.py"
git diff -- backend/app/api backend/alembic frontend/src
```

Run API neutrality proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

The dedicated API neutrality evidence must name `app.routes`, `app.openapi()` and `TestClient`.

## 16. Regression Risks

- Un test trop large peut bloquer prediction, fixtures ou projections publiques legitimes.
- Une allowlist trop large peut masquer une vraie derive structurelle.
- Un adapter interpretatif peut rappeler un calculateur structurel par import indirect.
- Un nouveau calculateur peut apparaitre hors chemins scannes.
- La documentation peut diverger de la matrice testee.
- Un mapper de referentiel peut continuer a exposer une vue hybride obligatoire aux calculateurs.

## 17. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only CS-231.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Implementer le plus petit delta coherent.
- Garder les commentaires globaux et docstrings en francais dans les nouveaux fichiers applicatifs.
- Ne pas utiliser de style inline, CSS ou frontend: aucun fichier frontend n'est attendu.
- Ne pas creer de `requirements.txt`.
- Executer les validations apres activation du venv.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in story evidence.
- Do not preserve legacy behavior through an unbounded fallback, shim or compatibility layer.
- Conserver dans l'evidence les commandes lancees, les resultats de tests, les scans et la preuve `app.routes` / `app.openapi()`.

## 18. CS-231 Final Evidence Template

```markdown
## CS-231 Final Evidence

### Structural Runtime Guard
- Structural zones are enumerated explicitly.
- AST guard blocks interpretive tokens outside allowlist.
- Future calculators are covered by the same path rules.

### Interpretive Adapter Guard
- Interpretive adapters do not call structural calculators.
- Adapters project or enrich existing facts only.

### Documentation
- structural runtime, interpretive runtime, public projection and legacy projection are documented.
- Allowed paths for valence, energy type and interpretive weight are listed.

### Compatibility
- Public JSON remains stable.
- Prediction remains governed by dedicated contracts.
- app.routes, app.openapi() and TestClient are captured.

### Commands
- ruff format backend
- ruff check backend
- pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py
- pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

## 19. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-231-runtime-boundary-guardrails-structural-vs-interpretive.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the brief, adjacent CS-229/CS-230 structure and validator diagnostics.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted ID search only.
- No regression guardrail registry update was made.
- Story validation result after correction cycle: PASS.
- Strict lint result after correction cycle: PASS.

## 20. References

- Source brief: `_story_briefs/cs-231-runtime-boundary-guardrails-structural-vs-interpretive.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-098`, `RG-099`, `RG-100`, `RG-101`, `RG-102`, `RG-145`).
- Previous story: `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/00-story.md`.
