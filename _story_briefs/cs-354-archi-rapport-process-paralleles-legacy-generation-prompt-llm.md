# CS-354 - Archi Rapport Process Paralleles Legacy Generation Prompt LLM

<!-- Commentaire global: ce brief cadre le rapport architectural qui classe les processus paralleles et legacy de generation des prompts LLM. -->

## Resume

Produire un rapport architectural a partir des audits CS-351 a CS-353 pour statuer sur la place des processus paralleles, legacy et non nominaux dans l'architecture de generation des prompts LLM.

Le nom de ce brief contient `archi` car il vise un rapport architectural.

## Contexte

CS-350 decrit le process actuel. CS-351 et CS-352 doivent valider la justesse du document et sa concordance avec le code. CS-353 doit identifier les chemins paralleles ou legacy. Il faut ensuite un rapport architectural qui dise quoi faire de ces chemins: documenter, conserver, migrer, deprecier, tester ou supprimer.

## Objectif

Produire une decision architecture claire sur:

- le flux nominal de reference;
- les flux paralleles officiellement supportes;
- les chemins legacy toleres temporairement;
- les chemins bootstrap/test/admin qui ne sont pas runtime truth;
- les fallbacks ou repairs qui restent des chemins non nominaux;
- les guardrails necessaires pour eviter qu'un chemin legacy redevienne prompt-visible par accident.

## Perimetre inclus

1. Lire les audits CS-351, CS-352 et CS-353.
2. Lire le document final CS-350.
3. Produire une taxonomy architecture des chemins de generation de prompt.
4. Produire une matrice decisionnelle par processus.
5. Produire une roadmap courte de corrections documentaires, guardrails ou stories d'extinction.
6. Identifier les decisions produit necessaires si un chemin parallele est encore provider-capable.

## Hors perimetre

- Modifier le code.
- Modifier le document final.
- Implementer la migration ou l'extinction des chemins legacy.
- Faire un audit de securite general.
- Faire un appel provider reel.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/**/01-adversarial-document-review-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/02-code-document-concordance-audit.md`
- `_condamad/audits/prompt-generation-document-review/**/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-cartography/**/architecture-prompt-generation-llm.md`
- `_condamad/reports/prompt-generation-cartography/**/report-prompt-generation-cartography.md`

## Livrable attendu

Creer:

```text
_condamad/architecture/prompt-generation-document-review/<YYYY-MM-DD-HHMM>/archi-parallel-legacy-prompt-generation-report.md
```

Le document doit contenir:

1. Executive architecture summary.
2. Source map.
3. Taxonomy des chemins de prompt generation.
4. Matrice nominal/parallele/legacy/fallback/bootstrap/test/admin.
5. Decision par processus.
6. Impacts sur le document final CS-350.
7. Guardrails requis.
8. Stories candidates, ordonnees par risque.
9. Open questions produit ou technique.

## Criteres d'acceptation

1. Chaque processus audite en CS-353 a une decision explicite.
2. Le rapport ne confond pas runtime supporte, fallback, seed, test et archive.
3. Les impacts sur le document final sont actionnables.
4. Les chemins provider-capable non nominaux ont une decision: documenter, migrer, deprecier ou supprimer.
5. Les guardrails proposes sont concrets et verifiables.

## Validation attendue

```powershell
rg -n "archi-parallel-legacy-prompt-generation-report|Taxonomy|Decision par processus|Guardrails|provider-capable" _condamad/architecture/prompt-generation-document-review
rg -n "nominal|parallele|legacy|fallback|bootstrap|test|admin" _condamad/architecture/prompt-generation-document-review
```

## Risques

Le risque principal est de produire un rapport descriptif sans decision. Cette story doit aboutir a une classification architecture exploitable par des stories de correction.
