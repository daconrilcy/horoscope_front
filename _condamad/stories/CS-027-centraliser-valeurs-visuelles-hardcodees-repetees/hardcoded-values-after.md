<!-- Inventaire final des valeurs hardcodees repetees apres migration CS-027. -->

# Hardcoded Values After

Guard: `npm run test -- css-fallback` et scan cible:

```powershell
rg -n "border-radius:\s*999px;|gap:\s*8px;|gap:\s*12px;" frontend\src\App.css frontend\src\pages\admin\AdminPromptsPage.css frontend\src\pages\HelpPage.css frontend\src\pages\settings\Settings.css frontend\src\pages\AstrologerProfilePage.css
```

Resultat: zero hit pour les trois valeurs exactes migrees dans le lot.
