# Dev Log

## 2026-05-04

- Preflight: `git status --short` montrait des modifications preexistantes sur `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md` et le dossier CS-013 non suivi.
- Capsule: generation des fichiers requis sous `generated/`.
- Inspection: `app.core.request_id` identifie comme source canonique; le routeur public transmet deja les IDs a l'enrichissement narration.
- Implementation: ajout d'un test de propagation vers `generate_horoscope_narration_via_gateway` et d'une garde anti-retour ciblant `public_projection.py`.
