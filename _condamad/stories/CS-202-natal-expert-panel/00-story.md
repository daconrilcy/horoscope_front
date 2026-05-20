# Story CS-202 natal-expert-panel: Afficher un panneau expert du theme natal depuis le JSON public

Status: done

## 1. Objective

Créer une première surface frontend experte qui affiche les blocs natals
avancés exposés par CS-201 depuis le JSON public, sans déplacer ni recréer de
calcul astrologique côté React.

Le panneau doit lire, formater, grouper et afficher des faits techniques déjà
présents dans le payload public: secte du thème, condition de secte par
planète, hayz, out-of-sect, joies, dignités, profils conditionnels, signaux,
conditions avancées, dominantes et adaptation interprétative factuelle.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-20 pour CS-202, follow-up de CS-197, CS-198, CS-199, CS-200 et CS-201.
- Reason for change: le backend expose une projection JSON publique stable, mais le frontend ne propose pas encore de panneau expert consommant ces blocs avancés.
- Selected story writer mode: Repo-informed story.

## 3. Domain Boundary

Cette story appartient à un seul domaine:

- Domain: `frontend`
- In scope:
  - auditer le flux frontend existant du thème natal: route `/natal`,
    hook `useLatestNatalChart`, types `LatestNatalChart`, états UI et tests;
  - ajouter ou mettre à jour les types TypeScript du payload natal public CS-201 dans le domaine API frontend existant;
  - créer un composant `NatalExpertPanel` ou équivalent selon la convention locale;
  - afficher les blocs publics existants: `dignities`, `dignities.sect`,
    `sect_condition`, profils, signaux, conditions avancées, dominantes et
    `interpretation_adapter`;
  - intégrer le panneau dans la page natale sans remplacer le résumé utilisateur ni l'interprétation existante;
  - couvrir les états présent, présent vide, indisponible sans heure fiable, absent d'un ancien payload, loading et error;
  - produire les preuves persistantes sous `_condamad/stories/CS-202-natal-expert-panel/evidence/`.
- Out of scope:
  - modifier le calcul backend, `json_builder.py`, les routes API, les
    contrats backend, les migrations, les seeds, la persistance ou les moteurs;
  - recalculer secte, hayz, out-of-sect, joies, dignités, dominantes, conditions ou signaux côté frontend;
  - générer une interprétation narrative, appeler un LLM ou transformer `interpretation_adapter` en conseil personnalisé;
  - ajouter une nouvelle route API, un nouveau mécanisme de permission backend ou une compatibilité legacy.
- Explicit non-goals:
  - ne pas inférer la secte depuis le Soleil, les maisons, les signes, les positions ou les codes planètes;
  - ne pas inférer `in_sect`, `out_of_sect`, hayz, rejoicing, dominantes, chart ruler, angularité ou signaux depuis des constantes frontend;
  - ne pas introduire `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy` ou `legacy_planet_sect`;
  - ne pas masquer les champs absents par de faux defaults;
  - ne pas contourner `RG-108`, `RG-112`, `RG-118`, `RG-119`, `RG-120`, `RG-121`, `RG-122`, `RG-123`, `RG-124`, `RG-125`, `RG-126`, `RG-127`, `RG-128` ou `RG-129`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Brief archetype: public-contract-consumption
- Archetype reason: la story consomme une surface publique backend stabilisée par CS-201 sans changer la source de vérité ni le contrat API.
- Archetype adaptation: `public-contract-consumption` est le libellé du brief; `custom` est l'archetype CONDAMAD valide car la story est une intégration UI de contrat public.
- Additional validation rules:
  - les tests composants doivent prouver le rendu depuis les champs du payload public;
  - les scans statiques doivent prouver l'absence de calcul astrologique frontend;
  - le diff des chemins backend interdits doit rester vide.
- Behavior change allowed: constrained
- Behavior change constraints:
  - le backend reste inchangé;
  - le frontend affiche des faits calculés par le backend;
  - les routes existantes sont réutilisées;
  - les blocs absents ou indisponibles sont affichés comme indisponibles, vides ou manquants selon le cas, jamais recalculés;
  - les textes restent techniques et factuels.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if:
  - un champ requis du payload CS-201 est absent et empêcherait l'affichage
    sans dérivation frontend;
  - l'accès au panneau doit être restreint sans mécanisme existant.

## 4a. Required Contracts

La story doit persister les contrats sélectionnés depuis l'archétype et le
périmètre de story.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le frontend doit consommer `GET /v1/users/me/natal-chart/latest` ou le service existant, pas reconstruire les faits. |
| Baseline Snapshot | yes | Le flux actuel et un sample public doivent être capturés avant l'ajout du panneau. |
| Ownership Routing | yes | Le calcul reste backend; le frontend possède seulement la présentation et les états UI. |
| Allowlist Exception | no | Aucune exception large, alias legacy ou fallback doctrinal n'est autorisé. |
| Contract Shape | yes | Les types frontend doivent refléter les blocs CS-201 avec nullabilité/absence explicite. |
| Batch Migration | no | La story ne migre pas plusieurs surfaces concurrentes. |
| Reintroduction Guard | yes | Des scans doivent empêcher le retour de constantes ou calculs astrologiques frontend. |
| Persistent Evidence | yes | Audits, payload sample, validations et scans doivent être conservés dans le dossier de story. |

Brief-level contract requirements not represented as CONDAMAD contract names:

- Public Payload Source of Truth: les faits affichés proviennent du JSON public uniquement.
- Empty State Contract: les états vide, absent et indisponible doivent rester distinguables.
- UI Snapshot / Rendering Evidence: le rendu du panneau doit être prouvé par tests et, si possible, capture.

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `GET /v1/users/me/natal-chart/latest`;
  - hook/service frontend existant `useLatestNatalChart()` dans `frontend/src/api/natal-chart/index.ts`;
  - payload `LatestNatalChart.result` et champs publics CS-201.
- Runtime artifact:
  - rendu de `NatalExpertPanel` à partir d'un fixture public sanitizé;
  - test de la page natale prouvant que le panneau consomme `latestChart.data`;
  - sample `_condamad/stories/CS-202-natal-expert-panel/evidence/public-payload-sample-before.json`.
  - AST guard/static scan over `frontend` for forbidden astrology constants and derivation patterns:
    garde AST ou scan statique sur `frontend` pour les constantes astrologiques
    et patrons de dérivation interdits.
- Secondary evidence:
  - tests Vitest/Testing Library du panneau;
  - typecheck TypeScript;
  - scans anti-calcul frontend;
  - diff backend ciblé prouvant l'absence de changement sur les surfaces interdites.
- Static scans alone are not sufficient for this story because:
  les scans statiques seuls ne suffisent pas pour cette story:
  - l'absence de constantes ne prouve pas que les blocs publics sont rendus;
  - les états absent/vide/no-time doivent être validés par comportement de rendu.

## 4c. Baseline / Before-After Rule

- Required evidence directory:
  - `_condamad/stories/CS-202-natal-expert-panel/evidence/`
- Baseline artifact before implementation:
  - `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-before.md`
  - `_condamad/stories/CS-202-natal-expert-panel/evidence/public-payload-sample-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-after.md`
  - `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-validation.md`
- Optional artifact:
  - `_condamad/stories/CS-202-natal-expert-panel/evidence/expert-panel-screenshot.png`
- Required baseline questions:
  - où le dernier thème natal est récupéré;
  - où le payload est typé;
  - où les sections natales sont rendues;
  - s'il existe un panneau expert/debug/technique;
  - quels blocs avancés sont ignorés;
  - comment le mode sans heure est représenté.
- Expected invariant:
  - backend payload shape unchanged;
  - frontend consumes existing fields;
  - aucun calcul astrologique n'est introduit;
  - UI displays technical facts or unavailable states.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Frontend role | Forbidden destination |
|---|---|---|---|
| Latest natal chart retrieval | `frontend/src/api/natal-chart/index.ts` | reuse hook/service | duplicate fetch layer |
| Chart sect | backend `dignities.sect` | display | React inference from Sun/houses |
| Planet sect condition | backend `dignities.planets[*].sect_condition` | display/group by explicit fields | planet doctrine constants |
| Hayz / out-of-sect / advanced facts | backend `advanced_conditions` | display | recomputation in component/hook |
| Scores et détails de dignité | backend `dignities.planets` | affichage | règles locales de score |
| Condition profiles | backend `planet_condition_profiles` | display | local thresholds |
| Signaux conditionnels | backend `planet_condition_signals` | affichage de champs factuels | prompt/génération narrative |
| Dominant planets | backend `dominant_planets` | display | chart ruler/angularity scoring |
| Adaptateur interprétatif | backend `interpretation_adapter` | affichage de tableaux factuels | appel LLM ou génération de prose |
| Empty/missing/unavailable states | frontend | render safely | fake defaults |
| Layout visuel et CSS | frontend | présentation | styles inline |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason:
  - no broad allowlist, legacy alias, doctrinal fallback or compatibility path
    is allowed;
  - tout hit de scan conservé pour affichage direct doit être exact et
    documenté dans la validation.

## 4f. Contract Shape

- Contract type:
  - existing public chart JSON payload returned by `GET /v1/users/me/natal-chart/latest`.
- Fields:
  - `ChartSectResult`;
  - `PlanetSectCondition`;
  - `DignityPlanetPayload`;
  - `DignitiesPayload`;
  - `PlanetConditionProfile`;
  - `PlanetConditionSignal`;
  - `AdvancedCondition`;
  - `DominantPlanetsResult`;
  - `InterpretationAdapterResult`;
  - `NatalChartPayload` / `LatestNatalChart.result` equivalent.
- Required fields:
  - `dignities.sect.chart_sect`, `sun_horizon_position`, `sun_above_horizon`, `calculation_basis`, `reference_system`;
  - `dignities.planets[*].sect_condition` fields: `planet_code`,
    `chart_sect`, `intrinsic_sect`, `planet_sect_condition`, booleans, basis
    et système de référence;
  - scores `dignities.planets[*]` et `essential_breakdown` /
    `accidental_breakdown`;
  - axes `planet_condition_profiles`, `ranking_score` et `condition_level`;
  - `planet_condition_signals` technical fields except `prompt_hint` unless an existing debug/developer mode already exists;
  - tableaux et maps factuels `advanced_conditions`, `dominant_planets` et
    `interpretation_adapter`.
- UI fields expected by the initial brief:
  - `planet_condition_profiles`: `functional_strength`, `visibility`,
    `stability`, `intensity`, `coherence`, `support`, `constraint`,
    `ranking_score`, `condition_level`;
  - `planet_condition_signals`: `code`, `label`, `axis`, `level`,
    `axis_value`, `interpretation_use`, `priority_weight`, `prompt_hint`;
  - `dominant_planets`: `top_planet_code`, `chart_ruler_code`,
    `most_elevated_planet_code`, `planets[*].score`, `planets[*].rank`,
    `planets[*].factors`;
  - `interpretation_adapter`: `activated_themes`, `dominant_topics`,
    `dominant_axes`, `tension_patterns`, `support_patterns`,
    `critical_patterns`, `narrative_priorities`.
- Optional fields:
  - fields may be optional only when old persisted payloads or degraded/no-time modes can genuinely omit them;
  - distinguer `undefined`, `null`, `[]` et `{}` selon la convention existante
    du projet.
- Status codes:
  - no HTTP endpoint, method or HTTP status code is modified by this story.
- Serialization names:
  - preserve backend snake_case public names;
  - ne pas créer d'alias comme `sectCode`, `legacySect` ou `planetSectCode`.
- Frontend type impact:
  - les types frontend manuels doivent être étendus dans l'owner existant des
    types API natals, ou les types générés doivent être régénérés si le projet
    utilise des contrats générés.
- Generated contract impact:
  - inspect whether generated frontend types exist; if none, document that manual types are the contract owner in `frontend-expert-panel-before.md`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: la story ajoute un panneau expert et les types/tests associés; elle
  ne migre pas de lots de fichiers ni de contrats publics.

## 4g.1 Target UI Structure

Le panneau expert doit suivre la structure du brief initial, sauf adaptation à
la convention UI existante:

- Secte du thème:
  - source: `dignities.sect`;
  - champs: `chart_sect`, `sun_horizon_position`, `sun_above_horizon`,
    `calculation_basis`, `reference_system`;
  - aucune inférence depuis Soleil, maisons, signes ou positions.
- Condition de secte des planètes:
  - source: `dignities.planets[*].sect_condition`;
  - groupes: dans leur secte, hors secte, neutres/variables/inconnues;
  - grouping uniquement depuis `is_in_sect`, `is_out_of_sect` et
    `planet_sect_condition`.
- Conditions avancées:
  - source: `advanced_conditions`;
  - afficher au minimum les faits présents pour `hayz`, `out_of_sect`,
    rejoicing/joy, mutual reception, vitesse/station, conditions héliaques,
    maltreatment, bonification et besiegement;
  - groupement autorisé seulement par `condition_code` ou `condition_type`
    déjà présent.
- Dignités planétaires:
  - source: `dignities.planets`;
  - afficher scores essentiels/accidentels/totaux, axes fonctionnels et
    breakdowns disponibles.
- Profils conditionnels:
  - source: `planet_condition_profiles`;
  - afficher les axes techniques et `condition_level` sans interpréter de
    seuil local.
- Signaux conditionnels:
  - source: `planet_condition_signals`;
  - afficher des champs techniques; masquer `prompt_hint` hors mode
    technique/debug existant si le libellé semble interne.
- Planètes dominantes:
  - source: `dominant_planets`;
  - afficher les rangs, scores, facteurs et codes fournis sans calculer chart
    ruler, planète élevée, angularité ou centralité.
- Adaptation interprétative factuelle:
  - source: `interpretation_adapter`;
  - afficher les faits structurés sans prose, conseil personnalisé ou appel LLM.

## 4h. Persistent Evidence Artifacts

Required artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before audit | `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-before.md` | Documenter le flux frontend actuel et les blocs avancés ignorés. |
| Public payload sample | `_condamad/stories/CS-202-natal-expert-panel/evidence/public-payload-sample-before.json` | Preserve sanitized CS-201 payload shape. |
| After audit | `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-after.md` | Documenter l'UI implémentée, les fichiers modifiés et le comportement. |
| Validation record | `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-validation.md` | Enregistrer commandes, scans et preuve backend inchangé. |

- `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-before.md`
- `_condamad/stories/CS-202-natal-expert-panel/evidence/public-payload-sample-before.json`
- `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-after.md`
- `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-validation.md`

L'artefact de validation doit inclure:

- commands run;
- frontend tests result;
- backend regression tests result;
- typecheck result;
- lint result;
- scan results;
- allowed scan hits;
- screenshot/rendered output note;
- confirmation that backend was not changed;
- confirmation qu'aucun calcul astrologique n'a été ajouté au frontend.

## 4i. Reintroduction Guard

- Guard type:
  - scans statiques sur `frontend` pour les constantes, noms legacy et patrons
    logiques interdits;
  - component tests proving grouping uses explicit booleans;
  - backend diff check over forbidden backend paths.
- Forbidden frontend doctrine constants:
  - `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`, `SECT_PLANETS`,
    `DAY_SECT_PLANETS`, `NIGHT_SECT_PLANETS`, `ABOVE_HORIZON_HOUSES`,
    `BELOW_HORIZON_HOUSES`, `JOY_HOUSES`, `PLANETARY_JOYS`, `HAYZ_RULES`.
- Forbidden frontend logic patterns:
  - `sun.house`, `sun_house`, `planet.house`, `house_number >=`,
    `house_number <=`, `planet_code in`, `includes(planet_code)`, `isHayz`,
    `hayz =`, `chart_sect ===`, `chartSect ===`, `sun_above_horizon &&`,
    `is_in_sect &&`.
- Conditional allowed hits:
  - la sélection d'un libellé d'affichage pour une valeur fournie par le backend
    peut être acceptée seulement si elle est documentée avec fichier, ligne et raison.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/app/routes.tsx` - route `/natal` charge `NatalChartPage`.
- Evidence 2: `frontend/src/api/natal-chart/index.ts` - `useLatestNatalChart()`
  consomme `/v1/users/me/natal-chart/latest`; `LatestNatalChart` type les
  blocs natals de base.
- Evidence 3: `frontend/src/pages/NatalChartPage.tsx` - la page rend positions,
  maisons, aspects, guide, interprétation et états loading/error/no-data.
- Evidence 4: `frontend/src/features/natal-chart/NatalInterpretation.tsx` -
  l'interprétation existante est séparée du rendu du chart public.
- Evidence 5: `frontend/src/tests/NatalChartPage.test.tsx` and `frontend/src/tests/natalChartApi.test.tsx` - tests existants pour la page et l'API natale.
- Evidence 6: `frontend/src/components/ui/EmptyState`, `ErrorState`,
  `Skeleton`, `Card` - composants UI existants à inspecter/réutiliser.
- Evidence 7: `frontend/package.json` - scripts existants: `npm test`, `npm run lint`, `npm run build`.
- Evidence N: `_condamad/stories/regression-guardrails.md` - invariants de régression partagés consultés avant cadrage.

Assumptions to verify during implementation:

- aucun type généré OpenAPI dédié au chart natal n'existe actuellement côté frontend;
- aucun panneau expert/debug natal réutilisable n'existe déjà;
- les blocs CS-201 sont disponibles sous `LatestNatalChart.result` ou une propriété équivalente du payload public.

## 6. Target State

After implementation:

- la page natale expose une section ou un panneau expert technique sans remplacer les surfaces utilisateur existantes;
- `dignities.sect` est rendu en tant que contrat chart-level explicite;
- les conditions de secte planétaires sont groupées uniquement via `is_in_sect`, `is_out_of_sect` et `planet_sect_condition`;
- `advanced_conditions` affiche hayz, out-of-sect et autres conditions déjà présentes;
- les scores et breakdowns de dignités sont visibles par planète;
- les profils, signaux, dominantes et faits d'adaptation interprétative sont affichés sans prose générée;
- les états absent, vide et indisponible sans heure fiable sont distincts;
- les preuves persistantes démontrent que le backend n'a pas changé et que le frontend ne calcule pas d'astrologie.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - les données de référence runtime ne doivent pas être recréées en constantes locales frontend.
  - `RG-112` - les constantes et fallbacks astrologiques ne doivent pas revenir dans le frontend ou le backend.
  - `RG-118` - les dignités planétaires restent des faits backend et ne deviennent pas des règles UI.
  - `RG-119` - les profils conditionnels restent backend et ne deviennent pas des seuils frontend.
  - `RG-120` - les signaux conditionnels restent gouvernés par le runtime/backend, pas par des seuils UI.
  - `RG-121` - les dominantes planétaires restent calculées par le backend.
  - `RG-122` - les conditions avancées restent calculées par le backend.
  - `RG-123` - l'adaptateur interprétatif reste factuel et non narratif.
  - `RG-124` - `dignities.sect` reste le contrat canonique de secte chart-level.
  - `RG-125` - `dignities.planets[*].sect_condition` reste le contrat canonique par planète.
  - `RG-126` - hayz et out-of-sect restent dérivés par les moteurs backend.
  - `RG-127` - les golden cases traditionnels restent stables.
  - `RG-128` - la projection JSON publique reste une projection backend sans calcul.
  - `RG-129` - le frontend ne calcule pas d'astrologie depuis le payload natal public.
- Non-applicable invariants:
  - API route guardrails hors natal - this story does not add, remove, mount or rename backend routes.
  - DB/migration guardrails - this story does not change persistence, migrations or seeds.
- Required regression evidence:
  - component tests for expert panel rendering and explicit-boolean grouping;
  - frontend typecheck/lint/build;
  - forbidden frontend scans;
  - targeted backend regression tests from CS-201;
  - backend forbidden-path diff check.
- Allowed differences:
  - new frontend UI, CSS, types and tests;
  - new persistent evidence files;
  - no backend JSON shape, calculation or route change.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Rend `dignities.sect` sans valeur inférée. | Evidence profile: `json_contract_shape`; `npm test -- NatalExpertPanel`. |
| AC2 | Rend `sect_condition` par planète. | Evidence profile: `json_contract_shape`; `npm test -- NatalExpertPanel`. |
| AC3 | Groupe in/out-of-sect depuis champs explicites. | Evidence profile: `reintroduction_guard`; `npm test -- NatalExpertPanel`; `rg -n "DIURNAL_PLANETS" frontend`. |
| AC4 | Rend hayz/out-of-sect depuis `advanced_conditions`. | Evidence profile: `json_contract_shape`; `npm test -- NatalExpertPanel`. |
| AC5 | Rend les synthèses de score de dignité par planète. | Evidence profile: `json_contract_shape`; `npm test -- NatalExpertPanel`. |
| AC6 | Rend les champs techniques des profils conditionnels. | Evidence profile: `json_contract_shape`; `npm test -- NatalExpertPanel`. |
| AC7 | Rend les classements des planètes dominantes. | Evidence profile: `json_contract_shape`; `npm test -- NatalExpertPanel`. |
| AC8 | Rend `interpretation_adapter` sans prose. | Evidence profile: `reintroduction_guard`; `npm test -- NatalExpertPanel`; `rg -n "OpenAI|AIEngineAdapter" frontend/src`. |
| AC9 | Les états de payload indisponible rendent des fallbacks factuels. | Evidence profile: `json_contract_shape`; `npm test -- NatalExpertPanel`. |
| AC10 | Forbidden astrology symbols are absent from frontend. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg` scans from Validation Plan. |
| AC11 | Backend CS-201 regression suite passes. | Evidence profile: `json_contract_shape`; `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC12 | Evidence before/after/validation enregistrée. | Evidence profile: `baseline_before_after_diff`; `rg -n "validation" _condamad/stories/CS-202-natal-expert-panel`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inspecter le flux frontend et capturer la baseline (AC: AC9, AC12)
  - [ ] Subtask 1.1 - Inspecter `frontend/package.json`,
    `frontend/src/app/routes.tsx`, `frontend/src/pages/NatalChartPage.tsx`,
    `frontend/src/api/natal-chart/index.ts`, components, tests and UI states.
  - [ ] Subtask 1.2 - Créer `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-before.md`.
  - [ ] Subtask 1.3 - Créer `_condamad/stories/CS-202-natal-expert-panel/evidence/public-payload-sample-before.json`.

- [ ] Task 2 - Étendre les types frontend du payload natal (AC: AC1, AC2, AC5, AC6, AC7, AC8, AC9)
  - [ ] Subtask 2.1 - Ajouter ou mettre à jour les types manuels/générés pour
    secte, dignités planétaires, profils, signaux, conditions avancées,
    dominantes et `interpretation_adapter`.
  - [ ] Subtask 2.2 - Préserver les noms publics snake_case et les conventions
    exactes de nullabilité/absence.

- [ ] Task 3 - Construire les composants du panneau expert (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9)
  - [ ] Subtask 3.1 - Créer `NatalExpertPanel` avec des sous-composants ciblés:
    chart sect, planet sect table, advanced conditions, dignity breakdown,
    profils, signaux, dominantes et faits `interpretation_adapter`.
  - [ ] Subtask 3.2 - Implémenter le grouping uniquement depuis les champs backend explicites.
  - [ ] Subtask 3.3 - Implémenter les états vide/manquant/sans heure sans recalcul ni faux defaults.
  - [ ] Subtask 3.4 - Ajouter le CSS dans le fichier `.css` approprié, sans
    styles inline et avec réutilisation des variables/tokens existants.

- [ ] Task 4 - Ajouter le point d'entrée du panneau expert (AC: AC1, AC9)
  - [ ] Subtask 4.1 - Intégrer le panneau dans `NatalChartPage` ou la structure natale existante.
  - [ ] Subtask 4.2 - Conserver les sections résumé, guide et interprétation existantes.

- [ ] Task 5 - Ajouter les tests (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10)
  - [ ] Subtask 5.1 - Ajouter des tests de rendu `NatalExpertPanel` couvrant le payload complet et chaque bloc avancé.
  - [ ] Subtask 5.2 - Ajouter des fixtures pour blocs manquants, blocs vides, sans heure et ancien payload.
  - [ ] Subtask 5.3 - Ajouter ou mettre à jour les tests page-level prouvant l'accès depuis la page natale.

- [ ] Task 6 - Ajouter et enregistrer les gardes anti-calcul (AC: AC3, AC10, AC11, AC12)
  - [ ] Subtask 6.1 - Exécuter les scans frontend interdits et documenter les hits autorisés.
  - [ ] Subtask 6.2 - Exécuter le diff check des chemins backend interdits.
  - [ ] Subtask 6.3 - Exécuter les tests backend ciblés sous venv activé.

- [ ] Task 7 - Finaliser l'evidence (AC: AC11, AC12)
  - [ ] Subtask 7.1 - Créer `frontend-expert-panel-after.md`.
  - [ ] Subtask 7.2 - Créer `frontend-expert-panel-validation.md` avec commandes, résultats, scans et hits autorisés.
  - [ ] Subtask 7.3 - Capturer une capture optionnelle si la convention projet et le setup local le permettent.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/api/natal-chart/index.ts` for latest natal chart API access;
  - existing `LatestNatalChart` / natal API type location for contract typing;
  - `frontend/src/pages/NatalChartPage.tsx` / `frontend/src/features/natal-chart` layout conventions;
  - existing `@ui` components such as `Card`, `EmptyState`, `ErrorState`, `Skeleton` when compatible;
  - existing CSS variables, spacing, border and color tokens before creating new ones;
  - existing i18n conventions if the page copy is localized.
- Do not recreate:
  - chart calculation;
  - sect calculation;
  - planet sect classification;
  - hayz logic;
  - rejoicing logic;
  - dignity scoring;
  - signal thresholds;
  - dominance scoring;
  - interpretation adapter rules.
- Shared abstraction allowed only if:
  - it removes real duplication across expert panel subcomponents or follows an existing UI helper pattern.
- Allowed frontend transformations:
  - trier pour l'affichage par `rank`, `priority_weight`, `planet_code` ou
    ordre du payload;
  - grouper par booléens explicites ou codes explicites du payload;
  - formater des nombres et mapper des codes vers des libellés d'affichage via
    la convention i18n/display-label existante.
- Not allowed:
  - mapper des codes vers une nouvelle doctrine;
  - dériver des faits absents du payload;
  - utiliser des listes de planètes pour inférer secte, nature ou dignité.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers;
- transitional aliases;
- legacy imports;
- duplicate active implementations;
- silent fallback behavior;
- frontend doctrinal constants;
- backend contract or projection changes for convenience;
- inline styles.

Specific forbidden frontend symbols:

- `sect_legacy`
- `legacy_sect`
- `sect_code`
- `chart_sect_code`
- `planet_sect_code`
- `planet_sect_legacy`
- `sect_score_legacy`
- `legacy_planet_sect`
- `DIURNAL_PLANETS`
- `NOCTURNAL_PLANETS`
- `SECT_PLANETS`
- `DAY_SECT_PLANETS`
- `NIGHT_SECT_PLANETS`
- `ABOVE_HORIZON_HOUSES`
- `BELOW_HORIZON_HOUSES`
- `JOY_HOUSES`
- `PLANETARY_JOYS`
- `HAYZ_RULES`
- `chart_sect ===`
- `chartSect ===`

Specific forbidden backend paths to modify unless a blocker is documented:

- `backend/app/domain/astrology/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `migrations/**`
- `docs/db_seeder/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chart sect | backend `dignities.sect` | frontend derivation from Sun/houses/signs |
| Planet sect condition | backend `sect_condition` | frontend planet doctrine constants |
| Hayz / out-of-sect | backend `advanced_conditions` | frontend recomputation |
| Rejoicing | backend dignity / advanced condition payload | frontend house/joy constants |
| Dignity scores | backend `dignities.planets` | frontend scoring rules |
| Condition profiles | backend `planet_condition_profiles` | frontend thresholds |
| Condition signals | backend `planet_condition_signals` | frontend signal rules |
| Dominants | backend `dominant_planets` | frontend ruler/angularity scoring |
| Interpretation adapter | backend `interpretation_adapter` | frontend LLM/prose generation |
| Empty states | frontend | backend change for display convenience |
| Visual layout | frontend | backend payload change for UI formatting |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: applicable if generated frontend/OpenAPI contracts exist.
- Required generated-contract evidence:
  - inspect generated API/type locations before editing;
  - if no generated chart contract exists, record this in `frontend-expert-panel-before.md`;
  - si des types générés existent, les régénérer ou les mettre à jour selon la
    convention du projet et enregistrer la commande/le résultat.

## 17. Files to Inspect First

Codex doit inspecter avant édition:

- `frontend/package.json`
- `frontend/src/app/routes.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/ui/EmptyState`
- `frontend/src/components/ui/ErrorState`
- `frontend/src/components/ui/Card`
- `frontend/src/components/ui/Skeleton`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`

## 18. Expected Files to Modify

Likely files:

- `frontend/src/api/natal-chart/index.ts` - extend public natal payload types if manual types remain colocated there.
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - new expert panel component.
- `frontend/src/features/natal-chart/NatalExpertPanel.css` or appropriate existing CSS file - panel styles without inline styles.
- `frontend/src/pages/NatalChartPage.tsx` - add panel entry point.
- `frontend/src/i18n/natalChart.ts` - add factual UI copy if the project localizes natal page copy.

Likely tests:

- `frontend/src/tests/NatalExpertPanel.test.tsx` - component rendering, grouping and empty states.
- `frontend/src/tests/NatalChartPage.test.tsx` - integration reachability from `/natal`.
- `frontend/src/tests/natalChartApi.test.tsx` - type/API payload expectations.

Evidence files:

- `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-before.md`
- `_condamad/stories/CS-202-natal-expert-panel/evidence/public-payload-sample-before.json`
- `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-after.md`
- `_condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-validation.md`

Files not expected to change:

- `backend/app/domain/astrology/**` - calculation owners remain unchanged.
- `backend/app/services/chart/json_builder.py` - public projection already stabilized by CS-201.
- `backend/app/api/**` - no route or schema change expected.
- `backend/app/infra/**` - no persistence or client change expected.
- `migrations/**` - no database change.
- `docs/db_seeder/**` - no seed/reference change.

## 19. Dependency Policy

- New dependencies: none by default.
- Justification: le panneau peut être construit avec React, les composants UI
  existants, le CSS et l'outillage de test existant; ajouter des packages
  élargirait le scope sans capacité requise.
- Les changements de dépendances frontend ne sont pas autorisés sauf si
  l'implémentation découvre qu'une dépendance standard du projet manque et
  documente un blocker pour décision utilisateur.
- Backend dependency changes: forbidden.
- Dépendances LLM, prediction, charting ou table-library: interdites sauf si
  elles sont déjà utilisées et explicitement justifiées dans l'evidence.

## 20. Validation Plan

Run or justify why skipped:

```powershell
npm --prefix frontend test -- NatalExpertPanel
npm --prefix frontend run lint
npm --prefix frontend run build
```

Le script `frontend` ne déclare pas `typecheck`; le typecheck est couvert par
`npm --prefix frontend run lint`, qui exécute `tsc --noEmit` sur les configs de lint et Node.

Les commandes de régression backend doivent être exécutées après activation du venv:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
```

Frontend anti-calculation scans:

```powershell
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sun\.house|sun_house|planet\.house|house_number\s*[<>=]|planet_code\s+in" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "includes\(planet_code\)|isHayz|hayz\s*=|chart_sect ===|chartSect ===" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "sun_above_horizon\s*&&|is_in_sect\s*&&" frontend -g "*.{ts,tsx,js,jsx}"
rg -n "OpenAI|AIEngineAdapter|prompt_hint|personalized|conseil" frontend/src
```

Backend no-change scan:

```powershell
git diff -- backend/app/domain/astrology backend/app/services/chart/json_builder.py backend/app/api backend/app/infra migrations docs/db_seeder
```

Evidence checks:

```powershell
Test-Path _condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-before.md
Test-Path _condamad/stories/CS-202-natal-expert-panel/evidence/public-payload-sample-before.json
Test-Path _condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-after.md
Test-Path _condamad/stories/CS-202-natal-expert-panel/evidence/frontend-expert-panel-validation.md
rg -n "dignities|sect_condition|hayz|out_of_sect|advanced_conditions" _condamad/stories/CS-202-natal-expert-panel/evidence
rg -n "dominant_planets|interpretation_adapter|aucun calcul astrologique|no astrology calculation" _condamad/stories/CS-202-natal-expert-panel/evidence
```

Les commandes de validation de story doivent être exécutées après activation du venv:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-202-natal-expert-panel/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-202-natal-expert-panel/00-story.md
```

## 21. Regression Risks

- Risk: astrology logic leaks into frontend.
  - Guardrail: forbidden scans, component tests based on explicit payload fields and `RG-129`.
- Risk: planets are grouped by doctrine lists instead of backend booleans.
  - Guardrail: unusual/reordered planet fixture and scan for planet-code doctrine constants.
- Risk: missing or old payload crashes `/natal`.
  - Guardrail: tests for missing, empty and no-time unavailable states.
- Risk: `prompt_hint` becomes user-facing interpretation.
  - Guardrail: tests and copy review proving factual display only or hidden internal hint.
- Risk: backend changes are introduced to satisfy UI convenience.
  - Guardrail: backend forbidden-path diff and CS-201 regression tests.
- Risk: CSS introduces inline styles or duplicates tokens.
  - Guardrail: existing inline-style policy tests/scans and CSS token reuse review.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Treat CS-201 public JSON as canonical.
- Do not modify backend calculation, projection, API routes, migrations, seeds or persistence.
- Do not add frontend astrology calculations, planet doctrine constants, score thresholds or compatibility aliases.
- Ne pas ajouter d'appels LLM, de génération narrative ou de conseils
  personnalisés depuis `interpretation_adapter`.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in the validation evidence.
  En pratique: arrêter et enregistrer le blocker dans l'evidence de validation.
- Si un champ requis manque au payload public, arrêter et documenter le blocker
  au lieu de le dériver dans le frontend.
- Do not preserve legacy behavior for convenience.
- Ne pas marquer la story complète sans fichiers d'evidence et commandes de validation.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work.

## 23. References

- `CS-197 sect-audit-explicit-contract` - chart-level sect contract.
- `CS-198 planet-sect-condition-normalization` - per-planet sect condition contract.
- `CS-199 advanced-sect-scoring-integration` - advanced sect scoring ownership.
- `CS-200 hellenistic-medieval-golden-cases` - golden case stability.
- `CS-201 natal-public-json-projection-cleanup` - public JSON source of truth for this story.
- `_condamad/stories/regression-guardrails.md` - applicable invariants and new `RG-129`.
