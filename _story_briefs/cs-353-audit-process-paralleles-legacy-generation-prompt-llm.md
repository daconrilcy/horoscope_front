# CS-353 - Audit Process Paralleles Legacy Generation Prompt LLM

<!-- Commentaire global: ce brief cadre l'audit dedie aux processus paralleles, legacy ou non nominaux de generation des prompts LLM. -->

## Resume

Identifier et decrire tous les processus paralleles, legacy, fallback, bootstrap ou non nominaux qui peuvent construire, modifier, enrichir ou transmettre un prompt LLM en dehors du flux natal moderne documente.

Cette story doit produire un inventaire specialise: ce qui existe, ce qui est actif, ce qui est historique, ce qui est seulement test ou seed, et ce qui pourrait encore envoyer un prompt provider.

## Contexte

Le document final de CS-350 decrit principalement le flux moderne autour de `llm_astrology_input_v1`, du gateway et des frontieres prompt-visible/backend-only. Les audits precedents mentionnent aussi des surfaces non-natales ou non nominales: guidance, chat public, horoscope daily, bootstrap seeds, fallback catalog, repair prompts, legacy carriers `chart_json`/`natal_data`, provider fallback, tests et artefacts historiques. Ces surfaces doivent etre auditees en tant que processus potentiellement paralleles.

## Objectif

Repondre explicitement aux questions suivantes:

- existe-t-il un ou plusieurs processus paralleles de generation de prompt LLM?
- ces processus peuvent-ils envoyer un prompt au provider aujourd'hui?
- utilisent-ils le meme gateway, le meme renderer, les memes assemblies ou des chemins distincts?
- utilisent-ils encore `chart_json`, `natal_data`, un resume textuel de theme natal, des seeds ou un fallback catalog?
- sont-ils nominaux, toleres, legacy, test-only, admin-only, bootstrap-only ou dette a corriger?

## Processus candidats a verifier specifiquement

1. Guidance:
   - `backend/app/services/llm_generation/guidance/guidance_service.py`
   - `backend/app/api/v1/routers/public/guidance.py`
   - `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`
2. Chat public et guidance conversationnelle:
   - `backend/app/services/llm_generation/chat/public_chat.py`
   - `backend/app/services/llm_generation/chat/chat_guidance_service.py`
   - `backend/app/services/llm_generation/shared/natal_context.py`
3. Horoscope daily:
   - `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
   - `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py`
4. Fallback catalog et no-assembly fallback:
   - `backend/app/domain/llm/configuration/catalog.py`
   - `backend/app/domain/llm/runtime/gateway.py`
   - `backend/app/ops/llm/bootstrap/**`
5. Repair prompts:
   - `backend/app/domain/llm/runtime/repair.py`
   - `backend/app/domain/llm/runtime/repair_prompter.py`
6. Legacy carriers et samples:
   - occurrences `chart_json`
   - occurrences `natal_data`
   - samples admin ou tests qui peuvent ressembler a un input prompt-visible.

## Perimetre inclus

1. Scanner toutes les surfaces `backend/app/**` qui mentionnent prompt, LLM, provider, guidance, chat, horoscope, fallback, repair, `chart_json` ou `natal_data`.
2. Classer chaque processus trouve par statut: runtime active, runtime non nominal, recovery, bootstrap/seed, test-only, admin-only, archival, dette.
3. Decrire pour chaque processus:
   - trigger;
   - owner de code;
   - source de configuration;
   - input prompt-visible;
   - renderer ou assembly utilise;
   - handoff provider;
   - frontiere avec le flux natal moderne;
   - risque si le document final l'ignore.
4. Identifier les processus paralleles qui devraient etre ajoutes ou nuances dans le document final.
5. Identifier les processus legacy qui meritent une story d'extinction, de documentation ou de guardrail.

## Hors perimetre

- Supprimer les chemins legacy.
- Modifier les prompts, assemblies, seeds ou gateway.
- Decider une migration produit.
- Faire un appel provider reel.
- Corriger directement le document final.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `backend/app/services/llm_generation/**`
- `backend/app/domain/llm/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/**`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-document-review/<YYYY-MM-DD-HHMM>/03-parallel-legacy-processes-audit.md
```

Le document doit contenir:

1. Resume executif.
2. Methode et scans executes.
3. Inventaire des processus paralleles et legacy.
4. Matrice statut par processus.
5. Detail par processus candidat.
6. Liste des processus confirmes comme provider-capable.
7. Liste des processus seulement bootstrap, test, admin ou archive.
8. Gaps documentaires.
9. Stories candidates de correction ou de documentation.

## Criteres d'acceptation

1. Guidance, chat public, horoscope daily, fallback catalog, repair prompts et carriers legacy sont tous traites explicitement.
2. Chaque processus a un statut unique et justifie.
3. Les chemins provider-capable sont distingues des seeds et tests.
4. Les processus paralleles sont decrits specifiquement, pas regroupes sous une categorie vague.
5. Les recommandations indiquent s'il faut documenter, garder, migrer, tester ou supprimer.

## Validation attendue

```powershell
rg -n "prompt|LLM|provider|guidance|chat|horoscope|fallback|repair|chart_json|natal_data" backend/app backend/tests
rg -n "parallel-legacy-processes-audit|Guidance|Chat public|Horoscope daily|fallback catalog|repair prompts|chart_json|natal_data" _condamad/audits/prompt-generation-document-review
```

## Risques

Le risque principal est de conclure trop vite que tous les chemins passent par le meme gateway. L'audit doit verifier le trigger et le handoff provider de chaque processus, pas seulement les imports.
