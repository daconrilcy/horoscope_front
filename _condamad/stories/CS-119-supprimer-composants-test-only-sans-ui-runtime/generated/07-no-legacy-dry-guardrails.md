<!-- Guardrails No Legacy CS-119 pour supprimer les surfaces test-only sans compatibilite. -->

# No Legacy / DRY Guardrails - CS-119

## Forbidden

- Reintroduire un fichier composant supprime.
- Garder un import nominal ou type-only vers un composant supprime.
- Conserver un CSS orphelin dedie a un composant supprime.
- Ajouter un wrapper, alias, fallback, re-export ou barrel de compatibilite.
- Remplacer les exceptions exactes par une allowlist large ou folder-wide.
- Garder un test qui valide le composant supprime comme comportement nominal.

## Canonical State

- Les composants runtime restent ceux deja atteints par `frontend/src/main.tsx`
  ou classes `public-library-export`.
- Les surfaces CS-119 confirmees `test-only` n'ont plus de chemin actif.
- Les guards `component-usage`, `component-architecture`, `design-system` et
  `visual-smoke` restent executables sans lire de fichiers supprimes.

## Required Negative Evidence

- Scans zero-hit des symboles supprimes sous `frontend/src`.
- Scans zero-hit des chemins `components/<deleted>` et
  `components/prediction/<deleted>`.
- Scans zero-hit des CSS dedies supprimes.
- Tests `component-usage` et `component-architecture` prouvant l'absence
  d'exception stale.

## Applicable Regression Guardrails

- `RG-047`, `RG-048`, `RG-050`, `RG-056`, `RG-057`, `RG-069`, `RG-070`,
  `RG-072`, `RG-074`.

## Review Checklist

- [ ] Aucun consommateur runtime non-test n'a ete supprime.
- [ ] Aucun fichier public-library-export n'a ete supprime.
- [ ] Aucun symbole supprime ne reste en code actif.
- [ ] Aucun guard transversal n'a ete affaibli hors scope.
- [ ] Les preuves avant/apres et validation sont persistantes.
