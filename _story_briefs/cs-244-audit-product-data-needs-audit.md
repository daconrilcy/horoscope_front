# ASTRO-AUDIT-08 — Astrology Product Data Needs Audit

## Résumé

Auditer les besoins de données des écrans produit astrologiques pour éviter d'exposer des surfaces internes uniquement parce qu'elles existent.

Livrable attendu :

```text
_condamad/audits/astro-product-data-needs/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec la matrice obligatoire et les besoins par écran ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les données manquantes, non exposables ou ambiguës ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques produit/contrat/frontend ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le frontend doit rester consommateur de projections publiques stables.

Cet audit part des écrans cibles et remonte vers les données nécessaires, projections, traductions et niveaux de simplification.

## Écrans cibles

- thème natal simple ;
- thème expert ;
- debug astrologique ;
- analyse de dominantes ;
- analyse des aspects ;
- analyse traditionnelle ;
- analyse des étoiles fixes ;
- interprétation IA ;
- export PDF ;
- interface astrologue ;
- interface utilisateur grand public.

## Questions par écran

- Quelle donnée est nécessaire ?
- La donnée existe-t-elle ?
- Est-elle publique ?
- Est-elle stable ?
- Est-elle compréhensible ?
- Faut-il une projection dédiée ?
- Faut-il une traduction ?
- Faut-il un score ?
- Faut-il masquer la complexité ?

## Matrice obligatoire

| Écran | Donnée nécessaire | Existe | Publique | Stable | Projection dédiée | Traduction | Score | Complexité à masquer | Story recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Stories candidates à qualifier

- CS-255 — Define expert natal chart public data contract.
- CS-256 — Define beginner natal chart summary projection.
- CS-257 — Add fixed-star section projection for frontend display.

## Périmètre inclus

1. Inventaire des écrans cibles.
2. Identification des données nécessaires.
3. Mapping vers données existantes ou manquantes.
4. Recommandations de projection publique.
5. Identification des besoins de traduction, scores et masquage de complexité.

## Hors périmètre

Ne pas modifier le frontend.

Ne pas ajouter d'endpoint.

Ne pas changer les serializers.

## Critères d'acceptation

1. Chaque écran cible possède une liste de données nécessaires.
2. Les données existantes mais non exposables brutes sont identifiées.
3. Les projections publiques dédiées sont recommandées.
4. Les besoins débutant, expert, astrologue et debug sont séparés.
5. Les futures stories CS-255 à CS-257 sont qualifiées.

## Validation attendue

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-product-data-needs | Sort-Object Name -Descending | Select-Object -First 1
rg -n "thème natal|expert|debug|dominantes|aspects|étoiles fixes|PDF|frontend|projection" "$($auditFolder.FullName)\00-audit-report.md"
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
Réalise ASTRO-AUDIT-08.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-product-data-needs/<YYYY-MM-DD-HHMM>/.
Pars des écrans cibles et identifie les données nécessaires, leur existence, exposition publique, stabilité, projection dédiée, traduction, score et complexité à masquer.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les stories candidates CS-255 à CS-257 dans 03-story-candidates.md.
```
