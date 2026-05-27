# CS-351 - Audit Revue Adversariale Document Cartographie Prompt LLM

<!-- Commentaire global: ce brief cadre la revue adversariale du document final de cartographie de generation des prompts LLM. -->

## Resume

Produire une revue adversariale en profondeur de `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.

Cette story ne refait pas toute la cartographie. Elle cherche activement les erreurs, omissions, raccourcis, contradictions, conclusions non prouvees et formulations qui pourraient induire un futur agent en erreur.

## Contexte

Les stories CS-343 a CS-350 ont produit une serie d'audits, une architecture, un rapport et un document final de cartographie du process de generation de prompt LLM. Le document final est maintenant une source de lecture importante. Il doit donc etre challenge comme un contrat documentaire critique, pas seulement relu pour le style.

## Objectif

Verifier que le document final:

- decrit correctement le flux nominal de generation de prompt;
- cite les bons owners de code et les bons symboles;
- separe clairement prompt-visible, runtime-only, validation-only, audit-only et backend-only;
- ne transforme pas un fallback, un seed, un test ou un chemin legacy en runtime truth;
- ne masque pas les blockers connus;
- ne manque pas de surface importante identifiee par CS-343 a CS-349.

## Perimetre inclus

1. Lire le document final ligne par ligne.
2. Croiser chaque affirmation technique avec au moins une source primaire: code, audit CS-343 a CS-347, architecture CS-348 ou rapport CS-349.
3. Relever chaque affirmation non sourcee, ambigue ou trop forte.
4. Relever chaque omission qui change la comprehension du flux.
5. Produire une matrice: affirmation, source attendue, statut, correction proposee.
6. Produire une liste de corrections documentaires candidates, sans modifier le document.

## Hors perimetre

- Modifier le code applicatif.
- Modifier directement le document final.
- Refaire les audits CS-343 a CS-347.
- Produire une nouvelle architecture.
- Faire un appel provider reel.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `_condamad/architecture/prompt-generation-cartography/**/architecture-prompt-generation-llm.md`
- `_condamad/reports/prompt-generation-cartography/**/report-prompt-generation-cartography.md`

## Fichiers de code a consulter si une affirmation le requiert

- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-document-review/<YYYY-MM-DD-HHMM>/01-adversarial-document-review-audit.md
```

Le document doit contenir:

1. Resume executif.
2. Methode de revue adversariale.
3. Matrice des affirmations validees.
4. Matrice des affirmations a corriger ou a nuancer.
5. Omissions potentielles.
6. Contradictions ou tensions entre document, audits et code.
7. Corrections documentaires recommandees.
8. Decision finale: document acceptable, acceptable avec corrections, ou non acceptable.

## Criteres d'acceptation

1. Chaque finding cite un chemin de fichier et, si possible, un symbole ou une section.
2. Les critiques distinguent erreur factuelle, omission, ambiguite et risque de formulation.
3. Le rapport ne demande pas de changement runtime.
4. Les chemins legacy, fallback, seeds et tests sont explicitement controles.
5. La decision finale est justifiee par les preuves, pas par une impression generale.

## Validation attendue

```powershell
rg -n "prompt-generation-current-implementation|adversarial-document-review|affirmation|omission|contradiction" _condamad/audits/prompt-generation-document-review
rg -n "llm_astrology_input_v1|LLMGateway|PromptRenderer|fallback|legacy|backend-only|prompt-visible" _condamad/docs/prompt-generation-cartography _condamad/audits/prompt-generation-cartography
```

## Risques

Le risque principal est de produire une relecture molle qui valide le document sans prouver les points sensibles. Cette story doit chercher activement ce qui est faux ou incomplet.
