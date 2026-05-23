# Story Candidates - Astro Reference Governance

This file qualifies the three story keys required by CS-240. The validator requires one `SC-*` entry per source finding, so supplemental entries are explicitly routed under CS-249, CS-250 or CS-251 instead of introducing additional story keys.

## SC-001 CS-249 Inventory Astrology Rule Sources And Static Thresholds

- Source finding: F-003
- Suggested story title: CS-249 - Inventory astrology rule sources and static thresholds
- Suggested archetype: rule-source-inventory
- Primary domain: astro-reference-governance
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Contract Shape, Persistent Evidence
- Draft objective: Produce a maintained source ownership and doctrine index for every active threshold, weight, profile, interpretation source and rule family found by this audit.
- Closure intent: phased-with-map
- Must include: exact scan rules for `backend/app/domain/astrology/**`, `backend/app/infra/db/repositories/**`, `docs/db_seeder/astrology/**`, selected `backend/tests/**` and selected doctrine docs; classification as DB-owned, Python-owned, test-only, documentation-only, mixed, out-of-domain or needs-user-decision; mapping to F-003, F-004 and F-005; no seed, migration or runtime change.
- Validation hints: run `rg -n "0\\.283|8\\.5|17\\.0|15\\.0|0\\.05|mean_speed|stationary_threshold|weight|ranking_weight|score_value|orb_deg|interpretation_profile|advanced_condition_profile" backend/app/domain/astrology docs/db_seeder/astrology backend/tests/unit/domain/astrology docs`; run document validation for the generated index; verify `git diff --name-only` excludes app, seed, migration and frontend files unless a later story explicitly authorizes otherwise.
- Blockers: stop if a rule family, doctrine source, interpretation profile, sign weight, house weight or dominance rule cannot be classified without a product/doctrine decision; record it as `needs-user-decision` instead of inventing ownership.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: a new or updated governance index under `_condamad/stories/CS-249-*/` or another story-approved governance location; optional doctrine/source index in the same approved location; no wildcard folder allowlist.
- Before evidence: this audit folder and E-006 through E-013, E-015 and E-017.
- After evidence: updated source inventory, doctrine/source status for every matrix row, interpretation source classification, targeted scans with zero unclassified in-domain hits, and no app/seed/migration/frontend diff.
- Stop condition: every rule family in `00-audit-report.md` is classified, every static threshold/weight/profile hit is either mapped or documented as out-of-domain, and F-003, F-004 and F-005 are closed or explicitly blocked by `needs-user-decision`.

## SC-002 CS-250 Move Planetary Condition Thresholds To Versioned Runtime Reference

- Source finding: F-001
- Suggested story title: CS-250 - Move planetary condition thresholds to versioned runtime reference
- Suggested archetype: reference-governance-convergence
- Primary domain: backend astrology planetary conditions
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: Converge solar proximity, visibility, motion and station thresholds into a single versioned runtime reference path or document a user-approved Python-canonical exception.
- Closure intent: phased-with-map
- Must include: full affected surface from F-001 and F-002; exact inventory of DB accidental dignity thresholds, `SolarProximityThresholds`, visibility thresholds, `DEFAULT_PLANETARY_MOTION_PROFILES`, DB motion state/relation rows, `absolute_speed_max_deg_per_day`, accidental dignity speed comparisons, runtime loader/mapper behavior and tests; no silent fallback; no wildcard allowlist; explicit decision for `under_beams` 15 versus 17 and station threshold semantics.
- Validation hints: run current planetary condition tests, accidental dignity tests, targeted threshold scans, DB reference migration/seed tests only if the story authorizes seed/schema changes, and an ownership guard proving no duplicate unclassified threshold remains.
- Blockers: user decision required before changing doctrine-sensitive numeric values, deciding DB versus Python canonical ownership, replacing generic station thresholds with per-planet thresholds, or moving seeds/schema; stop instead of emitting another follow-up if these decisions cannot be made.

### Exhaustive Files To Modify

- Application files: exact files must be selected by CS-250 after deciding DB versus Python canonical ownership; expected candidates include `backend/app/domain/astrology/planetary_conditions/contracts.py`, `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`, solar/visibility/motion calculators, `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`, runtime reference loader/mapper files and focused tests.
- Governance/test files: targeted unit/architecture guard files only; no broad backend test rewrite.
- Before evidence: E-008, E-009, E-014 and E-015.
- After evidence: threshold scan has no unclassified duplicate owner; tests prove runtime consumes the selected canonical reference; no compatibility fallback remains.
- Stop condition: F-001 and F-002 close fully, or the story records a `needs-user-decision` blocker for unresolved doctrine or ownership values.

## SC-003 CS-251 Add Reference Governance Tests For Rule Source Ownership

- Source finding: F-006
- Suggested story title: CS-251 - Add reference governance tests for rule source ownership
- Suggested archetype: governance-test-hardening
- Primary domain: backend tests / astrology governance
- Required contracts: Reintroduction Guard, Contract Shape, Persistent Evidence, No Legacy
- Draft objective: Add deterministic tests or guard scripts that fail when thresholds, weights, profiles or rule sources are added without source ownership classification.
- Closure intent: full-closure
- Must include: no-wildcard allowlist; guarded terms for thresholds, weights, profiles, orbs, solar proximity, speed, station, dominance, dignity, fixed stars, aspects and interpretation; exact registry path; proof that existing known hits are classified; dependency on the CS-249 inventory when the guard needs a source registry.
- Validation hints: run the new guard, `pytest -q` for the owning test file, targeted `rg` scans from this audit, and `git diff --name-only` to prove no seed/runtime movement unless separately authorized.
- Blockers: if CS-249 inventory does not exist yet, CS-251 should either create a minimal registry as part of the same closure or stop and depend on CS-249.

### Exhaustive Files To Modify

- Application files: none expected.
- Governance/test files: one focused backend architecture/unit guard plus one exact ownership registry; no wildcard allowlist and no generated migration.
- Before evidence: E-003, E-018 and E-019.
- After evidence: guard fails on an injected unclassified rule-source fixture or equivalent negative check; all existing hits are classified.
- Stop condition: no threshold/weight/profile source can be introduced under audited paths without classification, and F-006 is closed.

## SC-004 CS-249 Include Interpretation Source Ownership

- Source finding: F-004
- Suggested story title: CS-249 - Inventory astrology rule sources and static thresholds
- Suggested archetype: rule-source-inventory
- Primary domain: backend astrology interpretation governance
- Required contracts: Runtime Source of Truth, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: Ensure DB interpretation profiles, Python advanced-condition catalogs and doctrine docs have explicit ownership classification in the CS-249 inventory.
- Closure intent: phased-with-map
- Must include: mapping for DB interpretation profiles/translations, Python profile catalogs, interpretation input projectors and doctrine/source metadata; clear separation from LLM prompts and public API projection.
- Validation hints: run `pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py` and targeted scans over `backend/app/domain/astrology/interpretation docs/db_seeder/astrology docs`.
- Blockers: product/editorial decisions for final user-facing text remain non-domain and must not block runtime source ownership classification.

### Exhaustive Files To Modify

- Application files: none unless a later implementation story explicitly authorizes moving catalog ownership.
- Governance/test files: exact interpretation governance registry entry inside the CS-249 inventory and focused guard coverage if needed.
- Before evidence: E-011, E-013 and E-017.
- After evidence: every interpretation profile source is classified as DB, Python, documentation-only or out-of-domain.
- Stop condition: F-004 closes without needing another discovery-only follow-up.

## SC-005 CS-250 Include Motion And Station Threshold Ownership

- Source finding: F-002
- Suggested story title: CS-250 - Move planetary condition thresholds to versioned runtime reference
- Suggested archetype: reference-governance-convergence
- Primary domain: backend astrology planetary motion
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: Decide and implement the canonical owner for mean speeds, speed ratios, station thresholds and speed-relation rules as part of CS-250.
- Closure intent: full-closure
- Must include: exact inventory of `DEFAULT_PLANETARY_MOTION_PROFILES`, DB motion state/relation rows, `absolute_speed_max_deg_per_day`, accidental dignity speed comparisons, before/after scans, no wildcard allowlist and no silent fallback.
- Validation hints: run `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py`; run targeted scans for `mean_speed`, `stationary_threshold_abs`, `0.05`, `speed_relation`.
- Blockers: user/doctrine decision required if per-planet station thresholds replace the current generic DB threshold or Python formula.

### Exhaustive Files To Modify

- Application files: exact files selected by the story after source decision; expected candidates are planetary motion contracts/profiles, accidental dignity calculator, runtime reference mapping and tests.
- Governance/test files: focused ownership guard only.
- Before evidence: E-009, E-014 and E-015.
- After evidence: no unclassified speed/station threshold remains and F-002 closes.
- Stop condition: all motion and station thresholds have one canonical source or an explicit `needs-user-decision` blocker.

## SC-006 CS-249 Include Doctrine Source Index

- Source finding: F-005
- Suggested story title: CS-249 - Inventory astrology rule sources and static thresholds
- Suggested archetype: doctrine-source-index
- Primary domain: astro-reference-governance
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Persistent Evidence
- Draft objective: Link each audited rule family to reference/source metadata, doctrine documentation, or an explicit documented absence inside the CS-249 governance inventory.
- Closure intent: full-closure
- Must include: every rule family from the mandatory matrix, source IDs where DB-backed, docs path where documentation-only, and explicit absence for unresolved doctrine.
- Validation hints: scan `docs/db_seeder/astrology/astral_sources.json`, `astral_reference_sources.json`, selected seed files and `docs/recherches astro/**`; validate the index references every family in this audit.
- Blockers: stop with `needs-user-decision` if doctrine ownership requires product/editorial approval.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: doctrine/source index entry inside CS-249 and optional guard tying it to the matrix.
- Before evidence: E-007 and E-013.
- After evidence: every matrix row has a doctrine/source status.
- Stop condition: F-005 closes without requiring runtime or seed changes.

## Deferred Non-Domain Candidates

- Prediction-specific transit orb governance is out of this domain despite broad scan hits under `backend/app/domain/prediction/**`.
- API/frontend exposure stories must use the runtime-surface and product-data audits, not this source-governance audit, unless they directly change rule ownership.
