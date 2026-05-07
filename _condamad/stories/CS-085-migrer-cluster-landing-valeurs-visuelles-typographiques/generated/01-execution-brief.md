# Execution Brief - CS-085

## Story key

`CS-085-migrer-cluster-landing-valeurs-visuelles-typographiques`

## Primary objective

Migrer le cluster CSS landing vers les tokens, roles typographiques et variables semantiques documentees du design-system sans modifier le comportement React, les routes publiques ni le contenu marketing.

## Boundaries

- Modifier uniquement le cluster landing et les registres/tests design-system necessaires.
- Perimetre CSS principal: `frontend/src/layouts/LandingLayout.css` et `frontend/src/pages/landing/**/*.css`.
- Ne pas modifier les composants React landing sauf necessite strictement mecanique prouvee.
- Ne pas ajouter de dependance, de namespace de compatibilite, de fallback CSS literal ou d'exception large.

## Required preflight

- Lire `00-story.md`, `AGENTS.md` et `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Produire `hardcoded-values-before.md` avant migration et `hardcoded-values-after.md` apres migration.

## Done conditions

- AC1 a AC8 sont `PASS` sans limitation.
- Les owners visuels repetables sont documentes dans les tokens, registres ou roles typographiques.
- Les guards frontend et scans cibles passent.
- `generated/10-final-evidence.md` et `_condamad/stories/story-status.md` sont synchronises.

## Halt conditions

- Une valeur ne peut pas recevoir de decision finale sans dette ou fallback.
- Un changement React comportemental devient necessaire.
- Une validation obligatoire echoue sans correction sure.
