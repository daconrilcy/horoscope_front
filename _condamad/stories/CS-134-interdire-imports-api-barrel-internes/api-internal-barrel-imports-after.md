<!-- Scan final des imports @api internes au domaine API apres CS-134. -->

# CS-134 - Imports @api internes after

Commande executee depuis `frontend`:

```powershell
rg -n 'from [''"]@api' src/api -g "*.ts" -g "*.tsx"
```

Resultat: zero hit.

La garde `api-architecture` couvre tout `frontend/src/api`.
