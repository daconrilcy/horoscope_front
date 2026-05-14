<!-- Baseline avant implementation de CS-162 sur les regles physiques d'orbes. -->

# Orb Rules Baseline Before

## Source JSON

Commande PowerShell:

```powershell
$data = Get-Content 'docs/recherches astro/astral_aspect_orb_rules.json' -Raw | ConvertFrom-Json
foreach ($g in $data.seed) {
  $rulesCount = if ($null -eq $g.rules) { 0 } else { @($g.rules).Count }
  $overrideCount = if ($null -eq $g.override_rules) { 0 } else { @($g.override_rules).Count }
  $copyFrom = if ($null -eq $g.copy_rules_from) { '<none>' } else { $g.copy_rules_from }
  "{0}: rules={1}; override_rules={2}; copy_rules_from={3}" -f $g.astral_system_code,$rulesCount,$overrideCount,$copyFrom
}
```

Resultat avant:

| System | Local `rules` | Local `override_rules` | `copy_rules_from` | Physical expanded count attendu |
|---|---:|---:|---|---:|
| `modern` | 39 | 0 | none | 39 |
| `traditional` | 0 | 1 | `modern` | 40 |
| `hellenistic` | 0 | 0 | `traditional` | 40 |
| `medieval` | 0 | 0 | `traditional` | 40 |

Total physique attendu par version avant story: `159`.

## Drift a corriger

- `hellenistic` et `medieval` ne portent aucune divergence locale, mais le seed deploie toutes les regles `traditional` en lignes physiques.
- `copy_rules_from` est le mecanisme documentaire actif a supprimer.
- L'etat cible attendu par version est `modern = 39`, `traditional = 40`, `hellenistic = 0`, `medieval = 0`, total `79`.
