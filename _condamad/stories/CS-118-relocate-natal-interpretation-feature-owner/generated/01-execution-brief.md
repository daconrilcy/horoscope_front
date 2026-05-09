# Execution Brief - CS-118

## Primary Objective

Relocaliser `NatalInterpretationSection` et le sous-container `PersonaSelector`
depuis `frontend/src/components/**` vers `frontend/src/features/natal-chart/**`
sans changer le comportement utilisateur du parcours theme natal.

## Boundaries

- Domaine unique: `frontend/src/features/natal-chart/**`.
- Autorise: moves frontend, imports runtime/tests, guards component-architecture,
  allowlist exacte, artefacts before/after/no-shim.
- Interdit: backend, contrats API, endpoints, comportement produit, wrapper,
  alias, fallback, re-export de compatibilite ou ancien chemin actif.

## Required Guardrails

- `RG-069`: les composants partages ne doivent pas posseder
  l'orchestration API/feature.
- `RG-071`: le split CS-115 de `NatalInterpretation` doit rester preserve.
- `RG-073`: l'orchestration d'interpretation natale appartient a
  `frontend/src/features/natal-chart/**`.

## Done When

- Les sept AC de `03-acceptance-traceability.md` sont `PASS`.
- Les artefacts `natal-feature-owner-before.md`,
  `natal-feature-owner-after.md` et `natal-feature-owner-no-shim.md` existent.
- Les commandes du plan de validation passent ou sont documentees comme bloquees
  avec risque explicite.
- Aucun ancien chemin `components/NatalInterpretation` actif, wrapper, alias ou
  exception allowlist stale ne reste.
- `generated/10-final-evidence.md` et `_condamad/stories/story-status.md` sont
  synchronises.

## Halt Conditions

- Un owner natal concurrent rend `features/natal-chart` ambigu.
- Un usage externe actif de l'ancien chemin est prouve.
- Une validation obligatoire echoue et aucune correction sure n'est disponible.
