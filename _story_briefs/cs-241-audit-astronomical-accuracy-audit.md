# ASTRO-AUDIT-05 — Astronomical Accuracy Audit

## Résumé

Auditer la fiabilité astronomique réelle du moteur, notamment l'usage effectif de `swisseph`, la configuration des éphémérides et les cas temporels sensibles.

Livrable attendu :

```text
_condamad/audits/astro-astronomical-accuracy/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec l'analyse de fiabilité et les golden charts attendues ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les risques astronomiques et écarts de garantie ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques de précision/reproductibilité ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le rapport post-CS-236 rappelle que le moteur simplifié existe encore.

Les garanties "audit-grade" dépendent de l'usage effectif de `swisseph`, des éphémérides et de la gestion correcte des dates, fuseaux, maisons et modes zodiacaux.

## Points à vérifier

- usage réel de `swisseph` en production ;
- interdiction du moteur simplifié hors test/dev ;
- version et hash des fichiers d'éphémérides ;
- reproductibilité des positions ;
- gestion UTC, timezone et DST ;
- cohérence UT vs TT ;
- ayanamsa sidéral ;
- topocentric ;
- altitude ;
- maisons aux hautes latitudes ;
- comportement Placidus quand le système échoue ou devient instable ;
- comparaison avec jeux de référence.

## Golden charts obligatoires

L'audit doit définir ou recommander :

- Paris normal case ;
- DST ambiguous time ;
- DST nonexistent time ;
- high latitude case ;
- Sidereal Lahiri case ;
- topocentric case ;
- whole sign case ;
- Placidus edge case.

## Stories candidates à qualifier

- CS-240 — Enforce swisseph-only production calculation mode.
- CS-241 — Add astronomical golden chart regression suite.
- CS-242 — Persist ephemeris configuration evidence in chart_result trace.

## Périmètre inclus

1. Inventaire des chemins de calcul simplifiés et `swisseph`.
2. Analyse de configuration par environnement.
3. Analyse des risques DST/timezone/UT/TT.
4. Proposition de golden charts de régression.
5. Liste des preuves à persister dans les traces de résultat.

## Hors périmètre

Ne pas supprimer le moteur simplifié.

Ne pas ajouter de golden tests dans cette story d'audit.

Ne pas modifier la configuration de production.

## Critères d'acceptation

1. Le mode de calcul actif par environnement est documenté.
2. Les risques astronomiques sont séparés des risques d'architecture.
3. Chaque golden chart possède un objectif de validation.
4. Les données d'éphémérides attendues sont listées.
5. Les futures stories CS-240 à CS-242 sont qualifiées.

## Validation attendue

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-astronomical-accuracy | Sort-Object Name -Descending | Select-Object -First 1
rg -n "swisseph|ephemeris|calculate_planet_positions|calculate_houses|timezone|UTC|ayanamsa|topocentric|placidus" backend/app backend/tests docs
rg -n "Paris|DST|Lahiri|topocentric|Placidus|whole sign" "$($auditFolder.FullName)\00-audit-report.md"
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
Réalise ASTRO-AUDIT-05.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-astronomical-accuracy/<YYYY-MM-DD-HHMM>/.
Audite l'usage réel de swisseph, le moteur simplifié, les éphémérides, UTC/timezone/DST, UT vs TT, ayanamsa, topocentric, altitude, hautes latitudes et Placidus.
Définis les golden charts attendues.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les stories candidates CS-240 à CS-242 dans 03-story-candidates.md.
```
