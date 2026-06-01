# CS-437 - Supprimer Catalogues Seeds Scripts Et Prompts Nataux Legacy

<!-- Commentaire global: ce brief cadre l'extinction des sources de reintroduction des anciens prompts natals. -->

## Resume

Supprimer ou archiver les catalogues, seeds et scripts qui peuvent encore creer,
restaurer ou tester les anciens use cases natals `natal_interpretation_short`,
`natal_long_free` et `natal_interpretation` comme runtime public. CS-434 a ferme
les chemins actifs; cette story supprime les sources qui peuvent les reintroduire.

## Perimetre Inclus

1. Supprimer les entrees prompt runtime legacy dans:
   - catalogues hardcodes;
   - canonical registries;
   - seeds bootstrap;
   - scripts historiques.
2. Remplacer les tests de presence de ces prompts par des tests d'absence.
3. Supprimer les scripts qui reseedent explicitement:
   - `natal_interpretation_short`;
   - `natal_long_free`;
   - `natal_interpretation` comme Basic ou Free.
4. Supprimer les scripts legacy quand ils vivent dans un chemin executable
   (`backend/scripts`, bootstrap, ops runtime). Une conservation n'est autorisee
   que comme preuve documentaire sous `_condamad`, jamais comme script executable.
5. Mettre a jour la cartographie prompt-generation pour que le natal moderne pointe
   uniquement vers les contrats `theme_natal`.
6. Conserver `basic_natal_prompt_payload` seulement si son owner est explicitement
   le runtime contractuel `theme_astral` moderne, pas `natal_interpretation`.

## Hors Perimetre

- Modifier les prompts Guidance, Chat, Horoscope daily ou autres familles non natales.
- Supprimer les donnees deja presentes en base de developpement.
- Renommer les variantes entitlement globales.
- Construire un nouveau prompt premium.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md`
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md`
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/ops/llm/bootstrap`
- `backend/scripts`
- `backend/app/services/llm_generation/admin_prompts.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-018` - les familles supportees ne doivent pas redevenir proprietaires de prompt fallback.
  - `RG-021` - tout fallback restant doit etre classifie.
  - `RG-023` - les scripts racine doivent avoir un ownership documente.
  - `RG-149` - la cartographie prompt-generation doit rester a jour.
  - `RG-171` - Basic ne route pas par les anciennes cles.
  - `RG-173` - aucune generation publique par old raw use case.
- Required regression evidence:
  - Before/after des hits legacy dans catalogues/seeds/scripts.
  - Tests prompt governance et legacy extinction.
  - Scan de startup prouvant que les seeds archives ne sont pas appeles.
- Allowed differences:
  - Suppression de scripts obsoletes.
  - Deplacement vers `_condamad` uniquement si le contenu devient une preuve
    documentaire non executable; aucun script `.py` legacy ne reste sous
    `backend/scripts` ou `backend/app/ops/llm/bootstrap`.

## Criteres D'acceptation

1. `natal_interpretation_short` n'est plus seedable par un script runtime ou bootstrap.
2. `natal_long_free` n'est plus seedable par un script runtime ou bootstrap.
3. `natal_interpretation` ne peut plus etre mappe a Basic ou Free dans une taxonomie
   runtime.
4. Les catalogues prompt ne contiennent plus ces cles comme fallback public executable.
5. `admin_prompts.py` ne propose plus `natal_long_free` comme fallback de creation ou
   de resolution.
6. Les tests qui attendaient la presence de ces cles sont supprimes, reclasses ou
   inverses en garde d'absence.
7. `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
   est mis a jour avec le nouvel etat.
8. Les hits restants sont limites aux preuves historiques `_condamad` ou a des tests
   anti-retour explicites; aucun hit ne reste dans un script, seed, bootstrap ou
   catalogue runtime.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_assembly_resolution.py --tb=short
python -B -m pytest -q tests/architecture/test_theme_astral_prompt_contract_guard.py tests/architecture/test_legacy_natal_generation_inventory_guard.py --tb=short
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" backend/app/domain/llm/prompting backend/app/domain/llm/configuration backend/app/ops/llm/bootstrap backend/scripts backend/app/services/llm_generation/admin_prompts.py
rg -n "get_active_prompt_version\(db, \"natal_interpretation_short\"|seed_natal_short|seed_30_8_v3_prompts" backend/tests backend/app/tests backend/scripts
rg -n "theme_natal|natal_interpretation_short|natal_long_free|admin-only" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md
```

## Dependances

- CS-436 recommande avant suppression totale des anciens prompts provider-capable.

## Risques

Les tests admin LLM peuvent utiliser ces cles comme fixtures generiques. Il faut
les remplacer par des cles de test non natales ou par des cles `theme_natal`
contractuelles pour ne pas conserver un use case historique comme exemple nominal.
