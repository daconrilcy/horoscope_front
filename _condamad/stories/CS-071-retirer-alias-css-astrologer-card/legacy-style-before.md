<!-- Preuve before de la surface alias CSS astrologer card avant suppression. -->

# CS-071 Legacy Style Before

## Commandes de baseline

| Commande | Repertoire | Resultat | Synthese |
|---|---|---|---|
| `rg -n "astrologer-card-alias|alias|legacy|--default_dropshadow" frontend/src/App.css frontend/src/features/astrologers/components/AstrologerCard.tsx frontend/src/tests/legacy-style-policy.test.ts frontend/src/styles/legacy-style-surface-registry.md` | racine repo | PASS | Hits actifs sur `.astrologer-card-alias`; le guard ne detecte que `legacy`. |

## Hits initiaux

| Fichier | Ligne | Hit | Classification before |
|---|---:|---|---|
| `frontend/src/features/astrologers/components/AstrologerCard.tsx` | 109 | `className="astrologer-card-alias"` | `historical-facade` consommee par le composant. |
| `frontend/src/App.css` | 1128 | `.astrologer-card-alias` | `historical-facade` active a supprimer. |
| `frontend/src/tests/legacy-style-policy.test.ts` | 10-18 | extraction `extractLegacySelectors` | guard gap: le vocabulaire `alias` n'est pas detecte. |

## Decision before

La classe `.astrologer-card-alias` est une surface active non canonique sans
classification registry. La story impose une suppression sans alias transitoire.
