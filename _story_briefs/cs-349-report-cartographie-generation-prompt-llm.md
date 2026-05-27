# CS-349 - Report Cartographie Generation Prompt LLM

<!-- Commentaire global: ce brief cadre le rapport de livraison et de tracabilite de la cartographie de generation des prompts LLM. -->

## Resume

Utiliser le skill `condamad-delivery-report` pour produire un rapport de synthese evidence-based couvrant les audits, la synthese architecture et les livrables de cartographie de generation des prompts.

Le nom de ce brief contient `report` pour declencher le skill specialise.

## Contexte

CS-343 a CS-348 doivent produire plusieurs artefacts d'audit et d'architecture. Cette story consolide la preuve, les criteres d'acceptation, les commandes, les gaps et les prochaines actions dans un rapport unique.

## Objectif

Prouver la chaine:

```text
demande initiale -> briefs -> audits -> architecture -> documentation finale attendue -> validation -> risques residuels
```

## Perimetre inclus

1. Charger le skill `condamad-delivery-report`.
2. Lire les briefs CS-343 a CS-350.
3. Lire les audits CS-343 a CS-347.
4. Lire l'architecture CS-348.
5. Lire le document final CS-350 s'il existe deja, ou marquer son absence comme dependance.
6. Produire une synthese evidence-based.
7. Lister les risques residuels et les prochaines actions.

## Hors perimetre

- Modifier le code.
- Refaire les audits.
- Modifier l'architecture.
- Produire le document Mermaid final si CS-350 n'est pas executee.

## Sources obligatoires

- `.agents/skills/condamad-delivery-report/SKILL.md`
- `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md`
- `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md`
- `_story_briefs/cs-345-audit-runtime-gateway-handoff-provider-prompt-llm.md`
- `_story_briefs/cs-346-audit-inputs-astrologiques-natals-prompt-llm.md`
- `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md`
- `_story_briefs/cs-348-architecture-cartographie-generation-prompt-llm.md`
- `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md`
- `_condamad/audits/prompt-generation-cartography/**`
- `_condamad/architecture/prompt-generation-cartography/**`
- `_condamad/docs/prompt-generation-cartography/**`

## Livrable attendu

Creer:

```text
_condamad/reports/prompt-generation-cartography/<YYYY-MM-DD-HHMM>/report-prompt-generation-cartography.md
```

Le rapport doit contenir:

1. Trigger initial.
2. Map des stories et briefs.
3. Acceptance criteria par story.
4. Evidence paths.
5. Validation evidence.
6. Gaps ou contradictions.
7. Risques residuels.
8. Next actions.

## Criteres d'acceptation

1. Le rapport suit les statuts et valeurs de validation du skill.
2. Chaque claim important a un ancrage concret.
3. Les preuves manquantes sont marquees `Evidence gap`.
4. Les contradictions ne sont pas lissees.
5. Le rapport distingue audit, architecture, documentation et implementation.

## Validation attendue

```powershell
rg -n "Evidence gap|residual risk|validation|CS-343|CS-348|CS-350" _condamad/reports/prompt-generation-cartography
rg -n "report-prompt-generation-cartography" _condamad
```

## Risques

Le risque principal est de produire une synthese narrative sans preuve. Le rapport doit rester strictement ancre dans les artefacts.

