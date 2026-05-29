# CS-379 - Stabiliser Contrat Public Generation Theme Natal Apres Enrichissement Prompts

<!-- Commentaire global: ce brief cadre la correction backend du contrat public natal casse apres l'enrichissement des prompts theme astral. -->

## Resume

Corriger la generation de theme natal cote API publique pour que `POST /v1/users/me/natal-chart` et `GET /v1/users/me/natal-chart/latest` retournent un payload affichable par l'application, sans regresser l'enrichissement `theme_astral_llm_input_v1` utilise par les prompts.

## Contexte

Les logs backend montrent que la generation repond `200 OK`, puis que le front recharge le dernier theme avec succes. La rupture visible est cote rendu:

```text
TypeError: Cannot read properties of undefined (reading 'is_hayz')
at TraditionalConditionsBlock (NatalExpertPanel.tsx)
```

La suspicion principale est une derive de forme entre le contrat traditionnel calcule/persiste et la projection publique consommee par `NatalExpertPanel`: certaines entrees de `traditional_conditions` existent mais ne portent pas `hayz` ou `rejoicing` dans la forme attendue. La correction ne doit pas reintroduire les anciens carriers de prompt (`chart_json`, `natal_data`, payload legacy) ni retirer les blocs enrichis recents.

Decision produit confirmee: `traditional_conditions` doit etre absent ou `null` uniquement quand le calcul fiable est impossible, par exemple en mode `no_time` ou `no_location_no_time`. L'absence ne doit pas dependre du plan commercial.

Observation runtime confirmee: le crash intervient des la creation d'un nouveau theme. La preuve doit donc commencer par le payload retourne par `POST /v1/users/me/natal-chart`, avant d'analyser `GET /latest` ou la persistence.

## Objectif

Retablir un contrat public stable pour le theme natal genere:

- `traditional_conditions` est absent/null uniquement quand les donnees de naissance ne permettent pas un calcul fiable, notamment `no_time` ou `no_location_no_time`;
- si une planete est exposee dans `traditional_conditions`, ses sous-contrats `hayz` et `rejoicing` sont complets ou l'entree est exclue avec raison explicite cote backend;
- `advanced_conditions`, `dignities`, `planet_condition_profiles`, `planet_condition_signals`, `dominant_planets` et `interpretation_adapter` restent coherents avec les enrichissements recents;
- le payload public reste separe du payload prompt/provider.

## Perimetre inclus

1. Reproduire localement la generation avec l'utilisateur test ou avec un fixture d'integration equivalent.
2. Capturer d'abord la forme exacte du JSON renvoye par `POST /v1/users/me/natal-chart`, car le crash est observe des la creation d'un nouveau theme.
3. Comparer ensuite avec `GET /v1/users/me/natal-chart/latest` pour verifier que la persistence ne deforme pas ou ne masque pas la cause initiale.
4. Identifier si la derive vient du calcul, de l'assemblage `NatalResult`, de `json_builder`, de la persistence ou de la lecture `latest`.
5. Corriger uniquement la frontiere proprietaire de la projection publique.
6. Ajouter un test d'integration qui genere un theme complet et valide la presence de `hayz.is_hayz` pour chaque entree traditionnelle exposee.
7. Ajouter un test de non-regression no-time si la logique neutralise les conditions traditionnelles.
8. Verifier que `theme_astral_llm_input_v1` et le provider payload enrichi restent inchanges hors champs explicitement justifies.

## Hors perimetre

- Modifier le prompt engineering redactionnel.
- Appeler un provider LLM reel.
- Corriger le composant React directement; cela appartient a CS-380.
- Revenir aux anciens carriers de prompt ou a une compatibilite legacy large.
- Masquer les erreurs backend en fabriquant des valeurs astrologiques cote UI.

## Sources obligatoires

- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py`
- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/runtime/natal_result_assembler.py`
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/tests/**`
- `frontend/src/api/natal-chart/index.ts`
- Logs fournis dans la demande utilisateur

## Criteres d'acceptation

1. Un test backend reproduit la generation d'un theme natal complet via `POST /v1/users/me/natal-chart` et capture la forme invalide de `traditional_conditions`.
2. Pour un theme avec heure de naissance fiable, `traditional_conditions` n'est pas `null` pour raison de plan commercial.
3. Pour chaque planete exposee dans `traditional_conditions`, `hayz.is_hayz` et `rejoicing.is_rejoicing` sont presents et booleens.
4. En mode `no_time` ou `no_location_no_time`, les blocs dependants de l'heure restent neutralises selon la politique existante.
5. Les schemas/types publics documentes par les tests correspondent au JSON reel renvoye par l'API.
6. Les tests du provider payload `theme_astral` prouvent que l'enrichissement prompt-visible n'a pas ete retire.
7. Aucun ancien carrier de prompt n'est reintroduit dans le runtime LLM.
8. Les erreurs de contrat sont explicites cote backend, pas converties en valeurs astrologiques inventees.
9. Les logs de generation restent `200 OK` uniquement si le payload public est valide.

## Commandes de validation minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral_provider_payload"
```

Validation cible si les tests existent deja sous ces chemins:

```powershell
python -B -m pytest -q tests/integration tests/unit/domain/astrology tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short
```

Scan anti-regression prompt:

```powershell
rg -n "chart_json|natal_data|legacy|llm_astrology_input_v1|theme_astral_llm_input_v1" app tests
```

Les hits `legacy` doivent etre interpretes: seuls les artefacts historiques ou les garde-fous documentes sont acceptables.

## Risques

Le risque principal est de corriger uniquement le symptome front alors que le backend publie un contrat partiel des le `POST` de creation. Cette story doit fermer la source backend de la derive ou prouver que le backend est sain avant de passer a CS-380.
