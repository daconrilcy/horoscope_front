<!-- Inventaire final des appels fetch directs sous frontend/src/api apres convergence CS-131. -->

# CS-131 - Inventaire fetch after

Commande executee depuis `frontend`:

```powershell
rg -n "\bfetch\(" src/api -g "*.ts"
```

## Resultat

| Fichier | Ligne | Classification |
|---|---:|---|
| `src/api/client.ts` | 88 | owner canonique permanent du transport HTTP |

Tous les appels backend audites passent par `apiFetch`. Le timeout geocoding de
15 secondes est conserve via l'option `timeoutMs`.
