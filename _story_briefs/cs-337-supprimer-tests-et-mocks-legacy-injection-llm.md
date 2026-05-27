# CS-337 - Supprimer Les Tests Et Mocks Legacy D'Injection LLM

<!-- Commentaire global: ce brief cadre le nettoyage des tests devenus invalides apres suppression du legacy LLM natal. -->

## Resume

Supprimer les tests, fixtures et mocks qui ne valident plus un comportement produit utile apres extinction des surfaces legacy d'injection LLM.

L'objectif est d'eviter de maintenir artificiellement des tests relatifs a `chart_json`, `natal_data`, placeholders legacy ou fallbacks supprimes. Les tests restants doivent valider le chemin unique `llm_astrology_input_v1`.

## Contexte

Apres CS-336, les tests de compatibilite legacy deviennent dangereux: ils forcent a conserver ou mocker des comportements qui n'ont plus de sens. Cette story nettoie explicitement le corpus de tests pour ne pas entretenir un second process fantome.

## Prerequis

CS-336 doit etre termine ou traite dans la meme sequence de livraison.

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`

Rechercher dans les tests:

- `chart_json`;
- `natal_data`;
- `evidence_catalog`;
- `legacy`;
- `fallback`;
- `transition`;
- placeholders historiques;
- mocks de `PromptRenderer`, `LLMGateway`, `NatalExecutionInput` ou adapters natals.

## Objectif

Retirer les tests legacy au lieu de les maintenir par mocks, et remplacer uniquement ce qui est necessaire par des tests du chemin moderne.

## Perimetre inclus

1. Inventorier les tests contenant `chart_json`, `natal_data`, `evidence_catalog`, `legacy`, `fallback` ou placeholders historiques.
2. Classer chaque test inventorie: compatibilite legacy a supprimer, comportement moderne a adapter, guard negatif a conserver, ou usage non-LLM hors scope.
3. Supprimer les tests dont l'unique but est de prouver la compatibilite `chart_json` / `natal_data` dans le chemin LLM.
4. Supprimer les fixtures et factories dediees aux placeholders legacy.
5. Supprimer les mocks qui recreent artificiellement un fallback legacy.
6. Supprimer les snapshots ou payloads attendus bases sur `chart_json` quand ils concernent le chemin LLM natal.
7. Remplacer les assertions utiles par des assertions sur `llm_astrology_input_v1`.
8. Conserver les tests negatifs qui prouvent que le legacy ne revient pas.
9. Documenter dans le rapport de livraison les tests supprimes et pourquoi ils n'ont plus de valeur.

## Hors perimetre

- Supprimer des tests relatifs a des usages non-LLM encore valides de `chart_json`.
- Masquer des echecs par skip ou xfail sans raison technique explicite.
- Mocker le legacy pour conserver des assertions obsoletes.
- Modifier le CI.
- Modifier le process general de generation de prompt LLM.

## Criteres d'acceptation

1. Aucun test ne requiert un payload LLM base sur `chart_json` ou `natal_data`.
2. Aucun mock ne recree un fallback legacy supprime.
3. Les tests modernes couvrent la presence de `llm_astrology_input_v1`.
4. Les tests negatifs couvrent l'absence de `chart_json` / `natal_data` dans le chemin LLM natal.
5. Aucun test n'est conserve uniquement pour satisfaire une ancienne compatibilite.
6. La suite backend passe sans skip/xfail opportuniste.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition|skip|xfail" tests
rg -n "llm_astrology_input_v1" tests
```

La sortie `rg` doit etre relue et classee. Les occurrences acceptables sont limitees aux guards negatifs, aux usages non-LLM ownerises ou aux references documentaires de test; aucun mock ou test de compatibilite legacy LLM ne doit rester.

## Risques

Le risque principal est de supprimer trop largement et de perdre une couverture utile sur la composition finale du prompt. Les tests supprimes doivent etre des tests de compatibilite legacy, pas des tests de comportement moderne a adapter.
