# CS-105 - Inventaire auth avant

- `/login` rendait directement `LoginPage` au niveau racine.
- `/register` rendait directement `RegisterPage` au niveau racine.
- `AuthLayout` existait mais n'etait pas l'ancestor route-level des routes auth publiques.
- Aucun contrat API, schema ou comportement de formulaire n'etait dans le scope.
