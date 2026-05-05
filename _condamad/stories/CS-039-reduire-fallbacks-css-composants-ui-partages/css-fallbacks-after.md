# CS-039 - Inventaire apres

Commande de controle:

```powershell
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src/components/ui/Button frontend/src/components/ui/Card frontend/src/components/ui/Field frontend/src/components/ui/Modal frontend/src/components/ui/Select frontend/src/components/ui/Skeleton frontend/src/components/ui/UserAvatar -g "*.css"
```

Resultat apres migration:

| Statut | Avant | Apres | Delta |
|---|---:|---:|---:|
| fallbacks du lot | 109 | 2 | -107 |
| exceptions documentees conservees | 2 | 2 | 0 |

Exceptions finales conservees:

- `frontend/src/components/ui/Modal/Modal.css` - `--z-index-modal`, `2000`, semantic-extension.
- `frontend/src/components/ui/Select/Select.css` - `--z-index-dropdown`, `1000`, semantic-extension.

Registres synchronises:

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
