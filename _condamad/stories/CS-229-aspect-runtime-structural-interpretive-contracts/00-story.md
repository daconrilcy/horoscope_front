# Story CS-229 aspect-runtime-structural-interpretive-contracts: Aspect Runtime Structural / Interpretive Contracts
Status: done

## 1. Objective

Formaliser la frontiere entre runtime structurel d'aspects, hints interpretatifs d'aspects, projection publique et projection legacy.
La story cree ou prepare les contrats cibles sans casser le JSON public natal, sans migrer tous les consommateurs et sans changer la doctrine astrologique.

## 2. Trigger / Source

- Source type: architecture-runtime-contracts.
- Source reference: `_story_briefs/cs-229-aspect-runtime-structural-interpretive-contracts.md`.
- Reason for change: `AspectRuntimeData` melange faits calculatoires et indices interpretatifs, ce qui rend la responsabilite des calculateurs ambigue.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: la story definit des contrats backend-domain et une documentation courte, sans route, frontend, DB, prompt ou migration globale.

## References

- `_story_briefs/cs-229-aspect-runtime-structural-interpretive-contracts.md`.
- `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/00-story.md`.
- `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/00-story.md`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102`.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology`.
- In scope:
  - documenter les couches `structural runtime`, `interpretive runtime`, `public projection` et `legacy projection`;
  - creer ou preparer `AspectStructuralDefinitionRuntimeData`;
  - creer ou preparer `AspectInterpretiveProfileRuntimeData`;
  - creer ou preparer `AspectStructuralRuntimeData`;
  - creer ou preparer `AspectInterpretiveHintsRuntimeData`;
  - borner les modifiers structurels d'aspects;
  - documenter le statut de `default_valence`, `interpretive_valence`, `energy_type` et `interpretive_weight`;
  - clarifier `AspectStrengthRuntimeData`, la dominance d'aspect et les modifiers factuels;
  - clarifier les usages prediction autorises via contrats prediction ou hints interpretatifs;
  - ajouter tests unitaires et guards d'architecture;
  - verifier l'absence de delta API public avec `app.routes`, `app.openapi()` et `TestClient`.
- Out of scope:
  - supprimer immediatement `AspectRuntimeData.interpretation`;
  - casser le JSON public natal;
  - modifier la doctrine astrologique, les valeurs de profils, les scores ou les prompts;
  - modifier le frontend;
  - modifier les tables DB, seeds ou migrations;
  - migrer tous les consommateurs d'un coup;
  - changer les sorties prediction.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas convertir les hints interpretatifs en texte narratif;
  - ne pas introduire une seconde logique de calcul d'aspects.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la story installe une frontiere de contrats backend-domain avant migration progressive des consommateurs d'aspects.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: nouveaux contrats structures pour definition, runtime structurel, profil interpretatif et hints interpretatifs;
  - autorise: alias ou ponts temporaires bornes uniquement pour conserver les consommateurs existants;
  - autorise: documentation d'architecture `Aspect runtime layers`;
  - autorise: tests qui prouvent que les champs interpretatifs ne reviennent pas dans les contrats structurels;
  - interdit: changement volontaire de route, OpenAPI, JSON public, DB, frontend, scores, doctrine, prompts ou dependance externe.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'implementation touche une sortie publique, une migration DB, un prompt, le frontend ou une suppression de champ legacy public.
- Additional validation rules:
  - les calculateurs structurels recoivent uniquement une definition structurelle d'aspect;
  - les valences, energy types, axes semantiques et poids interpretatifs sont produits par resolver ou adapter dedie;
  - `AspectStructuralRuntimeData` ne contient aucun champ de valence, energy type, prompt, meaning, narrative ou theme editorial;
  - `AspectInterpretiveHintsRuntimeData` reste un contrat de hints types et sources, pas un texte narratif;
  - `AspectStrengthRuntimeData` reste une force technique, sans lecture editoriale;
  - la dominance d'aspect reste chart-level et ne devient pas owner de valence;
  - les modifiers structurels portent uniquement type, source, intensite, raison et cible factuelle;
  - les usages prediction de valence passent par contrats prediction ou hints interpretatifs, jamais via runtime structurel;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta API volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le runtime structurel d'aspects devient la source calculatoire interne. |
| Baseline Snapshot | yes | Les champs hybrides actuels et leurs consommateurs doivent etre connus avant migration. |
| Ownership Routing | yes | Calculateurs, resolver interpretatif, prediction, projection publique et legacy ont des owners distincts. |
| Allowlist Exception | yes | Les champs interpretatifs legacy conserves doivent etre bornes et rattaches a une sortie de transition. |
| Contract Shape | yes | Les nouveaux contrats doivent lister champs autorises et champs interdits. |
| Batch Migration | yes | Contrats, docs, tests, ponts legacy et preuves API doivent etre livres par lots controlables. |
| Reintroduction Guard | yes | Les guards bloquent le retour de valence, energy type, prompt et narration dans les modules structurels. |
| Persistent Evidence | yes | Tests, scans, OpenAPI et decisions de transition doivent etre conserves dans le dossier CS-229. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectStructuralDefinitionRuntimeData`;
  - `AspectStructuralRuntimeData`;
  - `AspectStrengthRuntimeData`;
  - `AspectStructuralModifierRuntimeData`;
  - `AspectInterpretiveProfileRuntimeData`;
  - `AspectInterpretiveHintsRuntimeData`;
  - `docs/architecture/astrology-runtime-surfaces.md`.
- Runtime/domain artifacts:
  - contrats Python types;
  - resolver ou adapter interpretatif dedie;
  - documentation `Aspect runtime layers`;
  - tests unitaires des contrats;
  - tests d'architecture anti-retour;
  - preuves `app.routes`, `app.openapi()` et `TestClient`.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_aspect_modifiers.py`;
  - `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni la validation runtime des contrats, ni la compatibilite publique, ni le routage des hints interpretatifs.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/aspect_runtime_data.py`;
  - `Get-Content backend/app/domain/astrology/builders/aspect_runtime_builder.py`;
  - `Get-Content backend/app/domain/astrology/interpretation/aspects/contracts.py`;
  - recherche ciblee `AspectRuntimeData|AspectInterpretationRuntimeData|AspectStrengthRuntimeData`;
  - recherche ciblee `default_valence|interpretive_valence|energy_type|interpretive_weight|meaning|narrative|prompt|llm`;
  - `Select-String "RG-098|RG-099|RG-100|RG-101|RG-102" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres implementation;
  - tests CS-229 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend, prompts et prediction.
- Expected invariant:
  - les aspects publics restent disponibles;
  - `AspectRuntimeData.interpretation` peut rester comme legacy transition borne;
  - aucun endpoint public ne change volontairement;
  - les scores, orbes, dominance, modifiers factuels et profils existants ne changent pas.
- Allowed differences:
  - nouveaux contrats structurels et interpretatifs;
  - nouveau resolver ou adapter interpretatif borne;
  - tests d'architecture et documentation;
  - Registry gap: un invariant global dedie a la separation aspect structural/interpretive pourra etre ajoute ulterieurement.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Definition structurelle d'aspect | `AspectStructuralDefinitionRuntimeData` | profil interpretatif ou route API |
| Profil interpretatif d'aspect | `AspectInterpretiveProfileRuntimeData` | calculateur structurel |
| Runtime structurel d'aspect | `AspectStructuralRuntimeData` | builder narratif, prompt ou prediction directe |
| Hints interpretatifs | resolver ou adapter interpretatif | calculateur d'orbe ou force technique |
| Projection publique | chart json builder ou adapter public | runtime structurel interne |
| Projection legacy | adapter allowliste | nouveau calculateur |
| Prediction | contrats prediction ou hints interpretatifs | lecture directe du runtime structurel |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `AspectRuntimeData.interpretation` | legacy projection field | Compatibilite des consommateurs existants pendant CS-229. | Temporary; exit condition: CS-230 migrates consumers. |
| adapters publics existants | champs historiques d'aspects | Contrat API stable conserve. | Permanent pour cette story. |
| prediction consumers existants | valence ou energy type | Usage legitime via hints ou contrat prediction. | Temporary; exit condition: explicit hints/profile path. |
| tests et fixtures | champs hybrides historiques | Baseline et non-regression. | Borne aux tests et evidence. |

Validation rule:

- Toute nouvelle lecture de `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` depuis un calculateur structurel bloque CS-229.

## 4f. Contract Shape

- Contract type:
  - dataclasses ou Pydantic models deja coherents avec les contrats runtime existants;
  - resolver ou adapter interpretatif explicite;
  - tests unitaires et d'architecture;
  - aucune nouvelle API HTTP.
- Required functions/classes:
  - `AspectStructuralDefinitionRuntimeData`;
  - `AspectInterpretiveProfileRuntimeData`;
  - `AspectStructuralRuntimeData`;
  - `AspectInterpretiveHintsRuntimeData`;
  - `AspectStructuralModifierRuntimeData`;
  - resolver ou adapter qui assemble les hints depuis runtime structurel et profil interpretatif.
Fields:

- `code`;
- `name`;
- `angle`;
- `family`;
- `is_enabled`;
- `is_major`;
- `is_minor`;
- `default_orb_deg`;
- `system_code`;
- `legacy_orb_fields`;
- `aspect`;
- `participants`;
- `orb`;
- `metadata`;
- `strength`;
- `phase`;
- `modifiers`;
- `aspect_code`;
- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `semantic_axes`;
- `growth_axes`;
- `shadow_axes`;
- `relationship_axes`;
- `interpretive_weight`;
- `source_profile_code`;
- `source_codes`.

Required fields:

- `aspect`;
- `participants`;
- `orb`;
- `metadata`;
- `strength`;
- `modifiers`;
- `aspect_code`;
- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `source_codes`.

Required structural fields:

- `aspect`;
- `participants`;
- `orb`;
- `metadata`;
- `strength`;
- `modifiers`.

Required interpretive hint fields:

- `aspect_code`;
- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `semantic_axes`;
- `growth_axes`;
- `shadow_axes`;
- `relationship_axes`;
- `source_codes`.

Optional fields:

- `phase`;
- `interpretive_weight`;
- `source_profile_code`;
- `reference_version`;
- `legacy_orb_fields`.

- Required output surfaces:
  - structural runtime;
  - interpretive hints;
  - public aspect projection unchanged;
  - legacy aspect projection unchanged and bounded.
- Required behavior:
  - structurel: geometrie, participants, orbe, force technique, phase et modifiers factuels;
  - interpretatif: valence, energy type, axes semantiques, poids et sources;
  - public: payload stable;
  - legacy: compatibilite historique nommee.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-229.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | contrat aspect hybride | contrats separes | tests unitaires | contract tests | champs separes | champ interpretatif structurel |
| 2 | referentiel mixte | definition + profil | repository/adapters | repository tests | vues distinctes | calculateur lit profil |
| 3 | modifier ambigu | modifier structurel | builder aspects | modifier tests | no weight in modifier | poids non borne |
| 4 | hints implicites | resolver interpretatif | interpretation input | hint tests | owner unique | texte narratif produit |
| 5 | doc dispersee | runtime surfaces doc | aucun public | doc tests | couche explicite | couche manquante |
| 6 | preuve manuelle API | `app.routes` et `app.openapi()` | aucun public | TestClient smoke | zero public delta | route/schema modifie |

Completion rule: chaque batch conserve les sorties publiques, les scores, les orbes, la doctrine, `pytest`, `app.routes` et `app.openapi()`.

## 4h. Reintroduction Guard

- Guard target:
  - aucun champ `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` dans les contrats structurels;
  - aucun champ `meaning`, `narrative`, `prompt` ou `llm` dans les modules structurels d'aspects;
  - aucun poids interpretatif dans les modifiers structurels;
  - aucun calculateur structurel ne depend du profil interpretatif;
  - aucune modification volontaire de `app.routes`, `app.openapi()` ou payload public;
  - aucun changement DB, migration, frontend, prompt ou feature flag permanent.
- Guard mechanism:
  - tests unitaires des contrats structurels et interpretatifs;
  - tests de resolver des hints interpretatifs;
  - tests d'architecture AST sur les modules structurels d'aspects;
  - scans cibles des termes interdits dans les modules structurels;
  - preuve OpenAPI par `app.routes`, `app.openapi()` et `TestClient`.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py`;
  - `backend/tests/unit/domain/astrology/test_aspect_modifiers.py`;
  - `backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py`;
  - chemin complet `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/evidence/validation.md` | Conserver tests, lint et scans CS-229. |
| API neutrality evidence | `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/evidence/openapi-routes.md` | Conserver routes, OpenAPI et TestClient. |
| Aspect boundary proof | `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/evidence/aspect-runtime-boundary.md` | Prouver la frontiere aspect. |

## 5. Current State Evidence

- Le brief indique que `AspectRuntimeData` porte a la fois identite, participants, orbe, force, modifiers factuels et bloc `interpretation`.
- Le brief cite `default_valence`, `interpretive_valence`, `energy_type` et `interpretive_weight` comme champs a sortir du runtime structurel.
- CS-217 a CS-228 ont deja canonicalise `chart_objects`, aspects, dignites, dominance, fixed stars et calculation graph.
- Evidence 1: `_story_briefs/cs-229-aspect-runtime-structural-interpretive-contracts.md` - demande contrats avant migration consommateurs.
- Evidence 2: `_condamad/stories/CS-224-legacy-runtime-surface-cleanup-guardrails/00-story.md` - documente la discipline runtime/legacy.
- Evidence 3: `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/00-story.md` - conserve neutralite API pendant migration runtime.
- Evidence 4: `backend` existe dans l'arborescence courante.
- Evidence 5: `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` existe.
- Evidence 6: `.agents/skills/condamad-story-writer/scripts/condamad_story_lint.py` existe.
- Evidence 7: `.agents/skills/condamad-story-writer/SKILL.md` est absent; la story suit le brief, les stories voisines et les diagnostics.

## 6. Target State

- `docs/architecture/astrology-runtime-surfaces.md` contient une section `Aspect runtime layers`.
- Les termes `structural runtime`, `interpretive runtime`, `public projection` et `legacy projection` sont definis.
- `AspectStructuralRuntimeData` existe ou est prepare comme contrat structurel.
- `AspectInterpretiveHintsRuntimeData` existe ou est prepare comme contrat de hints.
- Le referentiel d'aspects distingue definition structurelle et profil interpretatif.
- `AspectStrengthRuntimeData` reste une force technique.
- Les modifiers structurels ne portent pas de poids interpretatif hors transition legacy bornee.
- Le domaine prediction consomme valence et energy type via contrat prediction ou hints interpretatifs.
- Les tests bloquent le retour des champs interpretatifs dans les modules structurels cibles.
- Le JSON public natal et les routes FastAPI restent inchanges.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- runtime-contracts: yes;
- astrology aspects: yes;
- interpretation hints: yes;
- prediction boundary: limited;
- API: no public delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-098 | local | `AspectStrengthRuntimeData` reste une force technique; les raisons de force ne deviennent pas des lectures interpretatives. |
| RG-099 | local | La projection publique des aspects reste alimentee par runtime canonique, sans recomposition locale ni changement de payload. |
| RG-100 | local | L'assemblage interpretatif reste owner des profils et ne produit pas de prompt ou texte final dans le runtime structurel. |
| RG-101 | local | Dominance et inter-chart reutilisent le runtime d'aspects et les referentiels existants, sans duplication. |
| RG-102 | local | La couche semantique des aspects reste separee du renderer editorial et des appels LLM. |

Non-applicable examples:

- DB/migration guardrails: hors scope, aucune table ni migration Alembic n'est modifiee.
- Frontend/style/build guardrails: hors scope, aucun fichier React, CSS ou build n'est touche.
- Auth/i18n guardrails: hors scope, aucune authentification ou localisation n'est modifiee.

Registry gap:

- Aucun guardrail global dedie a `AspectStructuralRuntimeData` versus `AspectInterpretiveHintsRuntimeData` n'existe encore.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | La documentation definit les quatre couches runtime/projection. | `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`; doc scan. |
| AC2 | Les contrats dedies d'aspects existent ou sont prepares. | `test_aspect_runtime_contracts.py`. |
| AC3 | Le referentiel d'aspects isole la definition structurelle du profil interpretatif. | `test_aspect_runtime_contracts.py`. |
| AC4 | Aucun nouveau champ interpretatif n'est ajoute a un contrat structurel. | `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`; AST guard. |
| AC5 | Les modifiers structurels ne portent pas de poids interpretatif non borne. | `pytest -q backend/tests/unit/domain/astrology/test_aspect_modifiers.py`; AST guard. |
| AC6 | Les tests bloquent le retour des termes interdits dans les modules structurels. | `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`; AST guard. |
| AC7 | `AspectStrengthRuntimeData` reste technique. | `pytest -q backend/tests/unit/domain/astrology/test_aspect_strength.py`; AST guard. |
| AC8 | La dominance d'aspect ne devient pas owner de valence. | `pytest -q backend/tests/unit/domain/astrology/test_dominant_aspects.py`; AST guard. |
| AC9 | Les consumers prediction gardent valence via hints ou contrat prediction. | `pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py`. |
| AC10 | Les hints interpretatifs acceptent des sources. | `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py`; runtime pytest. |
| AC11 | Les calculateurs structurels ne recoivent pas le profil interpretatif. | `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`; AST guard. |
| AC12 | Aucun prompt n'est produit dans le runtime structurel. | `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`; scan cible. |
| AC13 | Les sorties publiques d'aspects restent compatibles. | `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; `app.routes`; `app.openapi()`. |
| AC14 | Aucun changement DB n'est introduit. | `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py`; diff adjacent. |
| AC15 | L'evidence finale CS-229 est persistee. | from story dir, `rg -n "CS-229 Final Evidence" evidence/validation.md`. |

## 8. Implementation Tasks

- [ ] Task: lire le runtime d'aspects actuel, le builder, les modifiers, la force et les profils interpretatifs. (AC: AC1, AC2, AC3)
- [ ] Task: mettre a jour `docs/architecture/astrology-runtime-surfaces.md` avec `Aspect runtime layers`. (AC: AC1)
- [ ] Task: creer ou preparer `AspectStructuralDefinitionRuntimeData` avec commentaire global et docstrings en francais. (AC: AC2, AC3)
- [ ] Task: creer ou preparer `AspectInterpretiveProfileRuntimeData` avec commentaire global et docstrings en francais. (AC: AC2, AC3)
- [ ] Task: creer ou preparer `AspectStructuralRuntimeData` sans champs interpretatifs. (AC: AC2, AC4, AC11)
- [ ] Task: creer ou preparer `AspectInterpretiveHintsRuntimeData` avec axes, sources et poids optionnel. (AC: AC2, AC10)
- [ ] Task: borner `AspectStructuralModifierRuntimeData` et documenter tout poids legacy restant. (AC: AC5)
- [ ] Task: isoler ou preparer le resolver de hints interpretatifs depuis runtime structurel et profil interpretatif. (AC: AC9, AC10, AC11)
- [ ] Task: verifier que `AspectStrengthRuntimeData` reste une force technique. (AC: AC7)
- [ ] Task: verifier que la dominance d'aspect reste chart-level sans valence owner. (AC: AC8)
- [ ] Task: ajouter les tests unitaires de contrats structurels et interpretatifs. (AC: AC2, AC3, AC4, AC10)
- [ ] Task: ajouter les tests modifiers et force d'aspects. (AC: AC5, AC7)
- [ ] Task: ajouter l'AST guard des termes interdits dans les modules structurels cibles. (AC: AC4, AC6, AC11, AC12)
- [ ] Task: ajouter la preuve `app.routes`, `app.openapi()` et `TestClient` de neutralite API. (AC: AC13)
- [ ] Task: collecter l'evidence finale dans le dossier CS-229. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser les contrats existants `AspectIdentityRuntimeData`, `AspectParticipantsRuntimeData`, `AspectOrbRuntimeData` et `AspectStrengthRuntimeData`.
- Reutiliser les builders d'aspects existants comme point d'integration, sans recopier le calcul d'orbe ou de force.
- Reutiliser les profils d'aspects existants pour alimenter la vue interpretative.
- Reutiliser les tests d'aspects existants quand leur scope couvre deja le runtime.
- Ne pas creer un second calculateur d'aspects.
- Ne pas dupliquer les referentiels d'aspects dans des constantes locales.
- Ne pas creer de contrat public concurrent au JSON natal actuel.

## 10. No Legacy / Forbidden Paths

- Ne pas modifier le frontend.
- Ne pas ajouter de migration Alembic.
- Ne pas changer de route FastAPI, schema public, serializer public ou OpenAPI.
- Ne pas ajouter de dependance externe.
- Ne pas supprimer `AspectRuntimeData.interpretation` dans CS-229.
- Ne pas ajouter de compatibility wrapper non borne.
- Ne pas ajouter de fallback silencieux.
- Ne pas changer les scores, orbes, profils, dominance ou doctrine astrologique.
- Ne pas produire de prompt, texte narratif, appel LLM ou renderer editorial dans le runtime structurel.
- Ne pas ajouter `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` a un contrat structurel.
- Ne pas placer `interpretive_weight`, `prompt_hint`, `meaning` ou `narrative` dans un modifier structurel.
- Ne pas brancher un calculateur structurel sur un profil interpretatif.
- Ne pas conserver de pont legacy non borne.

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

- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`.
- `backend/app/domain/astrology/runtime/aspect_strength.py`.
- `backend/app/domain/astrology/interpretation/aspects/contracts.py`.
- `backend/app/domain/astrology/interpretation/aspects`.
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`.
- `backend/tests/unit/domain/astrology/test_aspect_modifiers.py`.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102`.

## 13. Expected Files to Modify

Likely files:

- `docs/architecture/astrology-runtime-surfaces.md`.
- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`.
- `backend/app/domain/astrology/interpretation/aspects/contracts.py`.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/evidence/validation.md`.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/evidence/openapi-routes.md`.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/evidence/aspect-runtime-boundary.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py`.
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`.
- `backend/tests/unit/domain/astrology/test_aspect_modifiers.py`.
- `backend/tests/unit/domain/astrology/test_aspect_strength.py`.
- `backend/tests/unit/domain/astrology/test_dominant_aspects.py`.
- `backend/tests/architecture/test_aspect_runtime_boundary.py`.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.

Files not expected to change:

- `frontend/src`.
- `backend/alembic`.
- `backend/app/api`.
- `backend/app/infra`.
- prompt templates and LLM providers.

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
pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_contracts.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_modifiers.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_strength.py
pytest -q backend/tests/unit/domain/astrology/test_dominant_aspects.py
pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py
pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run anti-regression scans:

```powershell
rg -n "default_valence|interpretive_valence|energy_type|interpretive_weight|meaning|narrative|prompt|llm" backend/app/domain/astrology/runtime -g "*.py"
rg -n "AspectStructuralRuntimeData|AspectInterpretiveHintsRuntimeData|AspectStructuralDefinitionRuntimeData" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "AspectInterpretiveProfileRuntimeData|AspectInterpretiveHintsRuntimeData" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "AspectRuntimeData\\(|AspectStrengthRuntimeData\\(|AspectStructuralModifierRuntimeData" backend/app/domain/astrology backend/tests -g "*.py"
git diff -- backend/app/api backend/alembic backend/app/infra frontend/src
```

Run API neutrality proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

The dedicated API neutrality evidence must name `app.routes`, `app.openapi()` and `TestClient`.

## 16. Regression Risks

- Un calculateur structurel peut continuer a produire valence ou energy type.
- Un modifier structurel peut conserver un poids interpretatif non borne.
- Un resolver de hints peut devenir un builder narratif.
- Le domaine prediction peut relire le runtime structurel hybride au lieu d'un contrat de hints.
- Une projection publique peut changer en renommant trop tot les champs legacy.
- La documentation peut definir la doctrine sans guard deterministe.

## 17. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only CS-229.
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
- Ne pas supprimer le bloc legacy `AspectRuntimeData.interpretation` pendant CS-229.
- Ne pas migrer tous les consommateurs sans story de suite.
- Conserver dans l'evidence les commandes lancees, les resultats de tests, les scans et la preuve `app.routes` / `app.openapi()`.

## 18. CS-229 Final Evidence Template

```markdown
## CS-229 Final Evidence

### Aspect Runtime Layers
- Structural runtime, interpretive runtime, public projection and legacy projection are documented.
- Aspect runtime layers are listed in docs/architecture/astrology-runtime-surfaces.md.

### Contracts
- AspectStructuralRuntimeData contains only structural facts.
- AspectInterpretiveHintsRuntimeData contains typed sourced hints.
- AspectStructuralDefinitionRuntimeData and AspectInterpretiveProfileRuntimeData are separated.

### Boundaries
- Structural calculators do not consume interpretive profiles.
- Modifiers do not carry non-bounded interpretive weight.
- Prediction uses hints or prediction contracts for valence.

### Compatibility
- No public API or OpenAPI delta.
- Existing public aspect fields remain stable.
- app.routes, app.openapi() and TestClient are captured.

### Guardrails
- AST guard blocks interpretive terms in structural modules.
- Scans cover valence, energy_type, meaning, narrative, prompt and llm.

### Commands
- ruff format backend
- ruff check backend
- pytest -q backend/tests
- targeted aspect runtime tests
```

## 19. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-229-aspect-runtime-structural-interpretive-contracts.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the brief, adjacent CS-224/CS-228 structure and validator diagnostics.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted search only.
- No regression guardrail registry update was made.
- Story validation result after correction cycle: PASS.
- Strict lint result after correction cycle: PASS.

## 20. References

- Source brief: `_story_briefs/cs-229-aspect-runtime-structural-interpretive-contracts.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-098`, `RG-099`, `RG-100`, `RG-101`, `RG-102`).
- Previous story: `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/00-story.md`.
