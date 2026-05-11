# CS-146 - Implementation plan

1. Capturer le baseline runtime avant correction.
2. Corriger la navbar tablette en conservant le menu compact jusqu'a `1023px`.
3. Ajouter le comportement modal accessible au menu mobile dans l'owner navbar.
4. Compactifier le hero mobile/tablette sans supprimer la preview produit.
5. Corriger le nom accessible du H1 unique.
6. Renforcer les tests landing et produire les preuves after.

## No Legacy

Aucun wrapper, alias, fallback ou composant modal parallele n'est cree. Les changements restent dans les owners landing existants.

