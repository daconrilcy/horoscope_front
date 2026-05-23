# ASTRO-AUDIT-01 — Astrology Engine Feature Coverage Audit

## Résumé

Produire l'audit de couverture fonctionnelle du moteur astrologique post-CS-236.

L'objectif est de déterminer quelles techniques astrologiques sont déjà calculées, partiellement couvertes, seulement présentes dans le référentiel, manquantes ou hors périmètre.

Livrable attendu :

```text
_condamad/audits/astro-feature-coverage/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec la matrice obligatoire et la conclusion métier ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les écarts, manques et dettes identifiés ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques associés ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le moteur natal dispose désormais d'un runtime `chart_objects`, d'un graphe `natal_chart_v1`, de surfaces de dignités, dominance, conditions avancées, aspects, étoiles fixes et profils de signes enrichis.

Il faut maintenant décider les prochaines stories à partir d'une vision produit et astrologique complète, pas seulement à partir des surfaces déjà codées.

Référence principale :

```text
docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md
```

## Objectifs

Auditer les techniques suivantes :

- thème natal structurel ;
- dignités essentielles ;
- dignités accidentelles ;
- conditions planétaires avancées ;
- sect, hayz, rejoicing ;
- parts arabes / lots ;
- noeuds, Lilith, apsides ;
- étoiles fixes ;
- parans ;
- midpoints ;
- astéroïdes ;
- Chiron ;
- transits ;
- progressions ;
- révolutions solaires et lunaires ;
- synastrie ;
- composite ;
- profections ;
- directions symboliques ;
- firdaria / time lords si pertinent.

## Matrice obligatoire

Le document doit contenir :

| Technique / objet / condition | Statut actuel | Niveau de couverture | Dépendances runtime | Tables nécessaires | Calculateur nécessaire | Projection publique nécessaire | Priorité produit |
| --- | --- | --- | --- | --- | --- | --- | --- |

Statuts autorisés :

- `implemented`
- `partially implemented`
- `reference-only`
- `missing`
- `out-of-scope`

## Périmètre inclus

1. Inventaire statique du code backend.
2. Vérification des tests et documents existants.
3. Distinction calcul, référentiel, runtime, projection publique et entrée interprétative.
4. Priorisation produit des prochains chantiers.
5. Liste de stories candidates en sortie.

## Hors périmètre

Ne pas implémenter de nouvelle technique astrologique.

Ne pas modifier l'API publique.

Ne pas exposer `chart_objects`.

## Critères d'acceptation

1. Le dossier d'audit existe sous `_condamad/audits/astro-feature-coverage/`.
2. Tous les sujets obligatoires sont couverts.
3. Chaque sujet possède un statut autorisé.
4. Chaque statut est justifié par des preuves concrètes.
5. La conclusion ordonne les prochaines stories recommandées.

## Validation attendue

Validation documentaire :

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-feature-coverage | Sort-Object Name -Descending | Select-Object -First 1
rg -n "implemented|partially implemented|reference-only|missing|out-of-scope" "$($auditFolder.FullName)\00-audit-report.md"
rg -n "chart_objects|natal_chart_v1|fixed|transits|synastrie|progressions" "$($auditFolder.FullName)\00-audit-report.md"
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
Réalise ASTRO-AUDIT-01.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-feature-coverage/<YYYY-MM-DD-HHMM>/.
Audite la couverture fonctionnelle du moteur astrologique post-CS-236 sur toutes les techniques listées.
Classe chaque sujet en implemented, partially implemented, reference-only, missing ou out-of-scope.
Justifie chaque statut par des références au code, aux tests ou aux docs.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les prochaines stories dans 03-story-candidates.md.

Interdictions:
- pas de changement applicatif;
- pas de nouvelle API;
- pas d'exposition brute de chart_objects.
```
