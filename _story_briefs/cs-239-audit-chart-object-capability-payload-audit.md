# ASTRO-AUDIT-03 — Chart Object Capability & Payload Audit

## Résumé

Auditer la taxonomie `ChartObjectRuntimeData` : types d'objets, capacités, payloads, producteurs, consommateurs et projections.

Livrable attendu :

```text
_condamad/audits/astro-chart-object-capability-payload/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec la matrice obligatoire et les réponses aux questions ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les incohérences et décisions ouvertes ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques runtime/contrat ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le runtime post-CS-236 impose aux calculateurs de sélectionner les objets par capacités plutôt que par `object_type`.

Cette discipline est déjà protégée par des tests d'architecture. Il faut maintenant vérifier si la matrice de capacités et payloads est complète, cohérente et extensible.

## Matrice obligatoire

| Object type | Capabilities | Payloads requis | Payloads optionnels | Calculateurs consommateurs | Calculateurs producteurs | Projection publique | Projection interprétative |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Questions obligatoires

- Toutes les capacités ont-elles une sémantique claire ?
- Un payload peut-il exister sans capacité correspondante ?
- Une capacité peut-elle être vraie sans payload requis ?
- Les étoiles fixes sont-elles des objets ou seulement des sources de contacts ?
- Les angles doivent-ils participer aux aspects ?
- Les cuspides doivent-elles devenir aspectables ?
- Les lots doivent-ils avoir dignités, aspects, maisons ou dominance ?
- Les noeuds doivent-ils être traités comme planètes, points ou catégorie dédiée ?

## Stories candidates à qualifier

- CS-246 — Formalize chart object capability matrix.
- CS-247 — Add runtime validation for capability/payload consistency.
- CS-248 — Add support for derived calculated points as first-class chart objects.

## Périmètre inclus

1. Inventaire des `object_type` actifs.
2. Inventaire des `ChartObjectCapabilities`.
3. Inventaire des payloads runtime.
4. Liaison producteurs/consommateurs.
5. Recommandations de validation runtime.

## Hors périmètre

Ne pas modifier les dataclasses runtime.

Ne pas ajouter de capacité.

Ne pas changer le comportement des calculateurs.

## Critères d'acceptation

1. Tous les types d'objets runtime actifs sont inventoriés.
2. Chaque capacité a une signification et une conséquence calculatoire.
3. Les incohérences capacité/payload potentielles sont listées.
4. Les projections publiques et interprétatives sont distinguées.
5. Les stories candidates sont priorisées.

## Validation attendue

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-chart-object-capability-payload | Sort-Object Name -Descending | Select-Object -First 1
rg -n "ChartObjectRuntimeData|ChartObjectCapabilities|payloads|supports_" backend/app backend/tests
rg -n "capability|payload|supports_aspects|supports_dignities" "$($auditFolder.FullName)\00-audit-report.md"
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
Réalise ASTRO-AUDIT-03.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-chart-object-capability-payload/<YYYY-MM-DD-HHMM>/.
Audite la matrice object_type / capabilities / payloads / producteurs / consommateurs / projections.
Réponds aux questions sur étoiles fixes, angles, cuspides, lots et noeuds.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les stories candidates CS-246 à CS-248 dans 03-story-candidates.md.
```
