# Story 24.2: Calcul aspects avec orbs et overrides

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Calculer les aspects majeurs avec orbs parametriques et overrides hierarchiques.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** des regles avec overrides **When** un aspect est detecte **Then** `orb_used` respecte la priorite de resolution attendue.
2. **Given** un aspect retourne **When** les champs sont verifies **Then** `orb_used <= orb_max` et `code` appartient a `{conjunction,sextile,square,trine,opposition}`.
3. **Given** un cas controle attendu **When** le calcul est execute **Then** au moins un aspect specifique attendu est present avec les bonnes valeurs d'orb.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-3)
  - [x] Implementer: Resolution orb: pair override > luminaries override > default orb.
- [x] Task 2 (AC: 1-3)
  - [x] Implementer: Retourner `orb_used` et `orb_max`.
- [x] Task 3 (AC: 1-3)
  - [x] Implementer: Limiter aux aspects majeurs.
- [x] Task 4 (AC: 1-3)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-3)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Les sorties doivent reproduire les pratiques "cabinet" en restant deterministes.

### Scope

- Resolution orb: pair override > luminaries override > default orb.
- Retourner `orb_used` et `orb_max`.
- Limiter aux aspects majeurs.

### Out of Scope

- Aspects mineurs et harmonics.

### Technical Notes

- Tri deterministic des aspects retournes.
- Ne pas accepter de test "non vide" sans fixture controlee.

### Tests

- Unit: priorite overrides.
- Golden: cas attendu avec aspect precis.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 3.

### Observability

- Metric `aspects_calculated_total{school}`.
- Metric `aspects_rejected_orb_total`.

### Dependencies

- 24.1

### Project Structure Notes

- Story artifact: `_bmad-output/implementation-artifacts/`.
- Planning source: `_bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md]
- [Source: .gemini/commands/bmad-bmm-create-story.toml]
- [Source: _bmad/bmm/workflows/4-implementation/create-story/template.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- _bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml
- _bmad/bmm/workflows/4-implementation/dev-story/instructions.xml

### Completion Notes List

- AC1: Resolution orb hierarchique confirmee et clarifiee dans `aspects.py`: pair_override > orb_luminaries > default_orb. La variable interne `orb_limit` (seuil resolu) est maintenant separee de `orb_used` (deviation) pour eviter toute confusion sémantique.
- AC1+AC2: `orb_used` = deviation angulaire reelle (ex. 3.0° pour un square Soleil-Mars a 93°). `orb_max` = seuil resolu par priorite (ex. 6.0° si default_orb_deg=6). Invariant garanti: `orb_used <= orb_max` pour tout aspect detecte.
- AC2: `AspectResult` enrichi des champs `orb_used: float` et `orb_max: float` (obligatoires pour l'auditabilité). Le champ `orb` (backward compat) conserve la meme valeur que `orb_used`.
- AC2+Task3: `MAJOR_ASPECT_CODES = frozenset({"conjunction","sextile","square","trine","opposition"})` ajoute dans `constants.py`. Filtrage applique dans `build_natal_result` avant appel a `calculate_major_aspects`.
- AC3 (golden): Test `test_golden_square_sun_mars_orb3_default` — Soleil 0°, Mars 93°, square attendu avec orb=3.0, orb_used=3.0, orb_max=6.0. Verifie le calcul deterministe bout-en-bout avec tri alphabetique des planetes (ex: `mars-sun`).
- Observabilite: `increment_counter(f"aspects_calculated_total_{aspect_school}", ...)` et `increment_counter("aspects_rejected_orb_total", ...)` — importations deplacees au niveau du module dans `natal_calculation.py` pour eviter les "local imports".
- Standardisation: Les planetes dans les aspects sont triees alphabetiquement (`planet_a < planet_b`) pour garantir la stabilite de l'API.
- 20 nouveaux tests (4 mis a jour + 16 nouveaux dans `test_aspect_orb_overrides.py`) — tous passent.

### File List

- backend/app/core/constants.py
- backend/app/domain/astrology/calculators/aspects.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/tests/unit/test_aspects_calculator.py
- backend/app/tests/unit/test_aspect_orb_overrides.py
- _bmad-output/implementation-artifacts/24-2-calcul-aspects-orbs-overrides.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-28: Implementation story 24-2 — calcul aspects orbs et overrides (claude-sonnet-4-6)
  - `aspects.py`: retourne maintenant `orb_used` (deviation reelle) et `orb_max` (seuil resolu par priorite)
  - `aspects.py`: tri alphabetique des planetes `planet_a < planet_b`
  - `natal_calculation.py` `AspectResult`: ajout champs `orb_used: float` et `orb_max: float` (requis)
  - `natal_calculation.py`: deplacement des imports d'observabilite au top-level
  - `constants.py`: ajout `MAJOR_ASPECT_CODES`
  - `test_aspects_calculator.py` & `test_aspect_orb_overrides.py`: mis a jour pour tri alphabetique et champs requis
