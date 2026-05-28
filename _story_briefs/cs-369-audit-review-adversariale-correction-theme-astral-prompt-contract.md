# CS-369 - Audit Review Adversariale Correction Theme Astral Prompt Contract

<!-- Commentaire global: ce brief cadre une review adversariale approfondie du nouveau contrat prompt theme astral et les corrections associees. -->

## Resume

Mener une review adversariale approfondie de l'implementation issue de CS-361 a CS-368, puis corriger tous les ecarts acceptes. L'objectif est de prouver que le nouveau contrat `theme_astral` est robuste, coherent, testable, maintenable et que le legacy ne subsiste pas sous forme active.

## Contexte

La bascule `theme_astral` introduit:

- un contrat stable `theme_astral_llm_input_v1`;
- un payload provider a squelette identique par delivery profile;
- un bloc `interpretation_material` issu des tables d'interpretation;
- un `delivery_profile` resolu a partir du plan commercial, sans exposer `free`, `basic` ou `premium` au LLM;
- une voix d'astrologue preponderante sur le style;
- une persistence/versioning DB des structures et textes;
- une suppression bigbang du legacy.

Cette surface est critique: une erreur peut produire des prompts incoherents, pauvres en interpretation, impossibles a versionner ou divergents entre plans.

## Objectif

Identifier puis corriger les defauts reels sur:

- la coherence du contrat;
- l'usage effectif des textes d'interpretation;
- la stabilite de structure entre plans;
- la separation backend-only / LLM-visible;
- la qualite du contrat de sortie;
- la persistence versionnee;
- la suppression legacy;
- les tests et guardrails.

## Perimetre inclus

1. Lire les livrables CS-361 a CS-368.
2. Lire le code implemente pour `theme_astral`.
3. Comparer les contrats persistants, DTO, builders, seeds et payloads provider.
4. Chercher activement les contradictions, duplications, chemins morts, fallbacks legacy et divergences par plan.
5. Produire un rapport adversarial avec severites.
6. Corriger les findings acceptes.
7. Ajouter ou adapter les tests necessaires.
8. Relancer lint, tests et validations ciblees.
9. Mettre a jour la documentation de synthese ou les exemples si les corrections changent le contrat.

## Hors perimetre

- Refaire l'architecture si elle est validee par CS-363.
- Ajouter une nouvelle feature autre que `theme_astral`.
- Appeler un provider LLM.
- Reintroduire une compatibilite legacy durable.

## Sources obligatoires

- `_condamad/audits/theme-astral-prompt-contract/**`
- `_condamad/architecture/theme-astral-prompt-contract/**`
- `_condamad/examples/prompt-generation-cartography/**`
- `_condamad/docs/prompt-generation-cartography/**`
- `backend/app/domain/**`
- `backend/app/services/**`
- `backend/app/ops/**`
- `backend/tests/**`
- `backend/migrations/versions/**`

## Axes de review adversariale

### Contrat et structure

- Le squelette JSON est-il strictement identique entre delivery profiles?
- Les differences entre plans sont-elles uniquement des valeurs, quantites, budgets, sections ou profondeur?
- Le contrat d'entree et le contrat de sortie sont-ils versionnes et referencables?
- Les noms de champs sont-ils stables, explicites et non redondants?
- Les messages provider evitent-ils la duplication contradictoire entre system/developer/user?

### Interpretation

- Les textes d'interpretation proviennent-ils de tables ou seeds audites?
- Chaque item `interpretation_material` a-t-il une source exploitable cote backend?
- Le builder evite-t-il les textes inventes, placeholders et constantes non sourcees?
- Le LLM recoit-il assez de matiere interpretative pour rediger, au-dela de simples faits astrologiques?
- Les quantites par profile sont-elles justifiees et testees?

### Astrologue

- `astrologer_voice` influence-t-il vraiment le style, le lexique, les emphases et les domaines de predilection?
- La voix de l'astrologue ne modifie-t-elle jamais les faits ni les regles de securite?
- Les domaines de predilection sont-ils explicites et exploitables dans le prompt?

### Securite et backend-only

- Le plan commercial reste-t-il hors payload LLM?
- Les champs audit, hash, provenance technique, debug et traces restent-ils backend-only?
- Les contraintes sante, predictions deterministes, propos offensants et anxiogenes sont-elles exprimees dans un bloc stable?
- Le contrat empeche-t-il une sortie hors schema?

### Legacy

- Aucun fallback legacy ne peut-il encore etre appele en runtime?
- Les anciens carriers `chart_json` et `natal_data` ne pilotent-ils plus le prompt `theme_astral`?
- Les tests legacy obsoletes ont-ils ete supprimes ou remplaces?

## Livrables attendus

Creer:

```text
_condamad/audits/theme-astral-prompt-contract/<YYYY-MM-DD-HHMM>/04-review-adversariale-correction-theme-astral-prompt-contract.md
```

Le rapport doit contenir:

1. Verdict global.
2. Liste des findings tries par severite.
3. Preuves sourcees pour chaque finding.
4. Decision: corrige, accepte avec risque, faux positif, hors perimetre.
5. Corrections appliquees.
6. Tests ajoutes ou modifies.
7. Commandes executees.
8. Risques residuels.

## Criteres d'acceptation

1. La review couvre tous les axes ci-dessus.
2. Chaque finding a une severite et une preuve fichier/ligne.
3. Les findings critiques et majeurs sont corriges ou explicitement bloques.
4. Les corrections restent dans le perimetre `theme_astral`.
5. Les tests prouvent que les textes d'interpretation atteignent le payload LLM.
6. Les tests prouvent que le squelette JSON est identique entre delivery profiles.
7. Les tests prouvent que le plan commercial n'est pas expose au LLM.
8. Les commandes `ruff format`, `ruff check` et `pytest` passent dans le venv.

## Commandes de validation minimales

Depuis la racine du repository:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Scans complementaires:

```powershell
rg -n "theme_astral_llm_input_v1|interpretation_material|delivery_profile|astrologer_voice|output_contract" app tests
rg -n "chart_json|natal_data|legacy|free|basic|premium" app tests
```

## Risques

Le risque principal est de faire une review trop descriptive. Cette story doit chercher les ruptures reelles de contrat et produire des corrections verifiables, pas seulement confirmer l'intention initiale.
