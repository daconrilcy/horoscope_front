# CS-326 — Audit Projections Interpretatives LLM Input Readiness

## Résumé

Auditer les projections et contrats recents destines a stabiliser les faits et signaux interpretatifs avant narration LLM : `structured_facts_v1`, `beginner_summary_v1`, `client_interpretation_projection_v1`, `AINarrativeInputContract` et `narrative_answer_audit_v1`.

## Contexte

La refonte recente a introduit des builders et projections qui semblent mieux adaptes a une injection LLM qualitative que le `chart_json` historique :

- `StructuredFactsV1Builder` assemble des faits hashables depuis `ChartInterpretationInputBuilder`.
- `ClientInterpretationProjectionV1Builder` produit une projection B2C par plan depuis `structured_facts_v1`.
- `AINarrativeInputBuilder` construit un contrat IA/narration avec faits structurels, signaux interpretatifs, readiness flags et source versions.
- L'audit narratif persistant conserve `projection_hash`, `llm_input_hash`, `prompt_version`, `provider`, `model` et `evidence_refs`.

Il faut determiner si ces surfaces sont pretes a devenir les entrees principales des prompts LLM ou si elles restent seulement des projections produit/audit.

## Objectif

Produire un audit de readiness des contrats recents pour l'injection LLM, en explicitant ce qui est deja utilisable, ce qui est partiel et ce qui manque.

## Sources obligatoires

Lire et citer explicitement :

- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- tests associes sous `backend/tests/unit/domain/astrology/**`
- tests associes sous `backend/tests/unit/test_rejected_narrative_answer_workflow.py`

## Questions obligatoires

1. Quel contrat est le meilleur candidat pour devenir l'entree LLM canonique : `structured_facts_v1`, `client_interpretation_projection_v1` ou `AINarrativeInputContract` ?
2. Quels champs sont suffisamment factuels pour eviter l'invention ?
3. Quels champs sont seulement des labels de support ou de profondeur editoriale ?
4. Quelles surfaces excluent explicitement les payloads bruts, traces debug, prompt payloads ou provider responses ?
5. Quelles donnees sont hashables et donc auditables ?
6. Quels readiness flags existent deja et que prouvent-ils vraiment ?
7. Quelle granularite par plan est deja exprimee et laquelle manque pour l'injection LLM ?

## Périmètre inclus

1. Comparer les projections recentes entre elles.
2. Identifier leurs producteurs, consommateurs, tests et garanties.
3. Classer les champs comme `factuel`, `signal interpretatif`, `shaping editorial`, `audit`, `exclusion`, `debug`.
4. Verifier si ces projections sont deja branchees au pipeline LLM ou seulement au endpoint de projections.
5. Identifier les donnees nouvelles disponibles mais non injectees dans les prompts.
6. Produire une recommandation de surface cible pour l'architecture, sans l'implementer.

## Hors périmètre

- Modifier les projections.
- Modifier les prompts.
- Ajouter des champs.
- Changer les plans B2C.
- Modifier la persistence d'audit.
- Exposer des surfaces internes en API publique.

## Livrable attendu

Créer un dossier d'audit :

```text
_condamad/audits/projections-interpretatives-llm-input-readiness/<YYYY-MM-DD-HHMM>/
```

avec :

- `00-audit.md` : synthese readiness ;
- `01-contract-comparison.md` : comparaison des contrats ;
- `02-field-classification.md` : classification des champs ;
- `03-llm-readiness-matrix.md` : matrice d'aptitude a l'injection LLM ;
- `04-recommendations.md` : recommandations pour l'architecture sans implementation.

## Critères d'acceptation

1. Les trois surfaces candidates principales sont comparees.
2. Les garanties de hash, provenance, exclusion et readiness sont documentees.
3. Les tests existants sont cites.
4. Les usages actuels et non-usages dans le pipeline LLM sont explicites.
5. Une recommandation cible est formulee avec ses limites.
6. Aucune modification applicative n'est realisee.

## Validation attendue

```powershell
rg -n "structured_facts_v1|beginner_summary_v1|client_interpretation_projection_v1|AINarrativeInput|readiness_flags|evidence_refs|projection_hash|llm_input_hash" .\backend\app .\backend\tests
git status --short -- _condamad _story_briefs backend/app backend/tests
```

## Risques

Le risque principal est de choisir une projection orientee affichage client comme entree LLM canonique alors qu'elle masque volontairement des faits utiles. L'audit doit separer projection produit et contrat interne d'injection.
