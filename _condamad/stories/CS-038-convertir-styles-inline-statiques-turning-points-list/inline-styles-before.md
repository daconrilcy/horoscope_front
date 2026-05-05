# CS-038 - Inventaire avant

Fichier cible: `frontend/src/components/prediction/TurningPointsList.tsx`.

Commande source:

```powershell
rg -n "style=\{" frontend/src/components/prediction/TurningPointsList.tsx
```

Resultat avant migration: 38 attributs `style={`.

Classification:

| Type | Compte | Decision |
|---|---:|---|
| static | 37 | migrer vers `TurningPointsList.css` |
| dynamic | 1 | `cursor: onTurningPointClick ? "pointer" : "default"` converti en classe conditionnelle |

Conclusion: aucune exception inline durable n'est requise pour `TurningPointsList.tsx`.
