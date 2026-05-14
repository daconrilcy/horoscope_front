<!-- Baseline apres implementation de CS-162 sur les regles physiques d'orbes. -->

# Orb Rules Baseline After

## Source JSON

Commande PowerShell:

```powershell
$data = Get-Content 'docs/recherches astro/astral_aspect_orb_rules.json' -Raw | ConvertFrom-Json
foreach ($g in $data.seed) {
  $rulesCount = if ($null -eq $g.rules) { 0 } else { @($g.rules).Count }
  $inheritsFrom = if ($null -eq $g.inherits_from) { '<none>' } else { $g.inherits_from }
  "{0}: rules={1}; inherits_from={2}" -f $g.astral_system_code,$rulesCount,$inheritsFrom
}
```

Resultat apres:

| System | Local `rules` | `inherits_from` | Physical count attendu |
|---|---:|---|---:|
| `modern` | 39 | none | 39 |
| `traditional` | 40 | none | 40 |
| `hellenistic` | 0 | `traditional` | 0 |
| `medieval` | 0 | `traditional` | 0 |

Total physique attendu par version apres story: `79`.

## Invariant runtime

- `hellenistic` et `medieval` resolvent les regles `traditional` via `astral_systems.inherits_from_system_id`.
- Aucun groupe JSON actif ne contient `copy_rules_from`.
- Les overrides locaux enfants restent possibles via des lignes physiques locales, mais aucune copie complete du parent n'est acceptee.
