# Story CS-207 traditional-advanced-final-audit-documentation: Auditer et documenter la chaine traditionnelle avancee

Status: done

## 1. Objective

Clore le chantier traditionnel avance livre par CS-197 a CS-206 en produisant
un audit transversal, une cartographie de contrats, une matrice de regression,
des scans documentes, une validation reproductible et un statut final
serialise. CS-207 ne doit ajouter aucune capacite astrologique: elle doit
prouver que secte, hayz, rejoicing, triplicite dependante de la secte,
mitigation benefique/malefique, conditions avancees, profils, signaux,
dominantes, adaptation interpretative, JSON public, panneau expert frontend et
persistance d'audit tiennent ensemble sans recalcul local ni double scoring.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-21 pour CS-207, closure story
  des stories CS-197 a CS-206.
- Closure sources:
  - CS-197 `sect-audit-explicit-contract`;
  - CS-198 `planet-sect-condition-normalization`;
  - CS-199 `advanced-sect-scoring-integration`;
  - CS-200 `hellenistic-medieval-golden-cases`;
  - CS-201 `natal-public-json-projection-cleanup`;
  - CS-202 `natal-expert-panel`;
  - CS-203 `natal-dignity-audit-persistence`;
  - CS-204 `hayz-rejoicing-explicit-condition-contracts`;
  - CS-205 `sect-aware-triplicity-golden-cases`;
  - CS-206 `benefic-malefic-sect-mitigation-signals`.
- Reason for change: les briques traditionnelles avancees ont ete livrees par
  stories successives; il faut maintenant une preuve de fermeture transverse,
  lisible, reproductible et attachee a la story.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend tous les enjeux du brief source:
  mapping des contrats, interdiction de recalcul local, stabilite des scores,
  audit JSON public, audit frontend, audit de persistance, evidence finale et
  statut JSON. Aucun enjeu n'est transforme en nouvelle fonctionnalite ou
  reporte sans preuve.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `traditional_advanced_natal_conditions_closure_audit`
- In scope:
  - auditer les owners et consommateurs des contrats CS-197 a CS-206;
  - verifier l'absence de recalcul local de secte, condition de secte, hayz,
    rejoicing, triplicite ou mitigation;
  - verifier l'absence de double scoring sur les scores de dignite, profils,
    dominantes et adaptateur interpretatif;
  - verifier la stabilite des chemins JSON publics;
  - verifier que le frontend affiche des faits backend sans doctrine locale;
  - verifier que le panneau expert frontend gere les etats vides ou
    indisponibles sans calcul astrologique local;
  - verifier que la persistance d'audit consomme des resultats deja calcules;
  - verifier que `astral_chart_planet_dignity_results` persiste les dignites,
    reste idempotente, reste liee au chart result et ne remplace pas
    `chart_results.result_payload`;
  - consolider la documentation technique et les limites restantes;
  - produire les artefacts d'evidence requis sous
    `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/`;
  - ajouter uniquement des garde-fous de test si l'audit prouve une couverture
    manquante.
- Out of scope:
  - ajouter une nouvelle regle astrologique;
  - modifier les scores, poids, seeds, migrations, routes API, methodes HTTP ou
    contrats JSON publics;
  - modifier fonctionnellement le frontend;
  - generer une interpretation narrative ou appeler un LLM;
  - refactorer massivement l'architecture;
  - introduire des alias, shims, compatibilites ou fallbacks.
- Explicit non-goals:
  - ne pas changer les invariants `RG-124` a `RG-134`;
  - ne pas creer de nouveau moteur de calcul;
  - ne pas rendre `json_builder.py`, le frontend, la persistance d'audit, les
    profils, la dominance ou l'adaptateur interpretatif proprietaires de la
    secte;
  - ne pas accepter `PASS with limitation`, TODO, residual hidden work ou
    allowlist large pour fermer la story;
  - ne pas ajouter de dossier de base sous `backend/`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: custom
- Archetype reason: CS-207 est une story de fermeture par audit/documentation
  transversal; aucun archetype standard ne couvre exactement une cloture sans
  changement metier qui produit uniquement preuves, documentation et gardes
  eventuels. Ce `custom` implemente l'intention du brief
  `closure-regression-audit`.
- Additional validation rules:
  - les artefacts d'evidence requis par le brief sont obligatoires;
  - les scans requis doivent etre executes et tous les hits autorises doivent
    etre classes;
  - les tests cibles backend et frontend doivent etre lances ou documentes avec
    raison exacte, risque et preuve de substitution;
  - tout changement de code applicatif doit etre justifie comme garde-fou ou
    bugfix documente;
  - aucun changement de resultat astrologique ou de contrat public n'est
    autorise.
- Behavior change allowed: no
- Behavior change constraints:
  - aucun resultat astrologique ne change;
  - aucun contrat JSON public ne change;
  - aucun comportement frontend ne change;
  - aucune route, methode HTTP, migration, seed ou dependance ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l'audit decouvre une incoherence qui ne peut pas
  etre fermee par documentation ou garde-fou sans changer une regle
  astrologique, un contrat public, un score, un seed ou une migration.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La story doit prouver les sources canoniques de secte, conditions, scores, JSON public, frontend et audit persistence. |
| Baseline Snapshot | yes | Les scores, contrats publics et surfaces critiques doivent etre compares a l'etat existant et declares stables. |
| Ownership Routing | yes | Chaque contrat doit etre mappe avec owner, source de verite, consumer et public path. |
| Allowlist Exception | no | Les hits autorises doivent etre documentes un par un; aucune allowlist large n'est permise. |
| Contract Shape | yes | Le contrat mappe `ChartSectResult`, `PlanetSectCondition`, hayz/rejoicing, conditions, JSON public, frontend et persistence. |
| Batch Migration | no | La story ne migre pas de surface et ne change pas de code fonctionnel par lots. |
| Reintroduction Guard | yes | Les scans et tests doivent bloquer les recalculs locaux et constantes doctrinales. |
| Persistent Evidence | yes | Les rapports, matrices, scans, validation et statut JSON sont l'objet principal de la story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/dignities/**` pour `ChartSectResult`,
    `PlanetSectCondition`, dignites et triplicite;
  - `backend/app/domain/astrology/advanced_conditions/**` pour hayz,
    rejoicing normalise, conditions avancees et mitigation;
  - `backend/app/domain/astrology/condition/**` pour profils et signaux;
  - `backend/app/domain/astrology/dominance/**` pour dominantes;
  - `backend/app/domain/astrology/interpretation_adapters/**` pour adaptation
    interpretative factuelle;
  - `backend/app/services/chart/json_builder.py` comme projecteur public
    serialize-only;
  - `backend/app/services/chart/result_service.py` et
    `backend/app/infra/db/**` comme persistance et audit sans recalcul;
  - `astral_chart_planet_dignity_results` comme table d'audit des dignites
    calculees, idempotente, liee au chart result et distincte de
    `chart_results.result_payload`;
  - `frontend` comme consommateur affichage uniquement.
- Runtime artifact:
  - loaded config `AstrologyRuntimeReference` exercised by the targeted
    astrology tests;
  - DB schema `AstralChartPlanetDignityResultModel.__table__` exercised by
    `test_chart_result_service.py`;
  - AST guard or targeted `rg` guard evidence for forbidden calculator imports
    and frontend derivations;
  - tests unitaires cibles listés dans le plan de validation;
  - scans requis du brief;
  - rapport d'audit et contract map persistants;
  - statut final JSON.
- Secondary evidence:
  - `story-status.md` prouve CS-197 a CS-206 en `done`;
  - `regression-guardrails.md` prouve les invariants `RG-124` a `RG-134`;
  - evidence historique des stories CS-197 a CS-206 quand elle est requise par
    la cartographie.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas la stabilite des tests golden, JSON, profils,
    dominantes, adapter et persistance;
  - les hits autorises doivent etre relies a des owners canoniques.
- Forbidden sources:
  - constantes doctrinales locales dans `frontend`, `json_builder.py`,
    persistance audit ou downstream consumers;
  - lecture de l'audit DB pour reconstruire le payload public;
  - recalcul de secte dans les profils conditionnels, la dominance ou
    l'adaptateur interpretatif;
  - LLM, prompts ou prediction pour l'audit traditionnel avance.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/`
- Baseline artifact before implementation:
  - interpretation: artefacts d'audit a produire avant le statut final, car
    CS-207 est une story de fermeture documentaire sans changement applicatif.
  - `traditional-advanced-audit-report.md`
  - `traditional-advanced-contract-map.md`
  - `traditional-advanced-regression-matrix.md`
  - `traditional-advanced-scan-results.md`
- Comparison after implementation:
  - interpretation: artefacts de validation a produire apres scans et tests.
  - `traditional-advanced-validation.md`
  - `traditional-advanced-final-status.json`
- Comparison rule:
  - les scores `essential_score`, `accidental_score`, `total_score`,
    `functional_strength_score`, `expression_quality_score`,
    `intensity_score`, les profils, dominantes et faits d'adaptation
    interpretative doivent etre declares stables;
  - toute difference doit etre classee comme bugfix documente et reliee a un
    test, sinon elle bloque la cloture.
- Expected invariant:
  - aucun changement metier, contrat public, route, frontend behavior, seed ou
    migration;
  - nouveaux artefacts d'evidence et documentation seulement, sauf garde-fou
    cible manquant.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | CS-207 role | Forbidden destination |
|---|---|---|---|
| Chart sect | `ChartSectResult` / dignity sect owner | audit and document | `json_builder.py`, frontend, persistence, dominance |
| Planet sect condition | `PlanetSectCondition` owner | audit and document | downstream recalculation |
| Hayz | advanced/traditional condition owners | audit and document | frontend or JSON derivation |
| Rejoicing | dignity/traditional condition owners | audit and document | frontend joy constants |
| Triplicity sect-aware | essential dignity owner | audit and document | local day/night maps |
| Benefic/malefic mitigation | advanced conditions owner | audit and document | frontend or JSON builder |
| Profiles/signals | condition owners | audit and document | UI thresholds |
| Dominants | dominance owner | audit and document | JSON or frontend scoring |
| Interpretation adapter | interpretation adapter owner | audit and document | narrative/LLM |
| Public JSON | `json_builder.py` | prove serialize-only | calculator imports |
| Frontend expert panel | frontend display owner | prove display-only | astrology doctrine |
| Audit persistence | chart service / DB repositories | prove persist-only, idempotent and chart-linked | dignity recalculation or public payload replacement |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: CS-207 n'autorise aucune allowlist large. Tout hit de scan conserve
  doit etre documente dans `traditional-advanced-scan-results.md` avec fichier,
  ligne, owner, raison et statut `allowed` ou `blocker`.

## 4f. Contract Shape

- Contract type:
  - closure audit contract and public evidence package.
- Fields:
  - `ChartSectResult`
  - `PlanetSectCondition`
  - `HayzCondition`
  - `RejoicingCondition`
  - `TraditionalPlanetCondition`
  - `SectNatureMitigationCondition`
  - `PlanetDignityResult`
  - `PlanetConditionProfile`
  - `PlanetConditionSignal`
  - `AdvancedCondition`
  - `DominantPlanetsResult`
  - `InterpretationAdapterResult`
  - public JSON
  - frontend expert panel
  - audit persistence
- Required audit axes:
  - no duplicate calculation in `json_builder.py`, frontend, audit
    persistence, condition profiles, dominance or interpretation adapter;
  - score stability for dignity scores, condition profiles, dominant planets
    and interpretation adapter facts;
  - public JSON path stability;
  - frontend empty/unavailable state handling without local astrology doctrine;
  - audit persistence idempotence, chart-result link and non-replacement of
    `chart_results.result_payload`.
- Required fields:
  - for each mapped contract: owner, source of truth, consumer, public path,
    tests and story source.
- Optional fields:
  - none expected; any in-domain limitation must be recorded as a blocker
    unless evidence proves it is outside CS-207 scope.
- Status codes:
  - no HTTP endpoint, method or status code may change.
- Serialization names:
  - preserve existing public JSON names:
    `dignities.sect`, `dignities.planets[*].sect_condition`,
    `traditional_conditions`, `advanced_conditions`,
    `planet_condition_profiles`, `planet_condition_signals`,
    `dominant_planets`, `interpretation_adapter`.
- Frontend type impact:
  - no functional frontend change expected; frontend audit may only document
    existing display/types.
- Generated contract impact:
  - no generated contract change expected; if generated contracts exist, record
    no-diff proof in validation evidence.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-207 ne migre aucun namespace, contrat, route, champ ou composant.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `evidence/traditional-advanced-audit-report.md` | Conclusion transverse, limites, non-redondance et absence de nouveau comportement. |
| Contract map | `evidence/traditional-advanced-contract-map.md` | Owner, source, consumer, public path, tests et story source. |
| Regression matrix | `evidence/traditional-advanced-regression-matrix.md` | Capacites, owners, chemins publics, tests, evidence et statut. |
| Scan results | `evidence/traditional-advanced-scan-results.md` | Commandes `rg`, hits autorises, blockers et justification. |
| Validation record | `evidence/traditional-advanced-validation.md` | Commandes, resultats, skipped commands, risques et checks finaux. |
| Final status | `evidence/traditional-advanced-final-status.json` | Statut serialise de fermeture avec booleens de stabilite. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher tout recalcul local de secte, hayz, rejoicing, triplicite,
    mitigation, scores, profils, dominantes ou interpretation dans les couches
    de projection, frontend, persistence et downstream consumers.
- Forbidden examples:
  - constantes `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`, `BENEFIC_PLANETS`,
    `MALEFIC_PLANETS`, `TRIPLICITY_RULERS`, `JOY_HOUSES`,
    `PLANETARY_JOYS`, `HAYZ_RULES`, `ABOVE_HORIZON_HOUSES`,
    `BELOW_HORIZON_HOUSES` hors owners canoniques;
  - alias `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`,
    `planet_sect_code`, `legacy_hayz`, `legacy_rejoicing`,
    `sect_mitigation_legacy`;
  - imports de calculateurs dans `json_builder.py`, `frontend` ou persistence;
  - conditions frontend sur `planet_code`, `chart_sect`, `sun.house`,
    `planet.house` ou `house_number`.
- Required guard evidence:
  - les quatre scans requis par le brief;
  - tous les tests cibles backend et frontend listés;
  - `ruff format .`, `ruff check .`, `npm run typecheck`, `npm run lint`,
    `npm run build`;
  - evidence files et statut JSON valides.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `brief utilisateur CS-207 traditional-advanced-final-audit-documentation`
- Closure proof required: evidence directory complete, contract map, scan
  results, regression matrix, validation record, final status JSON and
  successful targeted tests/scans or documented blockers requiring user
  decision.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

CS-207 est une story de fermeture. Si une incoherence in-domain est decouverte,
la story ne peut pas etre marquee complete avec limitation: elle doit soit la
corriger par garde-fou/bugfix documente sans changer les contrats, soit bloquer
avec decision utilisateur explicite.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - CS-197 a CS-206 sont
  enregistrees et marquees `done`; CS-207 est enregistree comme story de
  fermeture suivante.
- Evidence 2: `_condamad/stories/regression-guardrails.md` - invariants
  `RG-124` a `RG-133` couvrent secte chart-level, condition de secte,
  integration de scoring, golden cases, JSON public, frontend, persistance,
  hayz/rejoicing, triplicite et mitigation.
- Evidence 3: `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md`
  - source du contrat chart-level `dignities.sect`.
- Evidence 4:
  `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md` -
  source du contrat `dignities.planets[*].sect_condition`.
- Evidence 5:
  `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md` -
  integration des faits de secte dans le scoring avance.
- Evidence 6:
  `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md` -
  baseline golden cases traditionnels.
- Evidence 7:
  `_condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md` -
  `json_builder.py` est la projection publique serialize-only.
- Evidence 8: `_condamad/stories/CS-202-natal-expert-panel/00-story.md` -
  le frontend expert panel affiche les faits backend sans recalcul.
- Evidence 9:
  `_condamad/stories/CS-203-natal-dignity-audit-persistence/00-story.md` -
  l'audit persistence consomme des dignites deja calculees.
- Evidence 10:
  `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md`
  - hayz et rejoicing sont des contrats explicites.
- Evidence 11:
  `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` -
  la triplicite dependante de la secte est verrouillee par golden cases.
- Evidence 12:
  `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/00-story.md`
  - mitigation benefique/malefique par secte est exposee comme fait runtime.

Assumptions to verify during implementation:

- les fichiers d'evidence des stories CS-197 a CS-206 sont disponibles et
  suffisants pour alimenter la cartographie finale;
- les commandes frontend utilisent `npm`; si `pnpm` ou `yarn` est le package
  manager reel, adapter uniquement la commande et documenter l'adaptation;
- le script `npm run typecheck` existe ou son absence est documentee dans
  `traditional-advanced-validation.md`.

## 6. Target State

After implementation:

- le dossier d'evidence CS-207 existe avec les six artefacts obligatoires;
- chaque contrat traditionnel avance est mappe avec owner, source de verite,
  consommateur, chemin public, tests et story source;
- les scans prouvent qu'aucune couche interdite ne recalcule secte, hayz,
  rejoicing, triplicite, mitigation ou scores;
- la matrice de regression relie chaque capacite aux tests et preuves;
- le rapport final documente les limites restantes sans masquer un blocker;
- le JSON public reste stable;
- le frontend reste display-only;
- la persistance d'audit reste persist-only;
- le statut final JSON est valide et indique `validation_status: "passed"`
  seulement si les validations ont reellement passe.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-124` - contrat chart-level `dignities.sect`.
  - `RG-125` - contrat de condition de secte par planete.
  - `RG-126` - integration avancee des faits de secte sans recalcul downstream.
  - `RG-127` - golden cases traditionnels hellenistiques/medievaux.
  - `RG-128` - projection JSON publique serialize-only.
  - `RG-129` - frontend expert panel display-only.
  - `RG-130` - persistance d'audit des dignites sans recalcul.
  - `RG-131` - contrats explicites hayz/rejoicing.
  - `RG-132` - triplicite essentielle dependante de la secte.
  - `RG-133` - mitigation benefique/malefique par la secte.
  - `RG-134` - cloture documentaire et validation transverse de toute la
    chaine traditionnelle avancee.
- Non-applicable invariants:
  - guardrails API route hors natal - aucune route n'est ajoutee, supprimee ou
    renommee;
  - guardrails LLM/prediction - la story interdit LLM et prediction.
- Required regression evidence:
  - contract map;
  - scan results;
  - regression matrix;
  - validation report;
  - final status JSON;
  - tests backend/frontend cibles;
  - quality checks.
- Allowed differences:
  - nouveaux fichiers d'evidence CS-207;
  - documentation sous `docs/**` si elle consolide le contrat;
  - tests de garde-fou uniquement si l'audit prouve un manque.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Tous les contrats CS-197 a CS-206 sont mappes. | Evidence profile: `persistent_evidence`; `Test-Path` contract map + contract `rg`. |
| AC2 | Aucun recalcul local interdit n'est present ou non classe. | Evidence profile: `targeted_forbidden_symbol_scan`; quatre scans `rg` requis + scan-results. |
| AC3 | Les tests backend cibles passent. | Evidence profile: `deterministic_test`; commandes `pytest -q` du Validation Plan apres activation `.venv`. |
| AC4 | Les checks qualite backend passent. | Evidence profile: `deterministic_test`; `ruff format .` et `ruff check .` apres activation `.venv`. |
| AC5 | Frontend expert panel sans doctrine locale. | Evidence profile: `reintroduction_guard`; `npm --prefix frontend test -- NatalExpertPanel` + scans frontend. |
| AC6 | La persistance d'audit ne recalcule pas. | Evidence profile: `runtime_behavior_check`; `test_chart_result_service.py` + scans calculateurs interdits. |
| AC7 | Le JSON public conserve les chemins requis. | Evidence profile: `json_contract_shape`; `test_natal_result_contract.py`, `test_chart_json_builder.py` et contract map. |
| AC8 | Les scores de dignite sont stables. | Evidence profile: `baseline_before_after_diff`; scoring pytest + `rg` scores matrix. |
| AC9 | Les golden cases traditionnels passent. | Evidence profile: `deterministic_test`; `test_traditional_golden_cases.py`. |
| AC10 | Limites restantes sans blocker cache. | Evidence profile: `persistent_evidence`; `rg -n "Limites restantes|blocker" evidence/traditional-advanced-audit-report.md`. |
| AC11 | Aucun nouveau comportement metier n'est introduit. | Evidence profile: `baseline_before_after_diff`; app-surface `git diff` + validation `rg`. |
| AC12 | Le statut final JSON est valide. | Evidence profile: `persistent_evidence`; `python -m json.tool` final status. |
| AC13 | Les downstream facts sont stables. | Evidence profile: `baseline_before_after_diff`; `pytest -q test_planet_condition_profile_service.py`. |
| AC14 | Les golden cases de triplicite passent. | Evidence profile: `deterministic_test`; `test_triplicity_golden_cases.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Creer le dossier d'evidence et auditer les sources (AC: AC1, AC10, AC12)
  - [ ] Subtask 1.1 - Creer
    `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/`.
  - [ ] Subtask 1.2 - Inspecter les stories CS-197 a CS-206, leurs evidence
    directories et `regression-guardrails.md`.
  - [ ] Subtask 1.3 - Creer `traditional-advanced-audit-report.md` avec
    synthese, non-redondance, limites et conclusion de fermeture.

- [ ] Task 2 - Produire la contract map (AC: AC1, AC7)
  - [ ] Subtask 2.1 - Mapper chaque contrat liste en section 4f.
  - [ ] Subtask 2.2 - Pour chaque contrat, renseigner owner, source of truth,
    consumer, public path, tests et story source.
  - [ ] Subtask 2.3 - Signaler comme blocker tout contrat non localisable.

- [ ] Task 3 - Executer et documenter les scans requis (AC: AC2, AC5, AC6, AC11)
  - [ ] Subtask 3.1 - Executer les quatre scans `rg` exacts du Validation Plan.
  - [ ] Subtask 3.2 - Classer chaque hit avec fichier, ligne, owner, raison et
    statut.
  - [ ] Subtask 3.3 - Documenter toute absence de hit comme zero-result attendu.

- [ ] Task 4 - Produire la regression matrix (AC: AC3, AC4, AC7, AC8, AC9, AC13, AC14)
  - [ ] Subtask 4.1 - Lister les capacites du brief avec owner, public path,
    tests, evidence et statut.
  - [ ] Subtask 4.2 - Ajouter les scores et downstream facts a la matrice.
  - [ ] Subtask 4.3 - Mettre `Status: OK` uniquement si les tests et scans
    associes passent ou si le blocker est documente.

- [ ] Task 5 - Verifier backend, qualite et frontend (AC: AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC13, AC14)
  - [ ] Subtask 5.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 5.2 - Executer les tests backend cibles.
  - [ ] Subtask 5.3 - Executer `ruff format .` et `ruff check .`.
  - [ ] Subtask 5.4 - Executer les commandes frontend avec le package manager
    declare par `frontend/package.json` et documenter l'adaptation choisie.

- [ ] Task 6 - Ajouter uniquement les garde-fous manquants si l'audit l'exige (AC: AC2, AC5, AC6, AC11)
  - [ ] Subtask 6.1 - Si un recalcul interdit n'est pas deja garde par test ou
    scan, ajouter un test cible dans le fichier de test owner.
  - [ ] Subtask 6.2 - Ne modifier aucun fichier de production sauf bugfix
    documente et strictement necessaire.
  - [ ] Subtask 6.3 - Documenter tout bugfix avec cause, diff attendu,
    validation et absence de changement de contrat public.

- [ ] Task 7 - Finaliser validation et statut (AC: AC10, AC11, AC12)
  - [ ] Subtask 7.1 - Creer `traditional-advanced-validation.md` avec toutes
    les commandes, resultats, skipped commands, risques et checks.
  - [ ] Subtask 7.2 - Creer `traditional-advanced-final-status.json` avec la
    shape du brief.
  - [ ] Subtask 7.3 - Verifier `python -m json.tool` sur le statut final et
    `Test-Path` sur les six artefacts.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - stories CS-197 a CS-206 comme sources historiques;
  - `regression-guardrails.md` comme registre canonique d'invariants;
  - tests existants listés au Validation Plan;
  - `json_builder.py` uniquement comme sujet d'audit serialize-only;
  - `NatalExpertPanel` uniquement comme sujet d'audit display-only;
  - persistance d'audit existante uniquement comme sujet d'audit persist-only.
- Do not recreate:
  - contrats, DTO, calculateurs, runtime seeds, JSON projection, frontend
    display ou repository audit;
  - listes doctrinales ou mappings locaux;
  - rapports historiques des stories precedentes par duplication non
    referencee.
- Shared abstraction allowed only if:
  - un garde-fou de test manque et l'abstraction retire une duplication
    reelle; aucune abstraction applicative n'est attendue pour cette story.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- broad allowlists
- local doctrine constants in non-owner layers
- LLM/prompt/prediction logic
- production behavior changes

Specific forbidden symbols / paths:

- `sect_legacy`
- `legacy_sect`
- `sect_code`
- `chart_sect_code`
- `planet_sect_code`
- `legacy_hayz`
- `legacy_rejoicing`
- `sect_mitigation_legacy`
- `DIURNAL_PLANETS`
- `NOCTURNAL_PLANETS`
- `BENEFIC_PLANETS`
- `MALEFIC_PLANETS`
- `TRIPLICITY_RULERS`
- `JOY_HOUSES`
- `PLANETARY_JOYS`
- `HAYZ_RULES`
- `ABOVE_HORIZON_HOUSES`
- `BELOW_HORIZON_HOUSES`

Specific forbidden production modifications unless bugfix blocker is documented:

- `backend/app/domain/**`
- `backend/app/services/**`
- `backend/app/infra/**`
- `frontend/src/**`
- `backend/migrations/**`
- `docs/db_seeder/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect | CS-197 dignity sect owner | JSON builder, frontend, persistence, dominance |
| Planet sect condition | CS-198 dignity contract owner | condition profiles, dominance, interpretation adapter, frontend |
| Hayz | CS-199/CS-204 advanced/traditional owners | frontend or JSON derivation |
| Rejoicing | CS-204 dignity/traditional owners | frontend joy constants |
| Triplicity sect-aware | CS-205 essential dignity owner | local triplicity maps |
| Benefic/malefic mitigation | CS-206 advanced condition owner | frontend or JSON builder |
| Public JSON | CS-201 `json_builder.py` | calculators and downstream engines |
| Frontend expert panel | CS-202 frontend display owner | astrology engines |
| Audit persistence | CS-203 chart service / repository owner | recalculation, non-idempotent writes or public payload source |
| Closure evidence | CS-207 evidence directory | console-only notes |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: applicable if chart JSON is represented by OpenAPI,
  Pydantic response models, generated TypeScript clients or schema snapshots.
- Required generated-contract evidence:
  - inspect generated contract ownership during the audit;
  - record no-diff proof or exact reason no generated contract applies in
    `traditional-advanced-validation.md`;
  - no generated route, method, status code or public field change is allowed.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md`
- `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md`
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md`
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- `_condamad/stories/CS-202-natal-expert-panel/00-story.md`
- `_condamad/stories/CS-203-natal-dignity-audit-persistence/00-story.md`
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md`
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md`
- `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/chart/result_service.py`
- `backend/app/infra/db/**`
- `docs/db_seeder/astrology/**`
- `frontend/src/**`
- `docs/**`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/traditional-advanced-audit-report.md` - rapport final.
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/traditional-advanced-contract-map.md` - cartographie des contrats.
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/traditional-advanced-regression-matrix.md` - matrice de regression.
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/traditional-advanced-scan-results.md` - resultats de scans.
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/traditional-advanced-validation.md` - validation.
- `_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/traditional-advanced-final-status.json` - statut final.
- `docs/**` - documentation technique consolidee seulement si un emplacement
  existant est identifie comme owner.

Likely tests:

- no new test expected by default;
- `backend/tests/**` only if a missing guardrail is found;
- `frontend tests` only if a missing frontend guardrail is found.

Files not expected to change:

- `backend/app/domain/**` - no astrology behavior change.
- `backend/app/services/**` - no production service behavior change.
- `backend/app/infra/**` - no persistence behavior change.
- `frontend/src/**` - no functional frontend change.
- `backend/migrations/**` - no migration.
- `docs/db_seeder/**` - no seed change.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Dependency changes are not allowed for CS-207.

## 21. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Required backend tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py
pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py
pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py
pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py
```

Quality:

```powershell
ruff format .
ruff check .
```

Frontend, using the package manager declared by `frontend/package.json`:

```powershell
npm --prefix frontend test -- NatalExpertPanel
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

Required scans:

```powershell
$doctrine = "DIURNAL_PLANETS|NOCTURNAL_PLANETS|BENEFIC_PLANETS|MALEFIC_PLANETS|TRIPLICITY_RULERS|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES"
rg -n $doctrine backend/app frontend -g "*.{py,ts,tsx,js,jsx}"

$legacy = "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|legacy_hayz|legacy_rejoicing|sect_mitigation_legacy"
rg -n $legacy backend/app backend/tests frontend -g "*.{py,ts,tsx,js,jsx}"

$calculators = "SectCalculator|PlanetSectConditionCalculator|AdvancedConditionEngine|EssentialDignityCalculator|AccidentalDignityCalculator|PlanetDignityScoringService"
rg -n $calculators backend/app/services/chart frontend backend/app/infra/db/repositories -g "*.{py,ts,tsx,js,jsx}"

$frontendDerivation = "planet_code\s+in|if .*planet_code|chart_sect\s*==|sun\.house|planet\.house|house_number\s*[<>=]"
rg -n $frontendDerivation frontend -g "*.{ts,tsx,js,jsx}"
```

Evidence checks:

```powershell
$e = "_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence"
Test-Path "$e/traditional-advanced-audit-report.md"
Test-Path "$e/traditional-advanced-contract-map.md"
Test-Path "$e/traditional-advanced-regression-matrix.md"
Test-Path "$e/traditional-advanced-scan-results.md"
Test-Path "$e/traditional-advanced-validation.md"
Test-Path "$e/traditional-advanced-final-status.json"
python -m json.tool "$e/traditional-advanced-final-status.json"
```

Story validation commands:

```powershell
$story = "_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in `traditional-advanced-validation.md`
  with exact command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: documentation closes the story while a recalculation remains hidden.
  - Guardrail: required scans plus classification of every hit.
- Risk: a score drift is missed because only JSON shape is checked.
  - Guardrail: targeted scoring, golden case, profile, dominance and adapter
    tests plus regression matrix.
- Risk: frontend display logic becomes doctrine.
  - Guardrail: frontend scans and `NatalExpertPanel` tests.
- Risk: audit persistence becomes a second calculator.
  - Guardrail: forbidden calculator scans and chart result service tests.
- Risk: old evidence is copied without validating current repo state.
  - Guardrail: CS-207 validation must record current command results.
- Risk: final status JSON says `passed` without proof.
  - Guardrail: `traditional-advanced-validation.md` must list all commands and
    blockers before status is set to passed.

## 23. Dev Agent Instructions

- Implement only CS-207.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- Do not preserve legacy behavior for convenience.
- Treat CS-197 through CS-206 as canonical unless a blocker is documented.
- Do not add new astrology features.
- Do not change scoring.
- Do not change public JSON.
- Do not change frontend behavior.
- Do not change routes, methods, status codes, migrations, seeds or
  dependencies.
- Prefer documentation and evidence.
- Add tests only if a guardrail is missing.
- Any production code change must be documented as a bugfix with exact reason,
  tests and no public contract change.
- Do not introduce compatibility aliases, shims, broad allowlists or fallback
  behavior.
- Do not introduce local doctrine constants.
- Do not call LLM or prediction services.
- Do not mark complete without final status JSON.
- Do not mark `validation_status: "passed"` until all required validations have
  passed or blockers have been resolved.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO or hidden residual in-domain work.

## 24. References

- `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md` - chart
  sect contract.
- `_condamad/stories/CS-198-planet-sect-condition-normalization/00-story.md` -
  per-planet sect condition contract.
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md` -
  sect-aware advanced scoring.
- `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md` -
  traditional golden cases.
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md` -
  public JSON projection.
- `_condamad/stories/CS-202-natal-expert-panel/00-story.md` - frontend expert
  panel.
- `_condamad/stories/CS-203-natal-dignity-audit-persistence/00-story.md` -
  dignity audit persistence.
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md`
  - hayz and rejoicing contracts.
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` -
  sect-aware triplicity golden cases.
- `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/00-story.md`
  - benefic/malefic mitigation signals.
- `_condamad/stories/regression-guardrails.md` - applicable invariants
  `RG-124` through `RG-134`.
- `backend/app/services/chart/json_builder.py` - public JSON projection owner.
- `frontend` - expert panel display owner.
- `backend/app/infra/db` - audit persistence layer.
