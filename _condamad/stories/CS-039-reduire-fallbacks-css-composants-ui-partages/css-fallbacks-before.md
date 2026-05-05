# CS-039 - Inventaire avant

Lot selectionne:

- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`

Commande source:

```powershell
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src/components/ui/Button frontend/src/components/ui/Card frontend/src/components/ui/Field frontend/src/components/ui/Modal frontend/src/components/ui/Select frontend/src/components/ui/Skeleton frontend/src/components/ui/UserAvatar -g "*.css"
```

Resultat avant migration: 109 fallbacks CSS dans le lot.

Classification:

| Statut | Compte | Decision |
|---|---:|---|
| canonical-token-required | 107 | remplacer par `var(--token)` |
| semantic-extension | 2 | conserver `--z-index-modal` et `--z-index-dropdown` avec registre |
