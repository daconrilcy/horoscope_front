# Audit Report - Astro Product Data Needs

## Audit Scope

- Domain key: `astro-product-data-needs`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: screen-first astrology product data needs only.
- Output folder: `_condamad/audits/astro-product-data-needs/2026-05-23-2024/`

## Closure Analysis

- Prior same-domain audit folders consulted: none; E-004 records no previous same-domain audit.
- Adjacent audit folders consulted: `astro-runtime-surface-exposure/2026-05-23-1919` and `astro-calculation-interpretation-boundary/2026-05-23-2013`.
- Story keys consulted: `CS-244`, predecessor context listed in CS-244, and guardrails RG-141 to RG-148 through `_condamad/stories/regression-guardrails.md`.
- Active findings after current evidence: F-001, F-002, F-003, F-004 and F-005.
- Closed prior findings: none for this first same-domain audit.
- Guardrails mapped: RG-141 to RG-148 protect internal runtime ownership; this audit adds no new guardrail row because it does not implement a durable runtime invariant.
- Implementation files in audited domain: none changed by this audit; E-021 proves no current worktree delta under the CS-244 forbidden app/test/migration/seeder surfaces.
- Governance/test files in audited domain: only the six new audit artifacts.
- Deferred non-domain concerns: frontend UI changes, API endpoints, serializers, projections, translators, scorers, PDF rendering, auth, DB migrations, seeds and tests remain out of scope.

## Mandatory Product Data Matrix

| Écran | Donnée nécessaire | Existe | Publique | Stable | Projection dédiée | Traduction | Score | Complexité à masquer | Story recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| thème natal simple | Profil astro, Soleil, Ascendant, planètes, maisons, aspects majeurs, métadonnées de génération | yes: E-007, E-008, E-009 | public: E-007, E-009 | stable-for-current-client: E-007 | existing `LatestNatalChart.result`; future beginner summary recommended | signs, planets, houses, aspects via E-015 | none for placements; aspect strength hidden | raw longitude, house intervals, engine metadata for beginner view | CS-256 |
| thème expert | Dignités, secte, conditions avancées, conditions traditionnelles, profils/signaux, dominantes, adapter interprétatif | yes: E-007, E-008, E-009 | mixed public/internal-risk: E-004, E-010 | partial; public JSON exists but product contract is not explicit | expert natal chart public contract | required for technical labels; partial core coverage E-015 | dignity, dominance, condition and activation scores | raw runtime graph names, low-level score breakdowns for non-expert users | CS-255 |
| debug astrologique | Trace de calcul, sources, payloads internes, audit rows, garde runtime | partial: E-010, E-011, E-016, E-018 | internal-only/unknown protected surface | unknown for product use | none until decision | not primary | raw scores and audit evidence | most runtime graph payloads and internal IDs | blocked |
| analyse de dominantes | Top planet, chart ruler, most elevated planet, ranks, factors, explanation facts | yes: E-007, E-009, E-018 | public via `dominant_planets`, raw payload object internal | partial stable; expert shape needs contract | expert contract and optional beginner summary | planet labels required | yes: rank/score/factors | factor weights and normalized details for beginner | CS-255 |
| analyse des aspects | Aspect type, bodies, angle, orb, strength, valence/energy hints | yes: E-007, E-008, E-009 | public for major aspects | stable enough for current simple screen | existing aspect projection; beginner summary can reduce | aspect/planet labels covered by E-015 | strength available in projection | orb mechanics, normalized strength, interpretive hint taxonomy | CS-256 |
| analyse traditionnelle | Secte, hayz, rejoicing, condition de secte, mitigation | yes: E-007, E-008, E-009 | public in expert payload, not beginner-safe | partial; expert contract missing | expert natal chart public contract | required for traditional labels | dignity/traditional score context | doctrine labels and condition internals | CS-255 |
| analyse des étoiles fixes | Star contact, target object, orb, star display name, significance/display rule | partial: runtime/interpretation exists E-012 | not current frontend public section | unstable public contract absent | fixed-star frontend display projection | required for star names and target labels | maybe relevance/rank, not raw score | catalog/source/orb rule details | CS-257 |
| interprétation IA | Chart JSON, evidence catalog, compact natal summary, persona/use-case metadata, disclaimers | yes: E-013, E-014 | public as interpretation response, internal as prompt/runtime | stable per public interpretation schema | none for raw LLM; beginner summary can feed compact facts | required; resolver used in context | no product score, only validation/off-scope metadata internal | prompt internals, evidence IDs beyond display need | CS-256 |
| export PDF | Persisted interpretation payload, sections, highlights, advice, evidence, disclaimers, sun/ascendant labels, template config | yes: E-014 | public to owning user | stable for persisted interpretation contract | none; PDF consumes interpretation payload | PDF label resolver required | none | pagination/template internals and debug config | none |
| interface astrologue | User default astrologer, persona selection, interpretation history, expert facts, possibly client-facing diagnostic notes | partial: E-006, E-007, E-008 | mixed; current astrologer UI is persona/profile oriented | unknown | needs-user-decision before projection | required | maybe expert scores, subject to role decision | user/private diagnostic details | blocked |
| interface utilisateur grand public | Beginner summary, translated placements/aspects, highlights, advice, paywall state, degraded warnings | partial: E-006, E-008, E-013 | public to user | unstable without beginner projection | beginner natal chart summary projection | required | none or qualitative score bands | degrees, raw score factors, runtime graph and debug fields | CS-256 |

## Needs By Audience

- Beginner/public-user needs: compact sun/moon/ascendant, dominant themes, translated labels, gentle missing-data states, qualitative aspect/highlight explanations and no raw score breakdown. Evidence: E-006, E-008, E-013, F-002.
- Expert needs: public but technical blocks for dignities, conditions, traditional analysis, dominance and interpretation adapter with explicit stable field selection. Evidence: E-007, E-008, E-009, F-001.
- Astrologer needs: product decision still required because current evidence shows persona/profile workflows and expert payloads, not a protected astrologer diagnostic contract. Evidence: E-006, E-014, F-004.
- Debug needs: internal graph, audit rows and runtime traces exist, but public or protected debug exposure is not decided. Evidence: E-010, E-011, E-016, F-004.
- AI interpretation needs: compact natal context, chart JSON, evidence catalog, persona/use-case metadata and disclaimers. Evidence: E-013, E-014.
- PDF needs: persisted interpretation content, template selection, localized sun/ascendant labels, disclaimers and pagination config. Evidence: E-014.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-244-audit-product-data-needs/00-story.md` | used | E-001 | Source contract for scope, matrix, candidates and no-app-change rule. | None. |
| `_story_briefs/cs-244-audit-product-data-needs-audit.md` | used | E-002 | Brief defines target screens, questions and required output folder. | File is untracked before this audit. |
| `_condamad/stories/regression-guardrails.md` / RG-141..RG-148 | used | E-003 | Existing astrology invariants constrain raw runtime exposure decisions. | No exact product-data guardrail. |
| `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | used | E-004 | Adjacent exposure decision source for raw runtime/internal surfaces. | Adjacent domain, not same-domain prior audit. |
| `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013` | used | E-004 | Adjacent boundary source for structural, interpretive and public contracts. | Adjacent domain. |
| `frontend/src/pages/NatalChartPage.tsx` | used | E-005, E-006, E-008 | Current simple natal, aspect, expert panel and interpretation screen owner. | Screen behavior not browser-rendered. |
| `frontend/src/features/natal-chart/NatalExpertPanel.tsx` | used | E-006, E-008 | Current expert public JSON consumer. | Does not prove target contract is sufficient. |
| `frontend/src/features/natal-chart/NatalInterpretation.tsx` | used | E-006 | Current AI interpretation, persona, history and PDF flow consumer. | Detailed component internals not audited beyond data needs. |
| `frontend/src/api/natal-chart/index.ts` | used | E-007 | Current frontend API contract and hooks for natal chart, interpretation and PDF. | Not generated from OpenAPI in this audit. |
| `backend/app/services/chart/json_builder.py` | used | E-009 | Canonical public natal chart projection source. | No code changed. |
| `backend/app/domain/astrology/natal_calculation.py` | used | E-010 | Proves raw runtime fields excluded from public schema. | Internal contract only. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` and `natal_calculation_nodes.py` | used | E-011 | Proves runtime ownership for graph, fixed stars, dominance and interpretation input. | Structural source evidence. |
| `backend/app/domain/astrology/fixed_stars/**` | used | E-012 | Fixed-star calculation owner for candidate CS-257. | Public display contract absent. |
| `backend/app/services/llm_generation/shared/natal_context.py` | used | E-013 | Compact natal context owner for AI interpretation needs. | Prompt quality out of scope. |
| `backend/app/api/v1/routers/public/natal_interpretation.py` | used | E-014 | Public interpretation and PDF route owner. | Endpoint behavior not modified. |
| `backend/app/services/natal/pdf_export_service.py` | used | E-014 | PDF data assembly owner. | Visual PDF rendering out of scope. |
| `backend/app/tests/unit/test_astrology_translation_resolver.py` | test-only | E-015 | Translation resolver guard evidence. | Does not cover every future label. |
| `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` | test-only | E-016 | Runtime exposure guard evidence. | Product matrix not covered by test. |
| `backend/tests/architecture/test_astrology_runtime_boundary.py` | test-only | E-017 | Runtime boundary guard evidence. | UX copy not covered. |
| `backend/app/tests/unit/test_chart_result_service.py` | test-only | E-018 | Persisted payload and score evidence. | Not a frontend contract test. |
| `frontend/src/**`, `backend/app/**`, `backend/tests/**`, `backend/app/tests/**`, `backend/migrations/**`, `docs/db_seeder/**` modification surfaces | out-of-domain | E-001, E-020, E-021 | Application, backend test, migration and seeder changes are forbidden by CS-244, and the targeted worktree scan returned no path under those surfaces. | Existing unrelated governance/audit worktree changes are outside this forbidden-surface check. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: the audit reuses the source brief vocabulary, existing screen/client/backend owners, adjacent audits and existing tests. No duplicate app contract, endpoint or tooling was introduced.
- No Legacy: no compatibility route, shim, alias, fallback, serializer branch or legacy public path was added; E-021 confirms no forbidden application surface changed during this audit review.
- Mono-domain: findings stay within product data needs and route implementation details to candidate stories or user decision.
- Dependency direction: frontend remains a public projection consumer; backend runtime and LLM internals remain owners of their current layers.

## Exhaustive Active Finding Surface

- F-001: `frontend/src/features/natal-chart/NatalExpertPanel.tsx`, `frontend/src/api/natal-chart/index.ts`, `backend/app/services/chart/json_builder.py`, public contract tests selected by CS-255. No file is modified by this audit.
- F-002: `frontend/src/pages/NatalChartPage.tsx`, `frontend/src/features/natal-chart/NatalInterpretation.tsx`, `frontend/src/api/natal-chart/index.ts`, `backend/app/services/chart/json_builder.py`, `backend/app/services/llm_generation/shared/natal_context.py`, translation tests selected by CS-256. No file is modified by this audit.
- F-003: `backend/app/domain/astrology/fixed_stars/**`, `backend/app/domain/astrology/runtime/natal_calculation_graph.py`, `backend/app/services/chart/json_builder.py`, `frontend/src/api/natal-chart/index.ts`, future frontend section selected by CS-257. No file is modified by this audit.
- F-004: debug/astrologer product surfaces are blocked pending audience and authorization decision; no exhaustive implementation surface can be final until that decision exists.
- F-005: governance-only guard candidate; no application or test file remains to modify in this audit.
