# ASTRO-AUDIT-06 — Calculation Graph Readiness Audit

## Résumé

Auditer si le graphe `natal_chart_v1` et le runner actuel peuvent servir de base aux futures familles de graphes astrologiques.

Livrable attendu :

```text
_condamad/audits/astro-calculation-graph-readiness/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec l'analyse du runner, du graphe et des prérequis multi-graphes ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les limites et écarts de readiness ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques d'orchestration/provenance ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le graphe natal est maintenant le coeur de l'orchestration. Il faut vérifier s'il est prêt pour :

- `transit_chart_v1` ;
- `synastry_chart_v1` ;
- `solar_return_v1` ;
- `progressed_chart_v1` ;
- `composite_chart_v1`.

## Questions obligatoires

- Le runner supporte-t-il plusieurs graphes ?
- Les nodes sont-elles vraiment pures ?
- Les outputs sont-ils typés ?
- Les dépendances sont-elles déclarées et testées ?
- Peut-on tracer l'exécution d'un graphe ?
- Peut-on rejouer un graphe ?
- Peut-on versionner un graphe ?
- Peut-on comparer deux graphes ?
- Le cache local du runner suffit-il ?
- Faut-il un cache applicatif ?
- Comment invalider par version de référentiel ?

## Stories candidates à qualifier

- CS-243 — Add calculation graph execution trace contract.
- CS-244 — Add graph manifest and node IO schema validation.
- CS-245 — Prepare graph runner for multi-chart graph families.

## Périmètre inclus

1. Analyse du runner actuel.
2. Analyse de `natal_chart_v1`.
3. Analyse du cache local, de la provenance et des erreurs de node.
4. Identification des prérequis multi-graphes.
5. Recommandations pour trace, replay, manifest et versionnement.

## Hors périmètre

Ne pas modifier le runner.

Ne pas ajouter de nouveau graphe.

Ne pas ajouter de cache applicatif.

## Critères d'acceptation

1. Les limites du runner sont documentées avec preuves.
2. Cache local, cache applicatif, provenance, debug trace et replay sont distingués.
3. Chaque famille de graphe cible possède des prérequis.
4. Les futures stories CS-243 à CS-245 sont qualifiées.
5. Aucun changement applicatif n'est introduit.

## Validation attendue

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-calculation-graph-readiness | Sort-Object Name -Descending | Select-Object -First 1
rg -n "CalculationGraphRunner|natal_chart_v1|CalculationGraphDefinition|provenance|cache|trace|node" backend/app backend/tests docs
rg -n "transit_chart_v1|synastry_chart_v1|solar_return_v1|progressed_chart_v1|composite_chart_v1" "$($auditFolder.FullName)\00-audit-report.md"
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
Réalise ASTRO-AUDIT-06.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-calculation-graph-readiness/<YYYY-MM-DD-HHMM>/.
Audite le runner et natal_chart_v1 pour les futurs graphes transits, synastrie, solar return, progressions et composite.
Distingue cache local, cache applicatif, provenance, trace, replay et invalidation par version de référentiel.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les stories candidates CS-243 à CS-245 dans 03-story-candidates.md.
```
