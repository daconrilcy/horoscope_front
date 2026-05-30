# CS-396 - Refuser Le Padding Semantique De La Lecture Natale Et Les Sources Vides

<!-- Commentaire global: ce brief cadre la fermeture du defaut d'integrite de projection narrative natale. -->

## Resume

Supprimer le fallback qui recopie la premiere section LLM pour remplir artificiellement les
chapitres manquants de `narrative_natal_reading_v1`. Une lecture `complete` Basic ou Premium
ne doit etre acceptee, persistee ou exposee que si elle contient cinq chapitres distincts et
des sources astrologiques vulgarisees non vides.

## Contexte

La QA live du 2026-05-30 a montre une interpretation Basic `complete` avec cinq cartes mais
seulement trois contenus distincts. `personality`, `emotional_world` et `evolution_path`
reutilisent exactement le meme texte parce que
`narrative_natal_reading_builder._pick_section_content()` retombe sur
`response.sections[0]`. Le meme payload expose `used_astrological_elements=[]`.

## Objectif

Fermer l'ecart entre le contrat produit et la projection runtime:

```text
lecture complete acceptee = 5 chapitres semantiques distincts + sources publiques non vides
lecture incomplete = rejet audite, jamais padding silencieux
```

## Perimetre inclus

1. Supprimer le fallback `response.sections[0]` du builder narratif.
2. Introduire une erreur de projection explicite lorsqu'un chapitre source requis manque.
3. Valider l'ordre et l'unicite exacte des cinq cles de chapitre.
4. Rejeter les titres ou narrations dupliques apres normalisation whitespace/casse.
5. Exiger des `used_astrological_elements` non vides pour Basic et Premium.
6. Router les echecs vers le workflow de rejet/audit existant sans exposition publique.
7. Ajouter des fixtures V2/V3 incompletes, dupliquees et nominales.
8. Mettre a jour `backend/docs/narrative-natal-reading-v1-contract.md`.

## Hors perimetre

- Enrichir la selection de faits astrologiques.
- Modifier les calculs astrologiques.
- Modifier React ou CSS.
- Ajouter un fallback legacy, un chapitre generique ou une duplication toleree.
- Modifier les quotas.

## Sources obligatoires

- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/docs/narrative-natal-reading-v1-contract.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-150` - les lectures rejetees restent hors des routes publiques.
  - `RG-152` - une lecture complete acceptee persiste et relit un contrat narratif public sain.
  - `RG-155` - le padding semantique et les sources vides restent interdits.
- Required regression evidence:
  - `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
  - `rg -n "fallback = response.sections\\[0\\]" backend/app/services/llm_generation/natal`
- Registry enrichment completed:
  - `RG-155` interdit le padding semantique et les sources vides sur les lectures completes
    Basic/Premium.
- Allowed differences:
  - Les anciennes lectures artificiellement completees peuvent devenir non relisibles et
    demander une regeneration explicite.

## Criteres d'acceptation

1. Une reponse depourvue de section emotionnelle ou d'evolution ne produit plus de chapitre
   recopie.
2. Deux chapitres distincts ne peuvent pas partager le meme texte normalise.
3. Une lecture Basic ou Premium avec zero source vulgarisee est rejetee.
4. Un rejet est audite et absent des routes publiques POST/GET/LIST.
5. Une fixture nominale fournit cinq chapitres distincts dans l'ordre attendu.
6. Aucun fallback legacy ou generique n'est introduit.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py tests/integration/test_natal_interpretation_rejected_public_boundary.py
rg -n "fallback = response.sections\\[0\\]" app/services/llm_generation/natal
```

## Dependances

- CS-395.

## Risques

Le risque principal est de transformer une degradation silencieuse en erreur utilisateur
sans chemin de regeneration clair. CS-398 doit traiter le quota et la remediation.
