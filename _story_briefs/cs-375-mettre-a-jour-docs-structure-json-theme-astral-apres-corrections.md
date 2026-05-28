# CS-375 - Mettre A Jour Docs Structure JSON Theme Astral Apres Corrections

<!-- Commentaire global: ce brief cadre la remise a jour documentaire apres correction des profils, du birth_context et des exemples theme astral. -->

## Resume

Mettre a jour la documentation de structure JSON `theme_astral` pour qu'elle soit strictement coherente avec l'implementation corrigee et les exemples regeneres.

## Contexte

La revue a repere au moins une phrase obsolete: la documentation indique encore que CS-371 sera implemente ulterieurement alors que les exemples existent. D'autres sections devront probablement etre adaptees apres CS-372, CS-373 et CS-374.

## Objectif

Produire une documentation finale sans contradiction entre:

- architecture;
- implementation;
- profils persistants;
- payloads exemples;
- contexte de naissance structure;
- sources d'interpretation.

## Perimetre inclus

1. Lire les corrections CS-372 a CS-374.
2. Mettre a jour `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`.
3. Mettre a jour les liens vers les exemples CS-371.
4. Corriger toute mention obsolete ou future.
5. Verifier les diagrammes Mermaid.
6. Mettre a jour le README et `structure-comparison.md` des exemples si la doc les reference.
7. Verifier les scans anti-placeholder.

## Hors perimetre

- Modifier le code backend.
- Regenerer les payloads exemples.
- Ajouter une nouvelle architecture.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`

## Criteres d'acceptation

1. La documentation ne contient plus de phrase future obsolete sur CS-371.
2. Les depths documentes correspondent aux profils persistants et provider.
3. `birth_context` est documente avec ses champs structures.
4. Les sources d'interpretation sont decrites selon leur statut reel.
5. Les liens vers les exemples complets sont exacts.
6. Les diagrammes Mermaid restent valides conceptuellement.
7. Aucun placeholder ou TODO ne reste.
8. Le document precise clairement si les exemples utilisent des sources production, production-like, ou mixtes.
9. Le rapport de livraison anterieur est soit mis a jour, soit explicitement classe comme historique si les corrections le rendent obsolete.

## Commandes de validation minimales

```powershell
rg -n "expanded|complete|birth_date|birth_time_local|birth_place" _condamad\docs\prompt-generation-cartography\theme-astral-llm-json-structure-v1.md
rg -n "Quand CS-371 sera implemente|TODO|TBD|\\{\\{|\\bdeep\\b" _condamad\docs\prompt-generation-cartography\theme-astral-llm-json-structure-v1.md
rg -n "1973-04-24-1100-paris-theme-astral-v1|free-provider-payload|basic-provider-payload|premium-provider-payload" _condamad\docs\prompt-generation-cartography\theme-astral-llm-json-structure-v1.md
```

Le premier et le troisieme scan doivent trouver les elements attendus. Le second scan doit ne retourner aucun resultat, sauf mention historique explicitement annotee.

## Risques

Le risque principal est une documentation qui valide une intention et non le code. Cette story doit partir du code et des exemples finaux, pas de l'ancien plan.
