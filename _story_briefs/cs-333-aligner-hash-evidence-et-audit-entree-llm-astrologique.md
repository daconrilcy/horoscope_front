# CS-333 - Aligner Hash Evidence Et Audit De L'Entree LLM Astrologique

<!-- Commentaire global: ce brief cadre l'auditabilite du payload astrologique injecte au generateur de prompt LLM. -->

## Resume

Aligner `projection_hash`, `llm_input_hash`, `evidence_refs` et audit narratif autour de `llm_astrology_input_v1`, afin de prouver quelles donnees astrologiques et interpretatives ont influence le prompt.

## Contexte

Le rapport de transition indique que `evidence_catalog` est aujourd'hui ambigu: il sert surtout a la validation et ne prouve pas automatiquement le grounding prompt. La nouvelle entree LLM doit donc avoir un hash stable et une relation claire avec les preuves.

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
- `_story_briefs/cs-260-add-evidence-refs-contract-and-validation.md`
- `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`

## Objectif

Rendre l'entree LLM astrologique audit-able: une modification des faits, signaux, limites, evidence ou shaping qui influence le prompt doit modifier `llm_input_hash` ou une preuve equivalente.

## Perimetre inclus

1. Definir le calcul de hash stable de `llm_astrology_input_v1`.
2. Clarifier la relation entre `projection_hash` et `llm_input_hash`.
3. Integrer les `evidence_refs` utiles au contrat LLM.
4. Verifier que les refs presentes dans le contrat sont coherentes avec les facts/signals injectes.
5. Ajouter ou adapter les tests de stabilite et d'invalidation de hash.
6. Ajouter un test prouvant que modifier un signal interpretatif prompt-visible invalide le hash LLM.
7. Ajouter un test prouvant qu'une donnee runtime-only n'invalide pas le hash LLM si elle n'influence pas le prompt.

## Hors perimetre

- Modifier la securite, les roles admin ou les endpoints d'audit admin.
- Modifier le CI.
- Modifier les prompts redactionnels.
- Modifier le process general de generation de prompt LLM.
- Changer la politique de rejet des reponses non grounded au-dela de ce qui est necessaire pour l'entree LLM.

## Criteres d'acceptation

1. `llm_astrology_input_v1` a un hash stable et teste.
2. Le hash change quand un bloc prompt-visible pertinent change.
3. Le hash ne change pas pour une donnee runtime-only non injectee.
4. Les `evidence_refs` sont coherentes avec les facts/signals exposes.
5. La relation entre `projection_hash` et `llm_input_hash` est documentee dans le code ou dans une doc technique existante.
6. Les tests distinguent validation-only, runtime-only, audit-only et prompt-visible.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "llm_input_hash|projection_hash|evidence_refs|llm_astrology_input_v1|prompt-visible|runtime-only|validation-only|audit-only" app tests docs
```

## Risques

Le risque principal est une fausse auditabilite: stocker un hash sans garantir qu'il couvre toutes les donnees prompt-visibles. La validation doit comparer des variations controlees du payload.
