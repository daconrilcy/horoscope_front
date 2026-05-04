# Inventaire apres - CS-025

## Chemin final

- `docs/architecture/entitlements-canonical-platform.md`

## Statut apres

- Header preserve: `Document status: historical-note`.
- Le contenu historique est conserve.

## Absence legacy

- `backend/docs/entitlements-canonical-platform.md` absent.
- `backend/docs/ownership-index.md` ne reference plus l'ancien chemin.

## Removal audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `backend/docs/entitlements-canonical-platform.md` | md path | `historical-facade` | docs tests | `docs/architecture/entitlements-canonical-platform.md` | `delete` | tests entitlement + ownership | duplicate old path |

Le contenu conserve sous `docs/architecture/` n'est pas supprime; toute suppression future exige une decision utilisateur explicite.
