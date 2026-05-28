# CS-366 - Implementer Provider Payload Builder Theme Astral Stable Par Feature

<!-- Commentaire global: ce brief cadre le builder provider qui assemble un payload stable pour la feature theme astral. -->

## Resume

Implementer le nouveau builder de payload provider pour `theme_astral`, avec un squelette identique pour `free`, `basic` et `premium`. Le plan commercial doit rester backend-only; le LLM recoit uniquement un `delivery_profile` resolu.

## Contexte

Le contrat cible se resume ainsi:

- `theme_astral` a un prompt stable;
- le plan regle densite, quantite, budgets et contrat de retour;
- l'astrologue regle la voix;
- le moteur et les tables reglent la verite et la matiere interpretative;
- le contrat de sortie regle la forme.

## Objectif

Remplacer la construction actuelle pour la feature `theme_astral` par un payload provider stable contenant:

- `runtime_contract`;
- `safety_contract`;
- `astrologer_voice`;
- `feature_context`;
- `delivery_profile`;
- `input_data`;
- `output_contract`.

## Perimetre inclus

1. Lire CS-363, CS-364 et CS-365.
2. Implementer le builder ou adapter l'owner existant.
3. Mapper `plan` backend vers `delivery_profile` sans exposer `plan` au LLM.
4. Injecter `interpretation_material`.
5. Injecter `astrologer_voice`.
6. Eviter la duplication des donnees entre developer prompt et user payload.
7. Produire le `output_contract` explicite.
8. Ajouter tests de structure identique entre plans.
9. Ajouter tests de non-exposition du plan commercial.

## Hors perimetre

- Supprimer le legacy globalement; cela appartient a CS-367.
- Modifier les tables de textes.
- Appeler un provider LLM.
- Ajouter une UI admin.

## Sources obligatoires

- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/configuration/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/llm_generation/natal/**`
- `backend/tests/llm_orchestration/**`
- `backend/tests/unit/domain/astrology/**`

## Squelette obligatoire

```json
{
  "runtime_contract": {},
  "safety_contract": {},
  "astrologer_voice": {},
  "feature_context": {},
  "delivery_profile": {},
  "input_data": {
    "birth_context": {},
    "astrological_facts": {},
    "interpretation_material": {},
    "selected_themes": {},
    "limits": {}
  },
  "output_contract": {}
}
```

## Criteres d'acceptation

1. Les payloads `free/basic/premium` ont les memes cles au meme niveau.
2. Le LLM ne recoit jamais `plan`, `free`, `basic` ou `premium` comme label commercial.
3. Le LLM recoit `delivery_profile`.
4. `interpretation_material` est present dans tous les plans.
5. Les quantites de `interpretation_material`, facts et sections varient selon le delivery profile.
6. L'astrologue influence style, ton, vocabulaire et emphases.
7. Les donnees de verite astrologique viennent du moteur et des tables, pas de la persona.
8. Le `output_contract` est explicite et versionne.
9. Les tests comparent la structure entre plans et echouent si une cle disparait.
10. Les donnees audit-only restent hors payload LLM.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/llm_orchestration tests/unit/domain/astrology tests/integration/llm --tb=short
rg -n "theme_astral|delivery_profile|astrologer_voice|interpretation_material|output_contract|runtime_contract|safety_contract" app tests
```

## Risques

Le risque principal est de garder l'ancien `llm_astrology_input_v1` comme deuxieme contrat actif. Cette story doit preparer la bascule bigbang en gardant une seule sortie cible pour `theme_astral`.
