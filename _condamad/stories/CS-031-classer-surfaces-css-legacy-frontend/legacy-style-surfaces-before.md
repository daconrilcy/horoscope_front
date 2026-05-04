<!-- Baseline des surfaces CSS legacy avant classification CS-031. -->

# Legacy Style Surfaces Before

Baseline source:

```powershell
rg -n "legacy|--text-main|--text-1|--glass|--primary" src -g "*.css"
```

Surfaces detectees:

- familles chat legacy dans `frontend/src/App.css`;
- route admin prompts legacy dans `AdminPromptsPage.css`;
- aliases de tokens `--text-*`, `--glass*` et `--primary*`.
