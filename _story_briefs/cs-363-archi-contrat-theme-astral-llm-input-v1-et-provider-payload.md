# CS-363 - Archi Contrat Theme Astral LLM Input V1 Et Provider Payload

<!-- Commentaire global: ce brief cadre le rapport d'architecture du nouveau contrat stable de prompt pour la feature theme astral. -->

## Resume

Definir l'architecture cible du nouveau contrat `theme_astral_llm_input_v1` et du payload provider stable par feature. La structure doit etre identique pour `free`, `basic` et `premium`; les plans modulent uniquement les valeurs, quantites, budgets et profondeur.

## Contexte

Le modele cible est:

- le backend connait `feature`, `plan`, `astrologer_id`;
- le LLM recoit `feature_context`, `delivery_profile`, `astrologer_voice`, `input_data`, `output_contract`;
- le plan commercial reste backend-only;
- l'astrologue pilote la voix et les emphases, pas la verite astrologique;
- le moteur et les tables pilotent la matiere interpretative;
- le contrat de sortie est explicite, versionne et stable par feature.

## Objectif

Produire un rapport d'architecture qui fixe:

- le squelette JSON stable de `theme_astral_prompt_v1`;
- le contrat interne `theme_astral_llm_input_v1`;
- le role du `delivery_profile` derive du plan;
- le role de `astrologer_voice`;
- le bloc `interpretation_material` enrichi depuis les tables;
- le `output_contract` versionne;
- les tables DB a creer ou reutiliser pour versionner structures, prompts et contrats;
- la strategie bigbang de suppression legacy.

## Perimetre inclus

1. Lire les audits CS-361 et CS-362.
2. Lire les contrats existants `llm_astrology_input_v1`, assemblies, prompt versions, output schemas et personas.
3. Proposer le squelette provider stable.
4. Proposer les contrats internes Pydantic/domain.
5. Proposer la persistence versionnee en reutilisant les modeles LLM existants autant que possible.
6. Proposer les validations et guardrails.
7. Proposer la sequence de migration bigbang.

## Hors perimetre

- Modifier le code.
- Modifier les migrations.
- Ecrire les prompts finaux complets.
- Appeler un provider LLM.
- Implementer la suppression legacy.

## Sources obligatoires

- `_condamad/audits/theme-astral-prompt-contract/**/01-audit-usage-tables-textes-interpretation.md`
- `_condamad/audits/theme-astral-prompt-contract/**/02-audit-json-provider-theme-astral-actuels.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/**`
- `backend/app/infra/db/models/llm/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/migrations/versions/**llm**`

## Livrable attendu

Creer:

```text
_condamad/architecture/theme-astral-prompt-contract/<YYYY-MM-DD-HHMM>/archi-theme-astral-prompt-contract-v1.md
```

## Structure obligatoire du rapport

1. Executive summary.
2. Decisions d'architecture.
3. Non-goals.
4. Squelette provider cible.
5. Contrat `theme_astral_llm_input_v1`.
6. Bloc `interpretation_material`.
7. Bloc `astrologer_voice`.
8. Bloc `delivery_profile`.
9. Bloc `output_contract`.
10. Persistence DB et versioning.
11. Integration avec assembly/prompt registry existants.
12. Bigbang migration plan.
13. Legacy a supprimer.
14. Tests et guardrails.
15. Risques et decisions ouvertes.

## Squelette cible minimal

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

## Contraintes d'architecture

- Le LLM ne recoit pas `plan=free/basic/premium`.
- Le LLM recoit un `delivery_profile` resolu.
- Le squelette est identique entre plans pour une meme feature.
- Les champs absents doivent etre representes par tableaux vides ou objets vides stables, pas par suppression de cles.
- `astrologer_voice` influence style, ton, vocabulaire, emphases; jamais la verite astrologique.
- `interpretation_material` est derive des tables et du moteur, jamais invente dans le prompt builder.
- `output_contract` est versionne et explicite.
- Les contrats et prompts sont persistables/versionnables via les mecanismes backend existants.
- La bascule legacy est bigbang: pas de double runtime durable.

## Criteres d'acceptation

1. Le rapport tranche le squelette cible.
2. Le rapport decrit les responsabilites moteur, tables, astrologue, delivery profile et output contract.
3. Le rapport propose un schema de persistence versionnee.
4. Le rapport explique comment modifier simplement le process et les textes de prompt a l'avenir.
5. Le rapport identifie les owners backend a modifier.
6. Le rapport nomme les surfaces legacy a supprimer.
7. Le rapport propose les stories d'implementation CS-364 a CS-368.

## Validation attendue

```powershell
rg -n "theme_astral_llm_input_v1|runtime_contract|safety_contract|astrologer_voice|delivery_profile|interpretation_material|output_contract|bigbang|legacy" _condamad/architecture/theme-astral-prompt-contract
```

## Risques

Le risque principal est de creer un nouveau contrat parallele sans trajectoire de suppression. L'architecture doit prevoir une seule cible runtime et une extinction complete du legacy.
