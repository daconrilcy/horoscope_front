# ASTRO-AUDIT-02 — Runtime Surface Exposure Audit

## Résumé

Produire l'audit des surfaces runtime internes à exposer, projeter, réserver à l'admin/debug ou garder strictement internes.

Livrable attendu :

```text
_condamad/audits/astro-runtime-surface-exposure/<YYYY-MM-DD-HHMM>/
```

Le dossier d'audit CONDAMAD doit contenir les fichiers standards :

- `00-audit-report.md` avec la matrice obligatoire et les décisions explicites ;
- `01-evidence-log.md` avec les preuves reproductibles ;
- `02-finding-register.md` avec les risques, écarts et décisions ouvertes ;
- `03-story-candidates.md` avec les stories candidates priorisées ;
- `04-risk-matrix.md` avec les risques d'exposition ;
- `05-executive-summary.md` avec la synthèse décisionnelle.

## Contexte

Le rapport post-CS-236 confirme que `chart_objects` est canonique en interne mais exclu du contrat public.

Plusieurs surfaces sont utiles produit ou interprétation, mais ne doivent pas être exposées brutes :

- `chart_objects` ;
- `advanced_planetary_conditions` ;
- contacts d'étoiles fixes ;
- profils de signes enrichis ;
- `interpretation_input` ;
- hints internes d'aspects ;
- profils de condition ;
- payloads de dominance ;
- payloads de dignité.

## Objectifs

Décider pour chaque surface :

- si elle reste interne ;
- si elle mérite une projection publique dédiée ;
- si elle doit alimenter seulement l'interprétation/LLM ;
- si elle doit être accessible seulement en admin/debug ;
- si elle doit être différée.

## Matrice obligatoire

| Surface interne | Utilité produit | Risque d'exposition | Stabilité du contrat | Besoin frontend | Besoin admin/debug | Besoin LLM/interprétation | Exposition recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Décisions attendues

L'audit doit produire des décisions explicites.

Exemple attendu :

```text
chart_objects:
- ne pas exposer brut au frontend public;
- créer une projection publique contrôlée `chart_facts`;
- réserver le runtime complet à un endpoint admin/debug protégé.
```

## Stories candidates à qualifier

- CS-237 — Define public chart facts projection contract.
- CS-238 — Expose fixed star contacts through stable public projection.
- CS-239 — Add debug/admin endpoint for internal calculation graph trace.

## Hors périmètre

Ne pas ajouter d'endpoint.

Ne pas modifier les serializers publics.

Ne pas exposer de runtime brut.

## Critères d'acceptation

1. Le dossier d'audit existe sous `_condamad/audits/astro-runtime-surface-exposure/`.
2. Chaque surface auditée possède une recommandation explicite.
3. Les risques de stabilité, sécurité, couplage frontend et confusion produit sont documentés.
4. `ChartObjectRuntimeData` n'est jamais recommandé comme contrat public brut.
5. Les stories candidates sont ordonnées et justifiées.

## Validation attendue

```powershell
$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-runtime-surface-exposure | Sort-Object Name -Descending | Select-Object -First 1
rg -n "chart_objects|ChartObjectRuntimeData|projection|admin/debug|frontend|LLM" "$($auditFolder.FullName)\00-audit-report.md"
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
Réalise ASTRO-AUDIT-02.

Crée un dossier d'audit CONDAMAD sous _condamad/audits/astro-runtime-surface-exposure/<YYYY-MM-DD-HHMM>/.
Audite les surfaces runtime internes post-CS-236 et décide pour chacune: interne, projection publique dédiée, projection LLM/interprétation, admin/debug, différée ou dépréciée.
Ne recommande jamais l'exposition brute de ChartObjectRuntimeData.
Place les preuves dans 01-evidence-log.md, les écarts dans 02-finding-register.md et les futures stories CS-237, CS-238 et CS-239 dans 03-story-candidates.md.
```
