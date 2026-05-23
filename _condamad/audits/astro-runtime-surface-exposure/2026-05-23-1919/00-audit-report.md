# Audit Report - Astro Runtime Surface Exposure

## Audit Scope

- Domain key: `astro-runtime-surface-exposure`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend astrology runtime surface exposure decisions only.
- Output folder: `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/`

## Closure Analysis

- Prior same-domain audit folders consulted: none; E-004 found no previous `_condamad/audits/astro-runtime-surface-exposure` folder.
- Story keys consulted: `CS-238-audit-runtime-surface-exposure`, sibling audit story `CS-237-audit-astrology-engine-feature-coverage`, and recent runtime guardrail stories through `RG-141` to `RG-148`.
- Active findings after current evidence: F-001, F-002, F-003.
- Closed prior findings: none for this domain.
- Guardrails mapped: RG-141 to RG-148 protect internal runtime ownership for advanced conditions, `ChartObjectRuntimeData`, fixed stars, dignity and dominance payloads; RG-002 and RG-022 are local anti-drift guards for no API changes and concrete validation paths.
- Implementation files in audited domain: no file is changed by this audit.
- Governance/test files in audited domain: no existing governance/test file is changed by this audit.
- Deferred non-domain concerns: frontend UI, API route creation, public serializer changes, auth/admin design, DB migrations, seed data and runtime calculators remain out of scope.

## Exposure Matrix

| Surface interne | Utilité produit | Risque d'exposition | Stabilité du contrat | Besoin frontend | Besoin admin/debug | Besoin LLM/interprétation | Exposition recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `chart_objects` | Source canonique interne pour objets du theme, aspects, dignites, dominance, maisons, rulerships et contacts fixes. | Tres eleve si expose brut: couplage frontend au graphe calculatoire, confusion produit et fuite de payloads non stabilises. | Interne stable, contrat public brut explicitement instable. | Oui, mais via faits reduits et nommes, pas via `ChartObjectRuntimeData`. | Oui, utile pour trace de calcul protegee. | Oui, source amont de `interpretation_input`. | projection publique dediee |
| `advanced_planetary_conditions` | Conditions factuelles de mouvement, visibilite, proximite solaire, phase lunaire et signaux avances. | Moyen a eleve: vocabulaire technique, granularite changeante, risque de promesse produit non expliquee. | Interne; champ exclu du schema public. | Partiel, seulement pour faits explicables selectionnes. | Oui pour diagnostic des calculs. | Oui, deja projetable en faits interpretatifs. | interpretation/LLM uniquement |
| Contacts d'etoiles fixes | Valeur produit forte pour afficher des conjonctions significatives et alimenter le narratif. | Moyen: il faut reduire source, orbe, cible et libelle sans exposer tout le runtime. | Runtime calcule, projection publique dediee non encore stabilisee. | Oui, pour contacts lisibles et limites. | Oui pour verifier catalogues et orbes. | Oui, deja dans `interpretation_input`. | projection publique dediee |
| Profils de signes enrichis | Resume les balances elements, modalites, polarites, quadrants, fertilite, voix et formes pour interpretation. | Moyen: risque de surcharger le front et d'exposer une taxonomie encore editorialisee. | Stable comme input interpretatif post-CS-236, public shape non decidee. | Differe sauf besoin produit explicite. | Faible. | Oui, usage principal actuel. | interpretation/LLM uniquement |
| `interpretation_input` | Projection centrale deja nettoyee pour narration et signaux interpretatifs. | Eleve si expose au public: contrat oriente LLM, pas UX/API publique. | Interne interpretatif, non API. | Non, sauf projection produit separee. | Eventuellement en trace protegee. | Oui, owner principal. | interpretation/LLM uniquement |
| Hints internes d'aspects | Porte les valences, energy types et poids interpretatifs separes du runtime structurel. | Moyen: confusion entre calcul geometrique et lecture symbolique si expose sans cadrage. | Stable comme hints types; public actuel passe par projection aspect existante. | Partiel via projection publique d'aspects deja existante. | Faible. | Oui. | interpretation/LLM uniquement |
| Profils de condition | Agregent les dignites en profils factuels par planete pour conditions et interpretation. | Moyen: granularite interne et dependance aux poids de dignite. | Interne; derive de resultats de dignite. | Non direct. | Oui pour expliquer scoring. | Oui. | interpretation/LLM uniquement |
| Payloads de dominance | Payloads objet et resultat chart-level pour classer planete dominante, facteurs et rangs. | Moyen: les payloads objet ne doivent pas devenir contrat frontend brut. | Chart-level public existant; payload objet interne. | Oui via projection chart-level existante ou reduite. | Oui pour detail des facteurs. | Oui. | projection publique dediee |
| Payloads de dignite | Payloads objet et resultats de dignite essentielle/accidentelle. | Moyen: nombreux details techniques et poids doctrine-dependent. | Projection publique `dignities` existe; payload objet interne. | Oui via projection existante, pas payload brut. | Oui pour audit de scoring. | Oui. | projection publique dediee |

## Decision Notes

- `ChartObjectRuntimeData` and `chart_objects` must remain internal raw runtime surfaces. E-007 and E-008 prove they are excluded from public JSON/OpenAPI.
- Public value should be exposed through controlled projections only: `chart_facts` for selected object facts, a fixed-star contact projection, and existing or reduced dignity/dominance projections.
- Admin/debug exposure is justified only as a future protected design. No current repository evidence proves an existing protected debug endpoint for the full calculation graph.
- LLM/interpretation surfaces are already better bounded than raw runtime surfaces; they should feed narration, not become public API contracts.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md` | used | E-001 | Source contract for required surfaces, matrix columns, recommendation vocabulary and no-app-change rule. | None. |
| `_story_briefs/cs-238-audit-runtime-surface-exposure-audit.md` | used | E-002 | Source brief for exposure decisions and candidate story list. | File was already untracked before this audit run. |
| `_condamad/stories/regression-guardrails.md` / RG-141..RG-148 | used | E-003 | Existing invariants protect runtime ownership and public non-exposure adjacent to this audit. | Registry has no exact runtime exposure audit guardrail. |
| `_condamad/audits/astro-runtime-surface-exposure` | used | E-004 | Canonical output root for this audit domain. | No prior child folder existed. |
| `docs/architecture/astrology-runtime-surfaces.md` | used | E-005 | Architecture inventory classifies canonical, compatibility, chart-level and public projection surfaces. | It predates this exposure decision matrix. |
| `backend/app/domain/astrology/natal_calculation.py` / `NatalResult.chart_objects` | used | E-006, E-007 | Internal canonical runtime field, excluded from schema and dump. | Source inspection plus tests; no serializer was changed. |
| `backend/app/domain/astrology/natal_calculation.py` / `advanced_planetary_conditions` | used | E-006, E-009 | Internal advanced condition result, excluded from public schema. | Public projection choice remains product-dependent. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` / `natal_chart_v1` nodes | used | E-006 | Structural graph proves dependencies among chart objects, fixed stars, conditions, dignities, dominance and interpretation input. | Source inspection only for node shape. |
| `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` / node adapters | used | E-006 | Node adapters show runtime construction and projection owners. | Full graph suite not rerun beyond targeted tests. |
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | used | E-010 | Canonical builder for `ChartObjectRuntimeData` and runtime payloads. | Builder internals are not public contract. |
| `backend/app/domain/astrology/fixed_stars/**` | used | E-011 | Owner of fixed-star selectors, calculator and enricher. | No public projection contract exists yet. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` | used | E-012 | Builds `interpretation_input` from `chart_objects`, aspects, dominance, advanced conditions and sign balances. | LLM/narration consumers were not audited beyond input construction. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` | used | E-012 | Defines interpretation-only contracts for dignities, dominance, fixed-star contacts, aspect hints, sign balances and advanced conditions. | Not a public API contract. |
| `backend/app/services/chart/json_builder.py` | out-of-domain | E-013 | Inspected only to separate current public projections from internal runtime payloads. | Service layer changes are out of scope. |
| `backend/app/api/**` | out-of-domain | E-008, E-014 | Public API changes are forbidden; scans/tests prove no raw `chart_objects` public exposure. | No OpenAPI diff file was generated. |
| `frontend/src/**` | out-of-domain | E-014 | Frontend is outside this audit; scan found no natal runtime surface consumer. | Daily prediction fixed-star references are a different product surface. |
| `backend/tests/architecture/test_chart_runtime_surface_documentation.py` | test-only | E-005, E-015 | Architecture guard verifies documented runtime surface inventory. | Guard covers CS-224 inventory, not this new exposure matrix. |
| `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` | test-only | E-008, E-015 | Public contract guard proves `chart_objects` and `ChartObjectRuntimeData` stay out of OpenAPI/API payload. | It does not decide future projections. |
| `backend/tests/unit/domain/astrology/**` selected runtime tests | test-only | E-009, E-011, E-012, E-015 | Unit tests prove chart-object payloads, fixed-star contacts, advanced conditions and interpretation input behavior. | Only targeted tests were run. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: the audit reuses existing architecture docs, tests and runtime code as evidence; no duplicate docs outside the audit folder and no custom tooling were added.
- No Legacy: no compatibility route, alias, shim, fallback or raw runtime public contract was introduced.
- Mono-domain: decisions are limited to backend astrology runtime exposure; frontend, auth/admin implementation and serializers are deferred non-domain contexts.
- Dependency direction: current evidence keeps runtime owners under `backend/app/domain/astrology`, public projection under `backend/app/services/chart/json_builder.py`, and API exposure out of this audit.

## Exhaustive Active Finding Surface

- F-001: `chart_objects`, `ChartObjectRuntimeData`, `backend/app/domain/astrology/runtime/**`, `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`, current public contract tests. No application file is to be changed by this audit.
- F-002: `backend/app/domain/astrology/fixed_stars/**`, `backend/app/domain/astrology/interpretation/**`, current public contract tests. No application file is to be changed by this audit.
- F-003: `natal_chart_v1` graph and internal payload nodes. No application file is to be changed by this audit.
