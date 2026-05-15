# No Legacy / DRY Guardrails

## Canonical path

- Les axes de maisons proviennent de `astral_house_axis_members` et `astral_house_axis_definitions`, charges via le repository de reference.
- Le domaine astrology consomme un contrat de donnees deja charge; il ne lit pas la DB directement.

## Forbidden legacy patterns

- Import ou appel de `resolve_house_axis`.
- Usage actif de `HOUSE_AXES`.
- Module constant `backend/app/domain/astrology/constants/house_axes.py` conserve comme source nominale.
- Fallback silencieux vers une table en dur si `house_axes` manque.

## Required negative evidence

- `rg -n "resolve_house_axis|HOUSE_AXES|house_axes" app tests ../docs`
- `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"`

## Review checklist

- Un seul owner de lecture DB des axes.
- Les 12 maisons doivent avoir une entree d'axe.
- Les tests ne valident pas l'ancien chemin comme comportement nominal.
- Les hits docs restants, s'il y en a, sont historiques ou mis a jour.

