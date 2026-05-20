<!-- Guardrails No Legacy et DRY CONDAMAD pour CS-204. -->

# CS-204 No Legacy / DRY Guardrails

## Interdits

- Aucun alias public `hayz_legacy`, `rejoicing_legacy`, `joy_code`,
  `sect_code`, `chart_sect_code` ou `planet_sect_code`.
- Aucun calculateur doctrinal importe par `json_builder.py` ou le frontend.
- Aucune constante locale de maisons de joie, planetes de secte, horizons ou
  genres de signes dans la projection ou l'UI.
- Aucun fallback silencieux pour reconstruire hayz ou rejoicing.

## Guards executes

- Scans constants doctrinales: PASS, zero hit.
- Scans calculateurs projection/frontend: PASS, zero hit.
- Scans derivation frontend: PASS, zero hit.
- Scan anti-extension publique `advanced_conditions.calculation_facts`: PASS,
  zero hit dans `frontend/src` et `backend/app/services/chart/json_builder.py`.
- Diff chemins interdits API/infra/prediction/migrations/seeds: PASS, aucun
  changement.

## Decision

Le bloc `traditional_conditions` est additif, normalise cote domaine depuis les
faits deja calcules, puis uniquement projete/affiche en aval.
