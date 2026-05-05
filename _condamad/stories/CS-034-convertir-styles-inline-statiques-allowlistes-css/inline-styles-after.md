<!-- Inventaire apres migration CS-034 des styles inline statiques. -->

# CS-034 Inline Styles After

Lot migre:

- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/PrivacyPolicyPage.css`
- `frontend/src/tests/design-system-allowlist.ts`

Resultat apres:

- `PrivacyPolicyPage.tsx` ne contient plus aucun `style=`.
- Les styles statiques vivent dans `PrivacyPolicyPage.css`.
- Les entrees `pages/PrivacyPolicyPage.tsx` ont ete retirees de `INLINE_STYLE_EXCEPTIONS`.
- L'icone retour utilise `Button.leftIcon`, ce qui evite une classe locale uniquement pour l'espacement de l'icone.

Commandes de preuve:

```powershell
Push-Location frontend
rg -n "style=" src/pages/PrivacyPolicyPage.tsx
npm run test -- inline-style design-system
npm run lint
Pop-Location
```

Resultats:

- `rg -n "style=" src/pages/PrivacyPolicyPage.tsx` - PASS zero hit.
- `npm run test -- inline-style css-fallback design-system` - PASS, 3 fichiers, 11 tests.
- `npm run lint` - PASS.

Exceptions restantes:

- Aucune exception inline statique pour `PrivacyPolicyPage.tsx`.
