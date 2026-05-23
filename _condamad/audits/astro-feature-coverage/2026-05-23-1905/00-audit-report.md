# Audit Report - Astro Feature Coverage

## Audit Scope

- Domain key: `astro-feature-coverage`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend astrology runtime, tests, seed/reference data and astrology research docs.
- Output folder: `_condamad/audits/astro-feature-coverage/2026-05-23-1905/`

## Closure Analysis

- Prior same-domain audit folders consulted: none; E-004 found no previous `_condamad/audits/astro-feature-coverage` child folder.
- Story keys consulted: `CS-237-audit-astrology-engine-feature-coverage`; guardrail registry `RG-137` to `RG-148` for recent astrology runtime invariants.
- Active findings after current evidence: F-001, F-002, F-003, F-004, F-005.
- Closed prior findings: none for this domain.
- Guardrails mapped: RG-137 to RG-148 protect implemented natal runtime surfaces; no new guardrail was added because this audit did not discover a new already-enforced durable invariant beyond the current registry.
- Implementation files in audited domain: no file is changed by this audit.
- Governance/test files in audited domain: no existing governance/test file is changed by this audit.
- Deferred non-domain concerns: frontend UI, API exposure, database migrations, auth, i18n, styling and build tooling remain out of scope.

## Coverage Matrix

| Technique / objet / condition | Statut actuel | Niveau de couverture | Dependances runtime | Tables necessaires | Calculateur necessaire | Projection publique necessaire | Priorite produit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Theme natal structurel | implemented | Positions, maisons, points astraux configures, aspects, signes runtime, signature, dominance et resultats publics sont orchestres par `natal_chart_v1`. | `build_natal_result`, `natal_chart_v1`, `CalculationGraphRunner`, `NatalResultAssembler` | `astral_planets`, `astral_signs`, `astral_house_*`, `astral_aspect_*`, references runtime | Existing graph nodes | Projection publique existante a conserver sans exposer `chart_objects` | P0 keep stable |
| Dignites essentielles | implemented | Domicile, exaltation, detriment, fall, triplicity, terms/faces selon referentiel et tests golden. | `PlanetDignityScoringService`, `EssentialDignityCalculator`, `ChartSectResult` | `astral_essential_dignity_*`, `astral_triplicity_ruler_assignments`, term and face references | Existing dignity calculators | Projection publique existante via `dignities` | P0 keep stable |
| Dignites accidentelles | implemented | Angularite, mouvement, vitesse, solar conditions, sect, joie, hayz, benefic/malefic aspect conditions and besiegement rules are represented in reference/rules and runtime scoring. | `AccidentalDignityCalculator`, `advanced_condition_modifiers`, `PlanetDignityScoringService` | `astral_accidental_dignity_*`, `astral_advanced_condition_*` | Existing dignity and condition calculators | Projection publique existante via dignity and condition outputs | P0 keep stable |
| Conditions planetaires avancees | implemented | Solar proximity, motion, speed, visibility, lunar phase and advanced condition profiles are calculated internally and consumed by dignities and interpretation input. | `calculate_advanced_planetary_conditions`, `motion_visibility_payloads`, `advanced_conditions` node | Static profiles plus advanced condition reference tables | Existing `planetary_conditions` calculators | Mostly internal; public projection should remain deliberate | P1 productize selectively |
| Sect, hayz, rejoicing | implemented | Sect chart-level, planet sect condition, hayz components and rejoicing house are covered by runtime calculators and tests. | `SectCalculator`, `HayzCalculator`, `TraditionalConditionNormalizer` | `astral_sect`, accidental dignity rules, planet natures and sign genders | Existing dignity and advanced condition calculators | Current projection through traditional conditions and dignity surfaces | P0 keep stable |
| Parts arabes / lots | missing | `ChartObjectType.ARABIC_PART` exists as taxonomy, but no audited calculator, seed point family or public/runtime flow proves lots calculation. | none proven | likely new lot definitions and formulas | New lot calculator needed | Yes, after product decision | P2 |
| Noeuds, Lilith, apsides | partially implemented | Nodes, lunar apogee/perigee and Black Moon Lilith exist in seed data and `calculate_astral_points`; product exposure and capabilities are incomplete. | `AstralPointCalculationResolver`, `calculate_astral_points`, chart object builder | `astral_points`, `astral_point_calculation_variants`, interpretation profiles | Existing point resolver for current points | Yes, decision needed for public projection and capabilities | P1 |
| Etoiles fixes | partially implemented | Fixed-star catalog and chart-object payloads exist; only zodiacal conjunction contacts are calculated. | `FixedStarConjunctionCalculator`, selectors, enricher, `fixed_star_conjunctions` node | `astral_fixed_star_*`, reference sources | Existing conjunction calculator only | Yes, if user-facing contacts are required | P1 |
| Parans | missing | No backend astrology paran calculator or test found; research/source docs mention parans as future or absent. | none proven | fixed-star catalog plus horizon/diurnal motion data likely needed | New paran calculator needed | Yes, only after calculator exists | P3 |
| Midpoints | missing | No midpoint runtime, reference data or tests found in audited backend astrology domain. | none proven | midpoint definitions or object policy needed | New midpoint calculator needed | Yes, after taxonomy decision | P3 |
| Asteroides | missing | No asteroid ephemeris, seed taxonomy or calculator found; only future product mention exists. | none proven | asteroid catalog and ephemeris support needed | New asteroid calculator or provider extension needed | Yes, after taxonomy decision | P3 |
| Chiron | missing | No Chiron runtime calculator, seed planet/object, ephemeris mapping or test found. | none proven | Chiron object and ephemeris mapping needed | New Chiron support needed | Yes, after taxonomy decision | P2 |
| Transits | reference-only | Research docs and `transit_to_natal` orb rules exist, but no `backend/app/domain/astrology` transit calculator or graph was found. | none proven in audited domain | aspect orb rules contain transit contexts | New transit graph/calculator needed | Yes, dedicated public contract required | P0 |
| Progressions | reference-only | Research docs and `progression_to_natal` orb rules exist, but no progression calculator or graph was found. | none proven in audited domain | aspect orb rules contain progression contexts | New progression calculator needed | Yes, dedicated public contract required | P1 |
| Revolutions solaires et lunaires | reference-only | Solar return research doc exists; no solar/lunar return calculator was found in the audited runtime. | none proven | return chart settings and ephemeris policy needed | New return-chart calculator needed | Yes, dedicated public contract required | P1 |
| Synastrie | reference-only | Research doc exists and one code comment avoids adding synastry-specific scoring; no synastry graph/calculator was found. | none proven | dual-chart contracts and orb policy needed | New inter-chart calculator needed | Yes, dedicated public contract required | P1 |
| Composite | reference-only | Composite is mentioned as a later relationship option; no composite chart calculator was found. | none proven | dual-chart midpoint/composite policy needed | New composite calculator needed | Yes, after synastry decision | P2 |
| Profections | missing | No profection runtime, reference data or tests found. | none proven | time-lord/profection rules needed | New profection calculator needed | Yes, dedicated public contract required | P2 |
| Directions symboliques | missing | No symbolic direction runtime, reference data or tests found. | none proven | direction arc/rule references needed | New directions calculator needed | Yes, after forecast scope decision | P3 |
| Firdaria / time lords si pertinent | missing | No firdaria or time-lord runtime, reference data or tests found. | none proven | time-lord period tables needed | New time-lord calculator needed if product selects this doctrine | Yes, only if selected | P3 |

## Business Conclusion

The backend astrology engine is implemented for natal calculation and its recent internal runtime surfaces. The next recommended story is not a broad implementation batch: it is a P0 predictive runtime roadmap that selects the first forecast owner, probably transits, and defines a graph/calculator contract separate from `natal_chart_v1`.

Second-rank stories should productize existing internal value rather than invent new calculators: fixed-star conjunction projection and astral-point public/capability decisions. Parts arabes/lots, asteroids, Chiron, midpoints, parans, returns, synastry, composite, profections, directions and firdaria should wait for explicit object or predictive-domain ownership.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` | used | E-001 | Source contract for required techniques, matrix columns, statuses and validation scope. | None. |
| `_story_briefs/cs-237-audit-astrology-engine-feature-coverage-audit.md` | used | E-002 | Source brief for delivery folder, no-app-change rule and required validation checks. | File was already untracked in the worktree before audit artifact creation. |
| `_condamad/stories/regression-guardrails.md` | used | E-003 | Registry maps current astrology runtime invariants and no-app-change guardrails. | No exact feature-coverage invariant exists yet. |
| `_condamad/audits/astro-feature-coverage` | used | E-004 | Canonical audit output root for this domain. | No prior child folder was available for closure comparison. |
| `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md` | used | E-005 | Main narrative baseline for post-CS-236 runtime coverage and known limits. | File was already untracked in the worktree before audit artifact creation. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` / `natal_chart_v1` | used | E-006 | Runtime graph is the canonical structural evidence for implemented natal coverage. | Source inspection only; no graph execution was run for every technique. |
| `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` / node adapters | used | E-007 | Node adapters prove runtime calculators are wired for natal conditions, fixed stars, dignities, dominance and interpretation input. | Source inspection only; targeted tests provide partial runtime proof. |
| `backend/app/domain/astrology/natal_calculation.py` / `NatalResult` | used | E-008 | Contract shows public fields and internal excluded fields. | Public API serialization is validated by separate tests, not by this file alone. |
| `backend/app/services/chart/json_builder.py` / chart JSON projection | out-of-domain | E-009 | Inspected only to separate backend domain coverage from public projection concerns. | Serializer is service layer, not the audited domain owner. |
| `backend/tests/unit/domain/astrology/**` selected tests | test-only | E-010, E-011, E-012, E-013 | Tests prove implemented surfaces and classify coverage claims. | Full unit suite was not run before initial classification. |
| `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` | test-only | E-009 | Guards non-exposure of `chart_objects` in OpenAPI/API payloads. | Integration test covers public contract, not all product projections. |
| `docs/db_seeder/astrology/**` selected reference files | used | E-011, E-012, E-013, E-015 | Reference data proves which techniques have seed/reference support. | Reference-only data is not treated as implementation without runtime proof. |
| `backend/app/domain/astrology/fixed_stars/**` | used | E-013 | Canonical runtime owner for fixed-star conjunction selectors, rules, calculator and enrichment. | Does not implement parans or non-conjunction contacts. |
| `backend/app/domain/astrology/astral_point_calculation_resolver.py` | used | E-012 | Canonical resolver for configured astral points, nodes, Lilith and apsides. | Does not settle public projection or full capability policy. |
| `backend/app/domain/astrology/planetary_conditions/**` | used | E-007, E-011 | Canonical runtime owner for motion, visibility, solar proximity and lunar phase conditions. | Visibility remains simplified per E-005. |
| `backend/app/domain/astrology/dignities/**` | used | E-007, E-011 | Canonical owner for essential and accidental dignity scoring. | Some weights/profiles remain reference-driven and require governance for changes. |
| `backend/app/domain/astrology/advanced_conditions/**` | used | E-007, E-011 | Canonical owner for traditional advanced conditions including hayz and sect-related normalization. | Not a predictive-technique owner. |
| `frontend/src/**` | out-of-domain | E-002 | Explicitly excluded by story and brief. | Not inspected beyond scope exclusion. |
| `backend/app/api/**` | out-of-domain | E-002, E-003 | API/public exposure is excluded from this audit. | No route/OpenAPI diff was generated. |
| `backend/migrations/**` | out-of-domain | E-002 | Database migration work is forbidden for this audit. | Not inspected beyond scope exclusion. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: existing calculators and graph nodes are reused as evidence; no duplicate calculator or audit tooling was added.
- No Legacy: no compatibility route, alias, shim, fallback, app-code wrapper or public `chart_objects` exposure was added.
- Mono-domain: findings are limited to backend astrology feature coverage; API/frontend/DB concerns are deferred non-domain context.
- Dependency direction: implemented claims rely on domain runtime and tests; service-layer JSON builder is classified out-of-domain and only used for projection boundary evidence.

## Exhaustive Active Implementation Finding Surfaces

- F-001: no current implementation files to modify in this audit; future story must select exact predictive owner before changing code. Candidate surface selection rule: forecast graph/calculator modules under `backend/app/domain/astrology` plus dedicated tests, excluding `natal_chart_v1` changes unless explicitly justified.
- F-002: current in-domain surfaces are `backend/app/domain/astrology/fixed_stars/**`, `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`, fixed-star tests and reference data. Future story must decide projection versus new calculator before edits.
- F-003: current in-domain surfaces are `backend/app/domain/astrology/astral_point_calculation_resolver.py`, `backend/app/domain/astrology/natal_calculation.py`, `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`, chart-object tests and astral-point seed data.
- F-004: no implementation owner exists for parts arabes/lots, asteroids, Chiron or midpoints; first change should be a taxonomy/ownership story, not a calculator patch.
- F-005: governance/test surface remains to be selected; likely owner is a CONDAMAD guard or audit validation check, not backend application code.
