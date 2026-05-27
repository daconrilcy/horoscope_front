# CS-355 - Audit Cloture Validation Document Cartographie Prompt LLM

<!-- Commentaire global: ce brief cadre l'audit de cloture qui verifie que la cartographie des prompts LLM est exacte apres revue adversariale. -->

## Resume

Verifier, apres CS-351 a CS-354, que le document final de cartographie des prompts LLM est complet, juste, source-aligne et qu'il mentionne correctement les processus paralleles ou legacy.

Cette story est un audit de cloture documentaire. Elle ne doit etre lancee qu'apres execution des audits et du rapport architectural precedents.

## Contexte

La serie CS-343 a CS-350 a produit la cartographie initiale. CS-351 a CS-354 doivent challenger cette cartographie et classifier les chemins paralleles ou legacy. Il faut une cloture qui confirme que les corrections documentaires attendues ont ete appliquees ou que les risques residuels sont explicitement acceptes.

## Objectif

Donner un verdict final sur le document:

- valide tel quel;
- valide avec risques residuels acceptes;
- invalide tant que certaines corrections ne sont pas appliquees.

## Perimetre inclus

1. Lire le document final courant.
2. Lire les livrables CS-351 a CS-354.
3. Verifier que chaque correction documentaire recommandee a ete appliquee ou explicitement rejetee.
4. Verifier que chaque processus parallele ou legacy identifie a une mention, une exclusion ou une decision claire.
5. Verifier que les commandes de validation documentaire passent.
6. Produire un rapport court de cloture.

## Hors perimetre

- Modifier le document final.
- Modifier le code.
- Ajouter des tests.
- Redecider l'architecture.
- Faire un appel provider reel.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/**/01-adversarial-document-review-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/02-code-document-concordance-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-document-review/**/archi-parallel-legacy-prompt-generation-report.md`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-document-review/<YYYY-MM-DD-HHMM>/04-document-validation-closure-audit.md
```

Le document doit contenir:

1. Verdict de cloture.
2. Corrections attendues et statut.
3. Processus paralleles ou legacy et statut documentaire.
4. Risques residuels acceptes.
5. Risques bloquants restants.
6. Commandes de validation executees.
7. Decision finale.

## Criteres d'acceptation

1. Chaque finding CS-351 a CS-353 est ferme, accepte ou converti en story.
2. Chaque decision CS-354 est prise en compte.
3. Les processus paralleles/legacy ne restent pas implicites.
4. Le verdict final est non ambigu.
5. Le rapport est court mais suffisamment source pour etre auditable.

## Validation attendue

```powershell
rg -n "document-validation-closure-audit|Verdict|Corrections attendues|Processus paralleles|Risques bloquants" _condamad/audits/prompt-generation-document-review
rg -n "prompt-generation-current-implementation|parallel-legacy|archi-parallel-legacy" _condamad
```

## Risques

Le risque principal est de fermer la chaine alors que des corrections documentaires restent implicites. Toute exception doit etre nommee et rattachee a une story ou a une acceptation de risque.
