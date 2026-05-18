# No Legacy / DRY Guardrails - CS-185

## Invariants appliques

- `RG-093`: signes et profils restent modelises par `astral_signs`,
  `astral_sign_profiles` et taxonomies associees.
- `RG-095`: `domain/astrology` n'importe pas prediction.
- `RG-107`: les payloads libres restent confines a l'infra et convertis en
  dataclasses immutables.
- `RG-108`: pas de vocabulaire DB-backed recree en constante applicative.
- `RG-112`: pas de retour des constantes astrologiques hardcodees.
- `RG-114`: les profils structurels des signes viennent de la DB.

## Preuves attendues

- Test repository prouvant les profils DB.
- Test negatif sur profil manquant.
- Test builder prouvant la conservation des profils sans occupant.
- Guard de scan sur `ELEMENT_BY_SIGN`, `MODALITY_BY_SIGN`,
  `POLARITY_BY_SIGN`, `SIGN_PROFILE_DATA`.
- Scan prediction boundary zero-hit.

## Resultat

Aucun shim, alias, fallback silencieux, mapping local ou nouvelle dependance n'a
ete introduit.
