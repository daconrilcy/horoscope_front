<!-- Inventaire avant migration CS-034 des styles inline statiques. -->

# CS-034 Inline Styles Before

Lot selectionne:

- `frontend/src/pages/PrivacyPolicyPage.tsx`

Classification:

- static: wrapper `privacy-policy-page` (`padding`, `maxWidth`, `margin`, `color`).
- static: lien retour (`marginBottom`).
- static: icone retour (`marginRight`), remplace par le slot `leftIcon` de `Button`.
- static: titre (`fontFamily`, `fontSize`, `marginBottom`, `color`).
- static: date de mise a jour (`marginBottom`, `lineHeight`, `color`).
- static: sections, titres et paragraphes (`marginBottom`, `fontSize`, `lineHeight`, `color`).
- dynamic: aucun dans le lot.

Commande:

```powershell
Push-Location frontend
rg -n "style=" src/pages/PrivacyPolicyPage.tsx
Pop-Location
```

Resultat initial:

- 17 occurrences `style=` dans `PrivacyPolicyPage.tsx`.
