# ASTRO-AUDIT-07 — Calculation / Interpretation Boundary Audit

## Résumé

Auditer et verrouiller la frontière entre fait calculé, signal astrologique, scoring, interprétation, texte, prompt LLM et projection produit.

Livrable attendu :

```text
_condamad/audits/astro-calculation-interpretation-boundary/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec la grille obligatoire et les décisions de frontière ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les violations potentielles et risques de confusion ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques calcul/interprétation ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le moteur sépare déjà mieux le runtime structurel et l'interprétation.

Le prochain risque est d'introduire des tokens narratifs dans les calculateurs ou de transformer une projection LLM en vérité calculatoire.

## Grille obligatoire

| Élément | Catégorie | Owner | Surface runtime | Surface publique | Risque de confusion |
| --- | --- | --- | --- | --- | --- |

Catégories attendues :

- fait astronomique ;
- fait astrologique structurel ;
- scoring structurel ;
- signal interprétatif ;
- texte ;
- prompt LLM ;
- projection produit.

Exemples à inclure :

- longitude Mars = fait astronomique ;
- Mars maison 10 = fait astrologique structurel ;
- Mars dominant = scoring structurel ;
- Mars combatif = interprétation ;
- "Vous avez une énergie de conquête" = narration.

## Stories candidates à qualifier

- CS-252 — Define ChartInterpretationInput public/internal contract.
- CS-253 — Add interpretation-readiness projection from structural facts.
- CS-254 — Guard against narrative tokens in calculation runtime.

## Périmètre inclus

1. Inventaire des surfaces structurelles.
2. Inventaire des surfaces interprétatives.
3. Analyse des prompts et adapters LLM.
4. Identification des violations potentielles.
5. Recommandations de contrats public/interne/LLM.

## Hors périmètre

Ne pas modifier les prompts.

Ne pas changer les calculateurs.

Ne pas ajouter de projection.

## Critères d'acceptation

1. Les principales surfaces du moteur sont classées.
2. Les violations potentielles de frontière sont listées.
3. Les recommandations distinguent contrat interne, public et LLM.
4. Les futures stories CS-252 à CS-254 sont qualifiées.
5. Aucun changement applicatif n'est introduit.

## Validation attendue

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-calculation-interpretation-boundary | Sort-Object Name -Descending | Select-Object -First 1
rg -n "interpretation|prompt|narrative|LLM|ChartInterpretationInput|adapter|runtime" backend/app backend/tests docs
rg -n "fait astronomique|scoring structurel|prompt LLM|projection produit" "$($auditFolder.FullName)\00-audit-report.md"
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
Réalise ASTRO-AUDIT-07.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-calculation-interpretation-boundary/<YYYY-MM-DD-HHMM>/.
Classe les surfaces du moteur entre faits astronomiques, faits astrologiques structurels, scoring, signaux interprétatifs, texte, prompts LLM et projections produit.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les stories candidates CS-252 à CS-254 dans 03-story-candidates.md.
```
