# Dev Log - CS-185

## Preflight

- Story cible: `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md`.
- Dirty files preexistants observes: `_condamad/stories/regression-guardrails.md`,
  `_condamad/stories/story-status.md`, dossier CS-185 non suivi,
  `docs/recherches astro/2026-05-18-calcul-theme-astrologique.md` non suivi.
- Sufficiency gate: PASS, story finie et non batch.

## Implementation

- Snapshot avant capture dans `evidence/sign-profile-runtime-before.json`.
- `ReferenceRepository.get_reference_data()` joint les profils de signes et
  taxonomies.
- `ReferenceDataService.seed_reference_version()` synchronise maintenant les
  profils de signes avant les dignites et aspects.
- `SignReferenceData` et `SignRuntimeData` exigent `element`, `modality`,
  `polarity`.
- Le mapper transforme une absence de champ profile en erreur bloquante via le
  repository runtime.
- Tests repository, builder, signature, contrat et guards mis a jour.

## Fix review iteration 1

- Separation du payload public et du payload runtime enrichi apres finding CR-1.
- Suppression du fallback fixture via `SIGN_PROFILE_DATA` apres finding CR-2.
- Erreur de profil manquant rendue explicite via outer join runtime apres
  finding CR-3.

## Validation

- Validations ciblees lancees apres activation du venv.
- Revue independante par subagents lancee apres validation locale.
