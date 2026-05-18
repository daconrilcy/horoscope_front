# No Legacy / DRY Guardrails

## Guardrails applicables

- RG-035: frontière du domaine prediction pur.
- RG-097: héritage et résolution canonique des règles d'orbes d'aspects.
- RG-106/RG-108/RG-112: référentiels astrologiques runtime depuis la source canonique.

## Checks

- Pas de constante d'orbe hardcodée dans le moteur.
- Pas de fallback vers des règles `any/any` inventées pour le contexte natal.
- Pas de résolution publique par version active quand un snapshot fournit un `reference_version_id`.
- Pas de deuxième chemin de chargement des profils d'aspects en dehors du référentiel
  de projection publique.
