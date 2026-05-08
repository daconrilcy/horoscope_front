# CS-105 - Inventaire auth apres

- Decision owner: `AuthLayout` est le layout secondaire canonique pour `/login` et `/register`.
- `AuthLayout` est monte sous `RootLayout`.
- `/login` et `/register` sont enfants de `AuthLayout`.
- `LoginPage` et `RegisterPage` restent les owners du contenu de formulaire.
- Aucun refus produit de `AuthLayout` n'a ete constate; aucun `needs-user-decision` n'est requis pour ces deux routes.
- Guard: `frontend/src/tests/page-architecture-guards.test.ts` echoue si les routes auth redeviennent directes au niveau maitre.
