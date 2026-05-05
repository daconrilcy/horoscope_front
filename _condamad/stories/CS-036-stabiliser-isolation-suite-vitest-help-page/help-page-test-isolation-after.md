<!-- Validation apres correction CS-036 de l'isolation HelpPage. -->

# CS-036 HelpPage Isolation After

Correctif:

- `frontend/src/tests/HelpPage.test.tsx` appelle `clearAccessToken()` en `afterEach`.
- Le `QueryClient` de test utilise `gcTime: 0` et des mutations sans retry pour eviter un cache survivant entre tests.
- Aucune assertion n'a ete affaiblie; aucun `skip` ni timeout arbitraire ajoute.

Commandes de validation:

```powershell
Push-Location frontend
npm run test -- HelpPage
npm run test
npm run lint
rg -n "skip|timeout" src/tests/HelpPage.test.tsx
Pop-Location
```

Resultats:

- `npm run test -- HelpPage` - PASS, 1 fichier, 4 tests.
- `npm run test` - PASS, 113 fichiers, 1234 tests passes, 8 skips existants.
- `npm run lint` - PASS.
- `rg -n "skip|timeout" src/tests/HelpPage.test.tsx` - PASS zero hit.

Risque residuel:

- La defaillance initiale n'a pas ete reproduite dans cette session, mais le full run apres correctif passe.
