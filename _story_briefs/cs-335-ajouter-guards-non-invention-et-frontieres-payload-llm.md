# CS-335 - Ajouter Les Guards Non-Invention Et Frontieres Payload LLM

<!-- Commentaire global: ce brief cadre les tests de non-regression autour des donnees astrologiques injectees au LLM. -->

## Resume

Ajouter les tests et guards qui verrouillent la frontiere entre donnees prompt-visibles, runtime-only, validation-only et audit-only, afin de reduire l'invention astrologique et d'empecher la reintroduction accidentelle du legacy.

## Contexte

Une fois `llm_astrology_input_v1` branche dans les use cases natals, il faut prouver que:

- le LLM recoit les faits et signaux riches attendus;
- les limites/missing data sont visibles;
- les surfaces runtime brutes ne fuitent pas;
- `chart_json` / `natal_data` ne reviennent pas comme fallback silencieux;
- les donnees d'audit ou validation ne sont pas confondues avec le payload prompt.

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`

## Objectif

Construire un filet de tests de non-regression centre sur la qualite des donnees astrologiques et interpretatives donnees au generateur de prompt LLM.

## Perimetre inclus

1. Ajouter des tests qui inspectent la composition finale du payload/message prompt.
2. Verifier que les blocs `facts`, `signals`, `limits`, `evidence`, `shaping` et `provenance` sont presents quand attendus.
3. Verifier qu'un profil avec donnees manquantes expose explicitement ses limites au prompt.
4. Verifier que `ChartObjectRuntimeData`, `CalculationGraph`, `chart_json` et `natal_data` ne sont pas injectes comme payload brut dans les use cases migres.
5. Ajouter des scans ou tests de configuration contre les fallbacks legacy non declares.
6. Ajouter un test de non-duplication grossiere entre facts et signals.
7. Ajouter un test de regression sur un profil natal representatif pour garantir que la richesse du payload reste presente.

## Hors perimetre

- Modifier la securite ou le CI.
- Modifier les profils astrologues.
- Modifier le process general de generation de prompt LLM.
- Evaluer la qualite d'une reponse LLM reelle.
- Recrire les prompts redactionnels.
- Supprimer physiquement les surfaces legacy.

## Criteres d'acceptation

1. Les tests distinguent explicitement prompt-visible, runtime-only, validation-only et audit-only.
2. Les tests prouvent la presence des donnees riches attendues dans les prompts natals migres.
3. Les tests prouvent que les limites/missing data sont visibles au generateur de prompt.
4. Les tests echouent si une surface runtime brute est injectee.
5. Les tests echouent si un use case moderne retombe silencieusement vers `chart_json`.
6. Les tests ne dependent pas d'un appel LLM externe.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "prompt-visible|runtime-only|validation-only|audit-only|llm_astrology_input_v1|chart_json|natal_data|ChartObjectRuntimeData|CalculationGraph" app tests
```

## Risques

Le risque principal est de tester uniquement les builders et pas la sortie reellement donnee au generateur de prompt. Les guards doivent couvrir le rendu final ou l'objet final juste avant le gateway.
