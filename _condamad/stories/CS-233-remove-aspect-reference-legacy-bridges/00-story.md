# Story CS-233 remove-aspect-reference-legacy-bridges: Remove Aspect Reference Legacy Bridges
Status: done

## 1. Objective

Fermer les bridges temporaires restants entre definition structurelle d'aspect et profil interpretatif.
La story rend les hints interpretatifs obligatoires pour produire les champs publics interpretatifs, sans retirer les cles publiques existantes.

## 2. Trigger / Source

- Source type: architecture-runtime-cleanup.
- Source reference: `_story_briefs/cs-233-remove-aspect-reference-legacy-bridges.md`.
- Reason for change: CS-229 a CS-232 ont separe les contrats, mais plusieurs bridges `Temporary` restent consommables.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` sont absents.
- Source-alignment review: story de suppression backend-domain avec controle chart JSON, architecture et prediction; pas de DB, frontend, auth, i18n, style ou build.

## References

- `_story_briefs/cs-233-remove-aspect-reference-legacy-bridges.md`.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md`.
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/00-story.md`.
- `_condamad/stories/CS-231-runtime-boundary-guardrails-structural-vs-interpretive/00-story.md`.
- `_condamad/stories/CS-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases/00-story.md`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-106|RG-107|RG-145`.

## 3. Domain Boundary

Cette story appartient au domaine astrologie runtime et a la projection publique chart:

- Domain: `backend/app/domain/astrology`.
- Integration surfaces:
  - `backend/app/domain/astrology/runtime/runtime_reference.py`;
  - `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`;
  - `backend/app/domain/astrology/natal_calculation.py`;
  - `backend/app/services/chart/json_builder.py`;
  - `backend/tests/architecture`;
  - `docs/architecture/astrology-runtime-surfaces.md`;
  - `backend/app/domain/prediction` en controle de frontiere limite.
- In scope:
  - supprimer `AspectDefinitionRuntimeData` ou le rendre absent des chemins de calcul natal;
  - separer les vues `AspectReferenceSet` structurelles et interpretatives;
  - migrer `AstrologyRuntimeReferenceMapper` vers ces vues separees;
  - migrer `_aspect_runtime_rules` sans creation de definition legacy;
  - supprimer `_aspect_definition` quand il ne sert plus qu'au bridge legacy;
  - retirer `default_valence`, `interpretive_valence` et `energy_type` de `AspectResult`;
  - supprimer le fallback `json_builder` sur les champs plats d'aspect;
  - nettoyer les allowlists `Temporary` liees aux champs interpretatifs aspectuels;
  - mettre a jour `docs/architecture/astrology-runtime-surfaces.md`;
  - prouver la stabilite publique par `pytest`, `TestClient`, `app.routes` et `app.openapi()`.
- Out of scope:
  - supprimer les tables DB de valence;
  - modifier `astral_aspect_profiles.json`;
  - changer doctrine, orbes, scores prediction ou valeurs de profils;
  - supprimer les champs publics `interpretive_valence` et `energy_type` du JSON natal;
  - changer le frontend sans preuve d'usage direct a adapter;
  - refondre le domaine prediction;
  - ajouter une dependance externe ou un `requirements.txt`;
  - creer un dossier de base sous `backend/`.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas conserver un bridge legacy sous un autre nom;
  - ne pas ajouter de fallback silencieux dans la projection publique;
  - ne pas deplacer des champs hybrides dans un dictionnaire libre;
  - ne pas scanner tout le depot dans les guards.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime des bridges backend-domain et impose des contrats runtime separes avec preuves publiques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: suppression de bridges internes non publics;
  - autorise: remplacement par vues structurelles et interpretatives separees;
  - autorise: erreur de contrat explicite quand un aspect public manque de hints;
  - autorise: nettoyage des allowlists `Temporary` et de la documentation runtime;
  - interdit: suppression des cles publiques `interpretive_valence` et `energy_type`;
  - interdit: changement DB, migration, score, doctrine, prompt, auth, i18n, style, build ou dependance.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une cle publique, un schema OpenAPI, une table DB, un score, un prompt, le frontend ou une dependance doit changer.
- Additional validation rules:
  - `AspectReferenceData` ne force pas `default_valence`, `interpretive_valence` ou `energy_type` avec angle et orbe;
  - `AspectReferenceSet` expose une vue structurelle et une vue interpretative separees;
  - `AspectDefinitionRuntimeData` est supprime ou absent des chemins de calcul natal;
  - `_aspect_runtime_rules` consomme directement les definitions structurelles et profils interpretatifs;
  - `AspectResult` ne porte aucun champ plat interpretatif;
  - `json_builder` produit les champs publics depuis `aspect_interpretive_hints`;
  - absence de hints publies = erreur de contrat explicite ou mode degrade documente, jamais fallback silencieux;
  - prediction conserve `AspectProfileData.default_valence` et `AspectProfileData.energy_type` dans son propre contrat;
  - les allowlists temporaires d'aspects sont supprimees ou bornees avec sortie documentee;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent le delta public autorise.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les definitions structurelles et profils interpretatifs sont les sources canoniques separees. |
| Baseline Snapshot | yes | Les hits legacy doivent etre classes avant suppression. |
| Ownership Routing | yes | Reference, calculateur, resolver de hints, serializer public et prediction ont des owners distincts. |
| Allowlist Exception | yes | Les surfaces conservees doivent etre bornees, nommees et justifiees. |
| Contract Shape | yes | Les champs supprimes, conserves et projetes doivent etre explicites. |
| Batch Migration | yes | Inventaire, migration, suppression, docs et preuves sont livres par lots controlables. |
| Reintroduction Guard | yes | Les tests bloquent le retour des bridges et fallbacks plats. |
| Persistent Evidence | yes | Scans, OpenAPI, tests, docs et decisions d'allowlist doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectReferenceSet.structural_definitions`;
  - `AspectReferenceSet.interpretive_profiles`;
  - `AspectStructuralDefinitionRuntimeData`;
  - `AspectInterpretiveProfileRuntimeData`;
  - `AspectInterpretiveHintsRuntimeData`;
  - `aspect_interpretive_hints` dans `AspectResult`;
  - `json_builder` uniquement comme projection publique.
- Runtime/domain artifacts:
  - inventaire cible des bridges `Temporary`;
  - tests unitaires des contrats d'aspects;
  - tests du resolver de hints;
  - tests du graphe natal;
  - tests de projection publique;
  - tests d'architecture sur allowlists et champs interdits;
  - evidence `app.routes`, `app.openapi()` et `TestClient`.
- Secondary evidence:
  - `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`;
  - `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`;
  - `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `pytest -q backend/app/tests/unit/test_chart_json_builder.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni la compatibilite publique, ni les contrats importables, ni la source effective des champs publics.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - recherche ciblee `AspectDefinitionRuntimeData|_aspect_definition|AspectReferenceData`;
  - recherche ciblee `default_valence|interpretive_valence|energy_type|interpretive_weight`;
  - recherche ciblee `aspect_interpretive_hints|structural_definitions|interpretive_profiles`;
  - lecture ciblee de `docs/architecture/astrology-runtime-surfaces.md`;
  - `Select-String "RG-098|RG-099|RG-106|RG-107|RG-145" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres migration;
  - tests CS-233 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - smoke `TestClient`;
  - recherche frontend ciblee sur `interpretive_valence|energy_type` si une surface publique est touchee;
  - diff adjacent sur DB, migrations, prompts, scores, auth, i18n, style et build.
- Expected invariant:
  - les calculateurs lisent uniquement les definitions structurelles;
  - les resolvers lisent uniquement les profils interpretatifs;
  - les serializers publics lisent les hints explicites;
  - prediction garde ses contrats propres;
  - aucune sortie publique ne disparait.
- Allowed differences:
  - suppression des bridges legacy internes;
  - migration de consommateurs vers vues separees;
  - suppression de fallbacks silencieux;
  - allowlists temporaires reduites;
  - documentation runtime alignee;
  - evidence persistante CS-233;
  - Registry gap: un invariant global dedie a l'extinction finale des bridges aspect reference pourra etre ajoute ulterieurement.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Definition geometrique d'aspect | `AspectStructuralDefinitionRuntimeData` | objet hybride avec valence |
| Profil interpretatif d'aspect | `AspectInterpretiveProfileRuntimeData` | calculateur structurel |
| Graphe natal | `_aspect_runtime_rules` et graph nodes explicites | `_aspect_definition` legacy |
| Resultat d'aspect | `AspectResult` avec hints | champs plats interpretatifs |
| Projection publique | `json_builder` depuis hints | fallback sur champs plats |
| Prediction | contrat prediction dedie | runtime structurel astrology hybride |
| Reference runtime | `AspectReferenceSet` vues separees | `AspectDefinitionRuntimeData` bridge |
| Architecture docs | `docs/architecture/astrology-runtime-surfaces.md` | allowlist Temporary durable |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/domain/prediction` | `AspectProfileData.default_valence`, `energy_type` | Contrat prediction propre. | Permanent selon contrat prediction. |
| `backend/app/services/chart/json_builder.py` | `interpretive_valence`, `energy_type` publics | Cles publiques produites depuis hints. | Permanent pour contrat public. |
| tests et fixtures | donnees historiques d'aspects | Baseline, migration et non-regression. | Borne aux tests, fixtures et evidence. |
| docs historiques | mentions CS-229 a CS-232 | Historique de migration. | Borne aux docs historiques, pas aux contrats actifs. |

Validation rule:

- Toute allowlist restante doit contenir chemin, symbole, raison et sortie ou decision de permanence.

## 4f. Contract Shape

- Contract type:
  - dataclasses runtime Python;
  - graph nodes et use-cases backend-domain;
  - serializer public chart;
  - tests d'architecture AST;
  - documentation markdown;
  - aucune nouvelle API HTTP.

Required surfaces:

- `AspectReferenceSet.structural_definitions`;
- `AspectReferenceSet.interpretive_profiles`;
- `AspectStructuralDefinitionRuntimeData`;
- `AspectInterpretiveProfileRuntimeData`;
- `AspectInterpretiveHintsRuntimeData`;
- `AspectResult.aspect_interpretive_hints`;
- `json_builder` projection publique;
- tests d'architecture anti-retour.

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

Forbidden structural fields:

- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `interpretive_weight`;
- `AspectDefinitionRuntimeData`;
- `_aspect_definition`;
- fallback plat dans `json_builder`;
- dictionnaire libre qui remelange structure et interpretation.

Required public JSON fields:

- `interpretive_valence`;
- `energy_type`.

Optional fields:

- mode degrade documente avec valeur `None`;
- story de sortie;
- preuve OpenAPI;
- preuve frontend ciblee;
- adapter public nomme.

Status codes:

- no HTTP endpoint, method or status code is changed without explicit public contract evidence.

Serialization names:

- les noms JSON publics `interpretive_valence` et `energy_type` restent inchanges.

Frontend type impact:

- verifier `frontend/src` par recherche ciblee si une forme publique change.

Generated contract impact:

- `app.routes`, `app.openapi()` et `TestClient` doivent documenter le delta public autorise ou l'absence de delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | bridges Temporary non classes | inventaire CS-233 | aucun runtime | evidence scan | classification complete | hit non classe |
| 2 | `AspectReferenceData` hybride | vues reference separees | mapper reference | repository/unit | zero champ hybride force | champ interpretatif requis |
| 3 | `AspectDefinitionRuntimeData` | contrats separes | graph nodes natal | unit/architecture | zero import calcul natal | consommateur interne actif |
| 4 | `_aspect_definition` | `_aspect_runtime_rules` direct | graphe natal | graph execution | zero helper legacy | graph casse |
| 5 | `AspectResult` champs plats | hints explicites | resultats aspects | contracts/unit | zero field plat | fixture non migree |
| 6 | fallback `json_builder` | projection depuis hints | serializer chart | public tests | no fallback scan | cle publique absente |
| 7 | allowlists Temporary | guards definitifs | architecture tests | boundary tests | zero Temporary actif | invariant absent |
| 8 | docs obsoletes | doc runtime alignee | docs only | doc test | matrice a jour | mention contractuelle legacy |

Completion rule: chaque batch conserve `pytest`, `TestClient`, `app.routes`, `app.openapi()`, scores, orbes, doctrine et contrats publics autorises.

## 4h. Reintroduction Guard

- Guard target:
  - aucun `AspectDefinitionRuntimeData` dans les chemins de calcul natal;
  - aucun `AspectReferenceData.default_valence`, `interpretive_valence` ou `energy_type` dans la vue structurelle;
  - aucun `_aspect_definition` comme bridge graph;
  - aucun champ plat interpretatif sur `AspectResult`;
  - aucun fallback `json_builder` sur `aspect.interpretive_valence` ou `aspect.energy_type`;
  - aucune allowlist `Temporary` active pour les champs interpretatifs aspectuels;
  - aucune lecture prediction depuis le runtime structurel astrology hybride.
- Guard mechanism:
  - architecture guard explicite contre tout symbole legacy reintroduced dans les zones structurelles;
  - deterministic source: forbidden symbols;
  - deterministic source: generated openapi paths;
  - tests d'architecture AST sur chemins backend-domain explicites;
  - scan cible des tokens legacy et champs hybrides;
  - tests unitaires des contrats d'aspects et hints;
  - tests de projection publique avec `TestClient`;
  - preuve `app.routes`, `app.openapi()` et `pytest`;
  - recherche ciblee `frontend/src` seulement si une surface publique change.
- Guard owner:
  - `backend/tests/architecture/test_astrology_runtime_boundary.py`;
  - `backend/tests/architecture/test_structural_runtime_boundary.py`;
  - `backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`;
  - chemin complet `pytest -q backend/tests/architecture/test_structural_runtime_boundary.py`;
  - chemin complet `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - chemin complet `pytest -q backend/app/tests/unit/test_chart_json_builder.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Legacy bridge inventory | `evidence/legacy-bridge-inventory.md` | Classer chaque bridge aspect reference et sa decision. |
| Public contract evidence | `evidence/public-contract.md` | Conserver `app.routes`, `app.openapi()`, TestClient et recherche front ciblee. |
| Validation evidence | `evidence/validation.md` | Conserver lint, tests, scans et decisions d'allowlist. |

## 5. Current State Evidence

- Le brief indique que les contrats structurels et interpretatifs d'aspects existent deja.
- Le brief indique que les calculateurs consomment desormais la vue structurelle.
- Le brief liste les bridges encore marques `Temporary` dans runtime reference, graph nodes, `AspectResult`, `json_builder` et architecture tests.
- CS-231 a pose les guardrails structural versus interpretive.
- CS-232 a supprime des surfaces legacy plus larges, mais a laisse cette fermeture fine des bridges aspect reference.
- Evidence 1: `_story_briefs/cs-233-remove-aspect-reference-legacy-bridges.md` - demande de suppression finale.
- Evidence 2: `backend` existe dans l'arborescence courante.
- Evidence 3: `_condamad/stories/regression-guardrails.md` contient des guardrails locales RG-098, RG-099, RG-106, RG-107 et RG-145.
- Evidence 4: `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` existe.
- Evidence 5: `.agents/skills/condamad-story-writer/scripts/condamad_story_lint.py` existe.
- Evidence 6: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` sont absents.

## 6. Target State

- `AspectReferenceSet` expose des definitions structurelles et profils interpretatifs separes.
- `AspectReferenceData` ne force plus de champs interpretatifs avec angle et orbe.
- `AspectDefinitionRuntimeData` ne sert plus au calcul natal.
- `_aspect_runtime_rules` construit directement definitions structurelles et profils interpretatifs.
- `AspectResult` ne contient plus de champs plats interpretatifs.
- `json_builder` lit `aspect_interpretive_hints` comme source unique des champs publics interpretatifs.
- L'absence de hints sur un aspect publie est detectee explicitement.
- Les allowlists `Temporary` liees aux champs interpretatifs aspectuels sont supprimees.
- Prediction reste isolee avec ses profils et projections propres.
- `docs/architecture/astrology-runtime-surfaces.md` documente l'etat final.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- runtime-contracts: yes;
- astrology reference mapper: yes;
- graph nodes: yes;
- chart public projection: yes;
- prediction boundary: limited;
- API: no public key removal;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-098 | local | Les faits runtime d'aspect restent produits par runtime et evaluator dedies, sans dependance prediction. |
| RG-099 | local | Les champs publics d'aspects restent presents et viennent du runtime canonique ou des hints. |
| RG-106 | local | Les calculateurs astrology consomment des contrats types sans constantes valence/energie legacy. |
| RG-107 | local | Les donnees DB/JSON sont parsees vers contrats immutables, pas transmises en payload libre. |
| RG-145 | local | Le moteur d'aspects reste sur les entrees chart objects et definitions structurelles. |

Non-applicable examples:

- DB/migration guardrails: hors scope, aucune table ni migration Alembic n'est modifiee.
- Frontend/style/build guardrails: hors scope, seule une recherche de contrat front peut etre necessaire.
- Auth/i18n guardrails: hors scope, aucune authentification ou localisation n'est modifiee.

Registry gap:

- Aucun guardrail global dedie a l'extinction definitive des bridges `AspectReferenceData` hybrides n'existe encore.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | `AspectDefinitionRuntimeData` est absent du calcul natal. | `AST guard`; `pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py`. |
| AC2 | `AspectReferenceData` ne force plus les champs interpretatifs. | `AST guard`; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | Le graphe natal consomme les vues separees. | `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`. |
| AC4 | `AspectResult` ne contient plus de champs plats interpretatifs. | `AST guard`; `pytest -q backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`. |
| AC5 | `json_builder` utilise les hints comme source unique des champs publics interpretatifs. | `TestClient`; `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC6 | Les allowlists `Temporary` aspectuelles sont supprimees. | `AST guard`; `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`. |
| AC7 | Prediction utilise ses profils ou projections propres. | `pytest -q backend/app/tests/unit/test_astrology_prediction_boundary.py`. |

## 8. Implementation Tasks

- [x] Task: inventorier les bridges `Temporary` par recherche ciblee et classer chaque hit. (AC: AC1, AC2, AC6)
- [x] Task: modifier `AspectReferenceSet` pour exposer des vues structurelles et interpretatives separees. (AC: AC2)
- [x] Task: migrer `AstrologyRuntimeReferenceMapper` vers les vues separees sans payload libre. (AC: AC2)
- [x] Task: supprimer ou neutraliser `AspectDefinitionRuntimeData` dans les chemins de calcul natal. (AC: AC1)
- [x] Task: migrer `_aspect_runtime_rules` et supprimer `_aspect_definition` si ce helper ne sert plus qu'au bridge legacy. (AC: AC3)
- [x] Task: retirer `default_valence`, `interpretive_valence` et `energy_type` de `AspectResult`. (AC: AC4)
- [x] Task: supprimer le fallback `json_builder` sur `aspect.interpretive_valence` et `aspect.energy_type`. (AC: AC5)
- [x] Task: ajouter la detection explicite d'absence de hints pour un aspect publie. (AC: AC5)
- [x] Task: nettoyer les allowlists `Temporary` dans les tests d'architecture. (AC: AC6)
- [x] Task: traiter la mention legacy `AspectRuntimeWeightTaxonomy.interpretive_weight` dans docs et guards. (AC: AC6)
- [x] Task: verifier que prediction conserve ses contrats propres et ne lit pas le runtime structurel hybride. (AC: AC7)
- [x] Task: mettre a jour `docs/architecture/astrology-runtime-surfaces.md`. (AC: AC1, AC2, AC6)
- [x] Task: collecter les preuves `AST guard`, `pytest`, `TestClient`, `app.routes` et `app.openapi()`. (AC: AC1, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser les contrats CS-229 et CS-230 pour nommer structural runtime, interpretive profiles et hints.
- Reutiliser les tests d'architecture CS-231 et CS-232 avant de creer un nouveau helper.
- Reutiliser `docs/architecture/astrology-runtime-surfaces.md` comme documentation canonique.
- Reutiliser les helpers existants de graph execution et reference repository.
- Ne pas creer un second registre global de guardrails.
- Ne pas dupliquer les listes de champs interdits dans plusieurs fichiers sans helper local commun.
- Ne pas ajouter de dependance externe.

## 10. No Legacy / Forbidden Paths

- Ne pas conserver `AspectDefinitionRuntimeData` comme bridge durable.
- Ne pas conserver `_aspect_definition` si son seul role est de reconstruire le bridge legacy.
- Ne pas forcer `default_valence`, `interpretive_valence` ou `energy_type` dans `AspectReferenceData`.
- Ne pas ajouter les champs plats `default_valence`, `interpretive_valence` ou `energy_type` a `AspectResult`.
- Ne pas lire `aspect.interpretive_valence` ou `aspect.energy_type` comme fallback dans `json_builder`.
- Ne pas transformer l'absence de hints en fallback silencieux.
- Ne pas supprimer les cles publiques `interpretive_valence` et `energy_type`.
- Ne pas faire dependre prediction du runtime structurel astrology hybride.
- Ne pas ajouter de compatibility layer, shim, wrapper ou fallback non borne.
- Ne pas modifier DB, migrations, prompts, scores, doctrine, auth, i18n, style ou build.
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

- `_condamad/stories/CS-233-remove-aspect-reference-legacy-bridges/evidence/legacy-bridge-inventory.md`

Table d'audit obligatoire:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| bridge legacy | field/class/helper/fallback | classification | owner liste | surface cible | delete/replace-consumer/keep-public-contract | scan/test | risque |

Allowed decisions:

- `delete`;
- `replace-consumer`;
- `keep-public-contract`;
- `needs-user-decision`.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Definition geometrique d'aspect | `AspectStructuralDefinitionRuntimeData` | `AspectDefinitionRuntimeData` bridge |
| Profil interpretatif d'aspect | `AspectInterpretiveProfileRuntimeData` | champs plats sur reference structurelle |
| Graphe natal | `_aspect_runtime_rules` direct | `_aspect_definition` helper legacy |
| Resultat d'aspect | `AspectResult.aspect_interpretive_hints` | `AspectResult.default_valence`, `interpretive_valence`, `energy_type` |
| Projection publique | `json_builder` depuis hints | fallback sur champs plats |
| Prediction | contrats prediction dedies | runtime structurel astrology hybride |
| Documentation surfaces | `docs/architecture/astrology-runtime-surfaces.md` | allowlists `Temporary` durables |

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

- External usage blocker: public JSON fields and frontend consumers must remain compatible.
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
  - test public natal/chart existant;
  - recherche ciblee `frontend/src` pour `interpretive_valence|energy_type` si le payload public est touche.
- Capture after:
  - memes preuves.
- Expected result:
  - aucun endpoint, method, status code, schema public ou cle JSON publique ne change sans preuve explicite et decision documentee.

## 17. Files to Inspect First

- `backend/app/domain/astrology/runtime/runtime_reference.py`.
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`.
- `backend/app/domain/astrology/natal_calculation.py`.
- `backend/app/services/chart/json_builder.py`.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`.
- `backend/app/infra/db/repositories/reference_repository.py`.
- `backend/app/domain/astrology/runtime/aspect_modifiers.py`.
- `backend/tests/architecture/test_astrology_runtime_boundary.py`.
- `backend/tests/architecture/test_structural_runtime_boundary.py`.
- `backend/tests/architecture/test_aspect_runtime_boundary.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.
- `backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`.
- `backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`.
- `backend/app/tests/unit/test_chart_json_builder.py`.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`.
- `docs/architecture/astrology-runtime-surfaces.md`.

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/runtime_reference.py`.
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`.
- `backend/app/domain/astrology/natal_calculation.py`.
- `backend/app/services/chart/json_builder.py`.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`.
- `backend/app/domain/astrology/runtime/aspect_modifiers.py`, seulement si la mention legacy reste active.
- `backend/tests/architecture/test_astrology_runtime_boundary.py`.
- `backend/tests/architecture/test_structural_runtime_boundary.py`.
- `backend/tests/architecture/test_aspect_runtime_boundary.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.
- `docs/architecture/astrology-runtime-surfaces.md`.
- `_condamad/stories/CS-233-remove-aspect-reference-legacy-bridges/evidence/legacy-bridge-inventory.md`.
- `_condamad/stories/CS-233-remove-aspect-reference-legacy-bridges/evidence/public-contract.md`.
- `_condamad/stories/CS-233-remove-aspect-reference-legacy-bridges/evidence/validation.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`.
- `backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`.
- `backend/app/tests/unit/test_chart_json_builder.py`.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`.
- `backend/app/tests/unit/test_astrology_prediction_boundary.py`.

Files not expected to change:

- `backend/alembic`.
- prompt templates and LLM providers.
- DB models, seeds and migrations.
- `frontend/src`, sauf adaptation testee apres decision de delta public.

## 19. Dependency Policy

- New dependencies: none.
Justification: no dependency changes are authorized.

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
pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py
pytest -q backend/tests/architecture/test_structural_runtime_boundary.py
pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py
pytest -q backend/app/tests/unit/test_astrology_prediction_boundary.py
```

Run anti-regression scans:

```powershell
rg -n "AspectDefinitionRuntimeData|_aspect_definition|AspectReferenceData" `
  backend/app/domain/astrology backend/app/services/chart backend/tests/architecture -g "*.py"
rg -n "default_valence|interpretive_valence|energy_type|interpretive_weight" `
  backend/app/domain/astrology backend/app/services/chart backend/app/domain/prediction backend/tests/architecture -g "*.py"
rg -n "aspect_interpretive_hints|structural_definitions|interpretive_profiles" `
  backend/app/domain/astrology backend/app/services/chart backend/tests -g "*.py"
```

Run public contract proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
rg -n "interpretive_valence|energy_type" frontend/src
```

The dedicated public contract evidence must name `app.routes`, `app.openapi()`, `TestClient` and `pytest`.

## 21. Regression Risks

- Une fixture peut encore construire un aspect avec des champs plats de valence.
- Un serializer public peut garder un fallback silencieux et masquer une absence de hints.
- Prediction peut consommer par erreur le runtime structurel astrology au lieu de ses profils dedies.
- Une allowlist `Temporary` peut rester trop large apres la suppression.
- Une suppression interne peut etre confondue avec une suppression de cle JSON publique.
- Un dictionnaire libre peut recreer le couplage structure et interpretation sans type explicite.

## 22. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only CS-233.
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
- Conserver dans l'evidence les commandes lancees, resultats de tests, scans, `app.routes`, `app.openapi()` et recherche frontend ciblee.

## 23. CS-233 Final Evidence Template

```markdown
## CS-233 Final Evidence

### Legacy Bridge Inventory
- Each bridge hit is classified as internal source, public projection, prediction, test, fixture or historical doc.
- Internal bridge reads are migrated or deleted.

### Aspect Reference Split
- Structural definitions and interpretive profiles are exposed separately.
- AspectDefinitionRuntimeData is absent from natal calculation paths.

### Public Compatibility
- Public fields interpretive_valence and energy_type remain present.
- app.routes, app.openapi(), TestClient and pytest are captured.

### Guardrails
- AST guard blocks flat fields and bridge symbols.
- Temporary allowlists for aspect interpretive fields are removed.

### Commands
- ruff format backend
- ruff check backend
- pytest -q backend/tests/architecture/test_astrology_runtime_boundary.py
- pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py
- pytest -q backend/app/tests/unit/test_chart_json_builder.py
```

## 24. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-233-remove-aspect-reference-legacy-bridges.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the brief, adjacent CS-231/CS-232 structure and validator diagnostics.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted ID search only.
- No regression guardrail registry update was made.

## 25. References

- Source brief: `_story_briefs/cs-233-remove-aspect-reference-legacy-bridges.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-098`, `RG-099`, `RG-106`, `RG-107`, `RG-145`).
- Previous story: `_condamad/stories/CS-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases/00-story.md`.
