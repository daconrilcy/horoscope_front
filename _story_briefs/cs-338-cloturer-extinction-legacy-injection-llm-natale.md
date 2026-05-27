# CS-338 - Cloturer L'Extinction Legacy De L'Injection LLM Natale

<!-- Commentaire global: ce brief cadre la validation finale garantissant qu'un seul chemin d'injection LLM natal reste actif. -->

## Resume

Produire la validation finale d'extinction legacy apres suppression du code, des configurations et des tests obsoletes. Cette story doit prouver qu'il ne reste pas deux process paralleles pour alimenter le generateur de prompt LLM natal.

## Contexte

CS-336 supprime les surfaces legacy. CS-337 supprime les tests et mocks legacy. CS-338 ferme la boucle en auditant le code restant, les tests, les prompts/configurations et la documentation.

## Prerequis

Les stories suivantes doivent etre terminees:

- CS-336 - Supprimer les surfaces legacy d'injection LLM natale;
- CS-337 - Supprimer les tests et mocks legacy d'injection LLM.

## Source obligatoire

Lire avant validation:

- `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`
- `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`

## Objectif

Verifier et documenter que `llm_astrology_input_v1` est l'unique entree astrologique/interpretee du chemin LLM natal.

## Perimetre inclus

1. Scanner le code applicatif pour les references legacy restantes.
2. Scanner les tests pour les mocks, fixtures et expectations legacy restantes.
3. Scanner les prompts, input schemas et registries de use cases natals.
4. Classer chaque reference restante a `chart_json`, `natal_data`, `evidence_catalog`, `legacy` ou `fallback`:
   - hors chemin LLM et ownerisee;
   - garde negative;
   - dette a supprimer avant cloture.
5. Produire un rapport de validation final dans `_condamad/reports`.
6. Verifier que les tests modernes couvrent le chemin unique.
7. Verifier que la documentation ne decrit plus le double process comme actif.

## Hors perimetre

- Ajouter de nouvelles fonctionnalites LLM.
- Modifier le contenu editorial fin des prompts.
- Traiter la securite, le CI ou les profils astrologues.
- Modifier les endpoints publics ou le frontend.
- Reintroduire une compatibilite legacy pour faciliter les tests.

## Livrable attendu

Creer un rapport:

```text
_condamad/reports/extinction-legacy-injection-llm-natale/<YYYY-MM-DD-HHMM>/validation-extinction-legacy.md
```

Le rapport doit contenir:

1. Resume de l'etat final.
2. Liste des surfaces legacy supprimees.
3. Liste des tests/mocks legacy supprimes.
4. References restantes et justification.
5. Preuves que `llm_astrology_input_v1` est l'unique chemin LLM natal.
6. Commandes de validation executees.
7. Risques residuels.

## Criteres d'acceptation

1. Le rapport final existe au chemin attendu.
2. Le rapport prouve qu'il n'y a plus deux chemins paralleles d'injection LLM natale.
3. Les references restantes a des termes legacy sont classees et non actives dans le chemin LLM natal.
4. Les tests backend passent sans mocks legacy.
5. Les guards modernes passent et couvrent `llm_astrology_input_v1`.
6. Les docs ne presentent plus `chart_json` / `natal_data` comme entree LLM active.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition-condition" app tests ..\_condamad ..\_story_briefs
rg -n "llm_astrology_input_v1" app tests ..\_condamad ..\_story_briefs
```

La validation finale ne doit pas exiger une absence textuelle totale des termes legacy dans les rapports ou briefs historiques. Elle doit prouver qu'aucune reference restante n'est executee par le chemin LLM natal et que les seules occurrences acceptees sont des guards negatifs, des archives documentaires ou des usages non-LLM ownerises.

## Risques

Le risque principal est de confondre presence textuelle et chemin actif. Le rapport doit distinguer clairement les references restantes qui sont des guards ou historiques documentaires des references encore executees par le runtime LLM natal.
