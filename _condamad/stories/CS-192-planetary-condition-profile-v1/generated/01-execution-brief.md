<!-- Brief d'execution CONDAMAD genere pour guider l'implementation CS-192. -->

# CS-192 Execution Brief

## Objectif

Construire `PlanetConditionProfile` comme couche backend derivee des
`PlanetDignityResult` existants, transporter les nouveaux axes de poids par le
runtime reference, exposer `NatalResult.condition_profiles`, puis projeter
`planet_condition_profiles` dans le JSON public.

## Perimetre

- Modifier uniquement le backend, les migrations, les tests et les preuves de
  story necessaires.
- Ne pas toucher `frontend/**`.
- Ne pas creer de table `astral_chart_planet_condition_profiles`.
- Ne pas ajouter de dependance.
- Ne pas introduire de narration, prompt, prediction ou appel LLM.

## Preflight

- Worktree sale preexistant: `_condamad/stories/regression-guardrails.md`,
  `_condamad/stories/story-status.md`, le dossier CS-192 et
  `docs/recherches astro/2026-05-19-calcul-theme-natal-post-stories.md`.
- Story non issue d'un audit: sufficiency gate `PASS`.
- Guardrails applicables: `RG-107`, `RG-108`, `RG-112`, `RG-115`, `RG-116`,
  `RG-118`, `RG-119`.

## Done Conditions

- AC1 a AC9 prouves par tests ou scans.
- Evidence avant/apres et rapports persistants crees.
- `generated/10-final-evidence.md` et `_condamad/stories/story-status.md`
  synchronises.
- Validation executee sous venv Python.
