# Story 23.4: Zodiac tropical vs sidereal + ayanamsa

Status: done

## Story

As a backend platform engineer,
I want Finaliser le mode sidereal avec ayanamsa explicite et invariant structurel.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** `zodiac=sidereal` avec ayanamsa valide **When** le calcul est execute **Then** le mode sidereal est applique et `metadata.ayanamsa` est non nul.
2. **Given** un cas fixe tropical vs sidereal **When** les resultats sont compares **Then** au moins un `sign_code` differe.
3. **Given** le meme JDUT **When** on compare `Lt` et `Ls` **Then** la difference angulaire respecte l'ayanamsa dans la tolerance documentee.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-3)
  - [x] Implementer: `set_sid_mode` + flag sidereal SwissEph.
- [x] Task 2 (AC: 1-3)
  - [x] Implementer: Traçer `ayanamsa` effective.
- [x] Task 3 (AC: 1-3)
  - [x] Implementer: Verifier invariant `(Lt - Ls) mod 360 ~= ayanamsa`.
- [x] Task 4 (AC: 1-3)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-3)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Le calcul sidereal doit etre mathematiquement verifiable et sans ambiguite de mode.

### Scope

- `set_sid_mode` + flag sidereal SwissEph.
- Traçer `ayanamsa` effective.
- Verifier invariant `(Lt - Ls) mod 360 ~= ayanamsa`.

### Out of Scope

- Ajout de nouvelles ayanamsas hors liste supportee.

### Technical Notes

- Utiliser une comparaison angulaire circulaire (wrap-safe).

### Tests

- Unit: validation ayanamsa supportee.
- Golden: tropical vs sidereal + invariant structurel.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 2.

### Observability

- Log `zodiac_effective`, `ayanamsa_effective`.
- Compteur erreurs `invalid_ayanamsa`.

### Dependencies

- 23.1

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

- `backend/app/domain/astrology/ephemeris_provider.py` : `set_sid_mode` déjà implémenté depuis story 23-1 (Task 1 pré-existant).
- Invariant tolérance 0.01° (36 arcsec) : SwissEph applique l'ayanamsa en interne à un niveau plus fondamental que la soustraction scalaire de `get_ayanamsa_ut()`, d'où un écart résiduel ~0.004° avec l'éphéméride Moshier. Tolérance alignée sur le standard golden de ce projet.

### Completion Notes List

- Story reformatee pour alignement strict create-story.
- **Task 1** : `set_sid_mode(ayanamsa_id)` + `FLG_SIDEREAL` flag déjà opérationnels dans `ephemeris_provider.py`. Réinitialisation en `finally` block.
- **Task 2** : Clés de log mises à jour. Compteur `invalid_ayanamsa` ajouté. Le provider retourne désormais `ayanamsa_value` via `EphemerisResult` (Audit-grade).
- **Task 3** : Invariant `(Lt - Ls) mod 360 ≈ ayanamsa` implémenté AU RUNTIME dans `ephemeris_provider.py` avec warning si dépassement de 0.01°. Vérifié également via tests golden.
- **Task 4** : 16 tests ajoutés dans `test_golden_zodiac_sidereal_ayanamsa.py` — tous verts. Couvre AC1/AC2/AC3.
- **Task 5** : Story mise à jour après revue de code (Adversarial Review fixes).

### File List

- `backend/app/domain/astrology/ephemeris_provider.py` (modifié — EphemerisResult + invariant runtime + audit)
- `backend/app/domain/astrology/natal_calculation.py` (modifié — support nouveau retour EphemerisResult)
- `backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py` (créé/renommé — 16 tests AC1/AC2/AC3)
- `backend/app/tests/unit/test_ephemeris_provider.py` (mis à jour — alignement type de retour)
- `backend/app/tests/unit/test_golden_reference_swisseph.py` (mis à jour — alignement type de retour)
- `backend/app/tests/unit/test_golden_zodiac_frame_invariants.py` (mis à jour — alignement type de retour)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié — statut de la story)
- `_bmad-output/implementation-artifacts/23-4-zodiac-tropical-vs-sidereal-ayanamsa.md` (mis à jour)

## Change Log

- 2026-02-27 : Implémentation story 23-4 complète.
- 2026-02-27 : (Revue de Code) Ajout de l'invariant au runtime, amélioration de la traçabilité de l'ayanamsa et renommage des tests golden.
