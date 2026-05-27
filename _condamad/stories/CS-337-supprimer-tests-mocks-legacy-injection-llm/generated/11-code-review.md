# Revue de redaction CS-337

Verdict: CLEAN

## Portee

- Story: `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/00-story.md`
- Brief source: `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`
- Tracker: `_condamad/stories/story-status.md`
- Date de revue: 2026-05-27

## Alignement brief / story

- L'objectif de suppression des tests, fixtures, snapshots et mocks legacy d'injection LLM natale est explicite.
- Les primitives du brief sont couvertes: inventaire, classification, deletion, remplacement par `llm_astrology_input_v1`,
  conservation des guards negatifs, preuve de non-skip et evidence de livraison.
- Les hors-perimetres du brief sont preserves: usages non-LLM de `chart_json`, CI, runtime prompt generation et API publique.
- La dependance CS-336 et le contexte CS-335 sont cites comme sources amont.
- Les risques principaux sont identifies: perte de couverture moderne, mauvaise classification et mocks residuels.

## Guardrails et preuves attendues

- Guardrails cibles relus par ID uniquement: RG-002 et RG-022.
- La story conserve RG-002 pour la neutralite API publique et RG-022 pour les chemins pytest collectes.
- La validation exige `pytest`, scans `rg`, checks OpenAPI et preuves persistantes separees.
- L'artefact de revue attendu est bien ce fichier:
  `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/generated/11-code-review.md`.

## Validations de redaction

- `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ...\00-story.md`: PASS
- `python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ...\00-story.md`: PASS

## Issues

Aucune issue de redaction actionnable identifiee.

## Risque residuel

La story reste pre-implementation: les preuves runtime et les scans backend devront etre produits pendant l'implementation.
