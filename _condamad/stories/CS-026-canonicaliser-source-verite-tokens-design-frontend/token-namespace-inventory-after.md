<!-- Inventaire final des namespaces CSS apres garde CS-026. -->

# Token Namespace Inventory After

Final guard: `npm run test -- design-system` depuis `frontend`.

Resultat: chaque declaration `--*:` detectee sous `frontend/src/**/*.css` a une
entree dans `frontend/src/styles/token-namespace-registry.md`.

Allowed differences:

- Ajout du registre canonique des namespaces.
- Ajout de la garde `design-system` qui compare les declarations CSS au registre.
- Aucun changement visuel attendu.
