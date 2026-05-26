# CS-313 — Stabiliser La Validation `pnpm lint` Après CS-308

## Résumé

CS-308 est fonctionnellement livré, mais son évidence finale signale que `pnpm lint` a été bloqué par une erreur Windows EPERM avant exécution du script. Cette story stabilise ou documente un chemin de validation standard pour que la fermeture ne repose plus sur une substitution manuelle.

## Contexte

Le rapport `_condamad/reports/CS-307-CS-311-delivery-report.md` classe CS-308 comme implémentée mais pas pleinement validée, car `pnpm lint` est `BLOCKED` dans `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/generated/10-final-evidence.md`.

## Objectif

Obtenir une preuve reproductible que le lint frontend standard passe, ou formaliser une commande Windows équivalente supportée dans la documentation/procédure du projet.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/generated/10-final-evidence.md`
- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/validation.txt`
- `frontend/package.json`
- `frontend/pnpm-lock.yaml` si présent
- `AGENTS.md`

## Périmètre inclus

1. Reproduire le blocage `pnpm lint` sur Windows/PowerShell si encore présent.
2. Identifier si l'EPERM vient de pnpm, du lock interne `node_modules/.pnpm/lock.yaml`, d'un process concurrent ou d'un script local.
3. Corriger uniquement la cause locale si elle est dans le dépôt.
4. Si la cause est environnementale, documenter une commande fallback officielle et vérifiable.
5. Mettre à jour l'évidence CS-308 ou un nouveau rapport de validation avec la commande réellement passée.

## Hors périmètre

- Changer de package manager.
- Réinstaller massivement les dépendances sans preuve de nécessité.
- Modifier la configuration TypeScript ou ESLint sans lien direct avec le blocage.
- Reformatter le frontend hors scope.

## Critères d'acceptation

1. `pnpm lint` passe depuis `frontend`, ou une limite environnementale est prouvée et une commande fallback officielle est documentée.
2. Les commandes TypeScript équivalentes restent passantes.
3. Aucun fichier applicatif n'est modifié sans nécessité.
4. La validation finale cite la cause, la commande, le résultat et le risque résiduel.

## Validation attendue

```powershell
cd frontend
pnpm lint
.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json
.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json
```

## Risques

Le risque principal est de masquer un problème outillage en acceptant indéfiniment une commande substitutive. La story doit clarifier si la substitution est temporaire ou canonique.
