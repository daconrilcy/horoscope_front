# No Legacy / DRY Guardrails

## Forbidden legacy patterns

- Reintroduire `AstroCharacteristicModel`.
- Reintroduire la table active `astro_characteristics` hors downgrade de migration historique.
- Garder une cle payload public `characteristics` vide pour compatibilite.
- Parser `orb_luminaries` ou `orb_pair_overrides` depuis une table generique obsolete.
- Creer une table remplaçante sans decision explicite.

## Canonical path

- Les donnees de reference actives restent sous `planets`, `signs`, `houses`, `aspects`.
- Les overrides d'orbes consommes par le moteur restent dans les definitions d'aspects, pas dans une table generique.

## Required negative evidence

- `rg -n "AstroCharacteristicModel|astro_characteristics" backend/app backend/tests`
- `rg -n "\"characteristics\"|\\['characteristics'\\]" backend/app backend/tests`
- Classification des hits restants dans migrations/capsule/guardrails.

## Review checklist

- Aucun import runtime du modele supprime.
- Aucun seed decoratif restant.
- Aucun test ne depend du payload `characteristics`.
- Migration complete pour bases existantes.
- Pas de shim, alias, fallback ou re-export.
