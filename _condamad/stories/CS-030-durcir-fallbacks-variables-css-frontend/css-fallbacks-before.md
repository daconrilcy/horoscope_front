<!-- Baseline des fallbacks CSS avant durcissement CS-030. -->

# CSS Fallbacks Before

Baseline source:

```powershell
rg -n "var\(--[^,]+," src -g "*.css"
```

Le code contenait des fallbacks CSS nombreux et non classes, dont des cas
dynamiques (`--usage-progress`, `--sidebar-width`) et des compatibilites UI.
