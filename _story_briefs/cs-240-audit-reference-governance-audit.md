# ASTRO-AUDIT-04 — Astrology Reference Governance Audit

## Résumé

Auditer où vivent les règles astrologiques, seuils, poids et profils : référentiel DB, Python, tests ou documentation doctrinale.

Livrable attendu :

```text
_condamad/audits/astro-reference-governance/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec la matrice obligatoire et les décisions de gouvernance ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les règles dupliquées, non versionnées ou ambiguës ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques de gouvernance ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le moteur devient data-driven, mais certains seuils et poids restent dans des profils Python ou des références DB selon les sous-systèmes.

Il faut rendre explicite la gouvernance des sources pour éviter les règles dupliquées ou non versionnées.

## Matrice obligatoire

| Règle métier | Source actuelle | DB ou Python | Versionnée | Testée | Doctrine astrologique associée | Modifiable sans code |
| --- | --- | --- | --- | --- | --- | --- |

## Règles à classer

- orbes ;
- poids de dominance ;
- seuils de combustion ;
- seuils de cazimi ;
- seuils d'under beams ;
- seuils de vitesse ;
- seuils de station ;
- poids des maisons ;
- poids des dignités ;
- profils de signes ;
- règles fixed stars ;
- règles d'aspects ;
- règles d'interprétation.

## Stories candidates à qualifier

- CS-249 — Inventory astrology rule sources and static thresholds.
- CS-250 — Move planetary condition thresholds to versioned runtime reference.
- CS-251 — Add reference governance tests for rule source ownership.

## Périmètre inclus

1. Recherche statique des seuils et poids dans `backend/app`.
2. Inventaire des tables/seeds de référence astrologique.
3. Distinction règle doctrinale, paramétrage runtime et présentation produit.
4. Identification des règles non versionnées.

## Hors périmètre

Ne pas migrer de règle.

Ne pas modifier les seeds.

Ne pas créer de nouvelle table.

## Critères d'acceptation

1. Les règles critiques sont reliées à une source unique ou à une dette explicite.
2. Les seuils hardcodés restants sont listés.
3. Les règles DB et Python sont distinguées.
4. Les règles modifiables sans code sont identifiées.
5. Les prochaines stories de gouvernance sont priorisées.

## Validation attendue

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-reference-governance | Sort-Object Name -Descending | Select-Object -First 1
rg -n "orb|combust|cazimi|under_beams|station|dominance|dignit|fixed_star|threshold|weight" backend/app docs/db_seeder docs
rg -n "DB|Python|Versionnée|Doctrine|Modifiable" "$($auditFolder.FullName)\00-audit-report.md"
```

Validation CONDAMAD :

```powershell
if (-not (Test-Path -LiteralPath .\.venv\Scripts\Activate.ps1)) { throw "Missing virtual environment: .\.venv" }
. .\.venv\Scripts\Activate.ps1
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName
```

## Formulation courte pour Codex

```markdown
Réalise ASTRO-AUDIT-04.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-reference-governance/<YYYY-MM-DD-HHMM>/.
Inventorie les règles astrologiques, seuils, poids et profils.
Indique pour chacun la source actuelle, DB ou Python, versionnement, tests, doctrine associée et capacité de modification sans code.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les stories candidates CS-249 à CS-251 dans 03-story-candidates.md.
```
