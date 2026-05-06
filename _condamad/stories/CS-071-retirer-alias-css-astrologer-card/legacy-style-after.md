<!-- Preuve after de suppression de l'alias CSS astrologer card. -->

# CS-071 Legacy Style After

## Decisions finales

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `.astrologer-card-alias` | CSS selector | `historical-facade` | `AstrologerCard.tsx` before story | `.astrologer-card-display-name` | `delete` + `replace-consumer` | zero hit scan | Aucun |
| `extractLegacyOrAliasSelectors` | test helper | `canonical-active` | `legacy-style-policy.test.ts` | `design-system-policy.ts` | `keep` | Vitest `legacy-style` | Aucun |

## Commandes after

| Commande | Repertoire | Resultat | Synthese |
|---|---|---|---|
| `rg -n "astrologer-card-alias" src -g "*.css" -g "*.tsx" -g "*.ts"` | `frontend` | PASS, exit 1 | Zero hit. |
| `rg -n "\.([a-zA-Z0-9_-]*(legacy\|alias)[a-zA-Z0-9_-]*)\|--default_dropshadow" src -g "*.css" -g "*.tsx" -g "*.ts"` | `frontend` | PASS, exit 1 | Zero selecteur actif legacy/alias et zero `--default_dropshadow`. |
| `npm run test -- legacy-style AstrologersPage ConsultationMigration consultationStore design-system theme-tokens css-fallback visual-smoke HelpPage` | `frontend` | PASS, exit 0 | 9 fichiers, 165 tests passes. |
| `npm run lint` | `frontend` | PASS, exit 0 | TypeScript lint configs OK. |

## No Legacy

L'ancien selecteur n'est pas conserve comme wrapper, alias, fallback ou entree
registry. Le guard `legacy-style` extrait maintenant les selecteurs contenant
`legacy` ou `alias` via le helper partage `design-system-policy.ts`.
