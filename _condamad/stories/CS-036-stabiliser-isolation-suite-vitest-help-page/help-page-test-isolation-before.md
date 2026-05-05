<!-- Reproduction avant correction CS-036 de l'isolation HelpPage. -->

# CS-036 HelpPage Isolation Before

Tentative de reproduction:

```powershell
Push-Location frontend
npm run test -- HelpPage
Pop-Location
```

Resultat:

- PASS, `src/tests/HelpPage.test.tsx`, 4 tests.
- La defaillance full-suite-only signalee par l'audit n'a pas ete reproduite en execution cible.

Audit d'isolation:

- `HelpPage.test.tsx` creait un `QueryClient` par rendu, mais ne forcait pas la collecte immediate du cache.
- `afterEach` nettoyait le DOM, les globals stubbes et `localStorage`.
- Le token applicatif et l'evenement associe reposent sur `authToken.ts`; un nettoyage explicite via `clearAccessToken()` rend l'intention de reset observable.

Hypothese retenue:

- Stabiliser le test en supprimant le cache QueryClient apres chaque test (`gcTime: 0`) et en nettoyant explicitement le token d'acces.
