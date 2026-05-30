# CS-398 - Rendre Le Quota Natal Complete Transactionnel Et Remedier Les Lectures Invalides

<!-- Commentaire global: ce brief cadre la consommation de quota et la remediation des lectures Basic invalides. -->

## Resume

Ne consommer le quota `natal_chart_long` qu'apres acceptation et persistance d'une lecture
complete valide. Identifier les lectures deja persistees avec chapitres dupliques, sources
vides ou schema historique incomplet et permettre leur regeneration corrective sans faire
payer une seconde fois l'utilisateur.

## Contexte

Le compte Basic de QA a consomme son quota lifetime `1/1` pour une lecture exposee avec
chapitres dupliques et zero source. Le routeur public appelle actuellement
`NatalChartLongEntitlementGate.check_and_consume()` avant la generation, puis commit apres
reponse. Un echec editorial ou une lecture insuffisante ne doit pas devenir une consommation
definitive.

## Objectif

Garantir:

```text
quota consomme = lecture valide acceptee et persistee
lecture invalide historique = regeneration corrective idempotente et auditee
```

## Perimetre inclus

1. Separer verification d'acces, reservation eventuelle et consommation finale du quota.
2. Consommer dans la meme transaction applicative que la persistance de la lecture acceptee,
   ou definir une compensation deterministe si la topologie existante l'impose.
3. Ne pas consommer apres rejet validation, rejet grounding, erreur provider ou rollback DB.
4. Detecter les lectures completes invalides: narrative absente, chapitre manque, contenu
   duplique ou sources Basic/Premium vides.
5. Definir un chemin de regeneration corrective gratuit, idempotent et audite.
6. Ne jamais muter silencieusement le texte historique; conserver la tracabilite.
7. Ajouter tests de concurrence et de non double-consommation si une reservation est ajoutee.
8. Documenter la politique de remediation et son impact frontend attendu.

## Hors perimetre

- Changer les limites commerciales des plans.
- Ajouter un reset manuel generaliste des quotas.
- Supprimer l'historique.
- Corriger le rendu frontend de l'accordeon.
- Ajouter une route admin non securisee.

## Sources obligatoires

- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py`
- `backend/app/services/entitlement/b2c_runtime_gate.py`
- `backend/app/services/quota/usage_service.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-002`, `RG-005`, `RG-006` - garder la logique metier hors du routeur HTTP.
  - `RG-150` - les rejets restent dans le workflow audit et hors relecture publique.
  - `RG-152` - seules les lectures narratives acceptees sont relues comme lectures completes.
  - `RG-157` - le quota est consomme apres acceptation et la remediation reste idempotente.
- Required regression evidence:
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
  - `pytest -q backend/tests/integration -k "natal and (quota or interpretation or rejected)"`
  - `pytest -q --long backend/app/tests/integration/test_natal_chart_long_entitlement.py backend/app/tests/integration/test_natal_interpretation_endpoint.py`
  - `rg -n "check_and_consume" backend/app/api/v1/routers/public/natal_interpretation.py`
- Registry enrichment completed:
  - `RG-157` protege la consommation post-acceptation et la regeneration corrective
    idempotente.
- Allowed differences:
  - Une lecture historiquement invalide peut etre marquee a regenerer et ne plus etre
    selectionnee comme lecture complete nominale.

## Criteres d'acceptation

1. Une sortie LLM rejetee ne decremente aucun quota.
2. Une erreur provider ou DB ne decremente aucun quota definitif.
3. Une lecture complete valide est persistee et consomme exactement une unite.
4. Une lecture Basic historique invalide est eligible a une regeneration corrective gratuite.
5. Deux demandes correctives concurrentes ne creent ni double lecture active ni double debit.
6. La politique est tracee par tests et documentation.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py
python -B -m pytest -q tests/integration --tb=short -k "natal and (quota or interpretation or rejected)"
python -B -m pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py app/tests/integration/test_natal_interpretation_endpoint.py --tb=short
rg -n "check_and_consume" app/api/v1/routers/public/natal_interpretation.py
```

## Dependances

- CS-396.

## Risques

Le risque principal est une double consommation en concurrence ou une compensation partielle.
La responsabilite transactionnelle doit vivre dans un service dedie, pas dans le routeur.
