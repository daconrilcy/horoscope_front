# CS-336 - Supprimer Les Surfaces Legacy D'Injection LLM Natale

<!-- Commentaire global: ce brief cadre la suppression definitive des surfaces legacy d'injection astrologique dans le chemin LLM natal. -->

## Resume

Supprimer physiquement les surfaces legacy d'injection LLM natale afin qu'il ne reste qu'un seul chemin actif pour les donnees astrologiques et interpretatives: `llm_astrology_input_v1`.

Cette story intervient apres la migration des use cases natals vers le contrat moderne. Elle doit retirer les branches, schemas, placeholders et fallbacks qui permettent encore a `chart_json`, `natal_data` ou `evidence_catalog` derive de `chart_json` de servir de chemin parallele.

## Contexte

Les briefs CS-330 a CS-335 introduisent le contrat moderne, son mapping, son branchement, son auditabilite, la migration des use cases et les guards de non-regression.

Cette story transforme la transition en extinction: il ne doit plus y avoir deux process concurrents qui alimentent le generateur de prompt LLM natal.

## Prerequis

Les stories suivantes doivent etre terminees:

- CS-330 - Definir le contrat `llm_astrology_input_v1`;
- CS-331 - Mapper la richesse astrologique vers `llm_astrology_input_v1`;
- CS-332 - Brancher `llm_astrology_input_v1` dans l'execution natale;
- CS-333 - Aligner hash/evidence/audit;
- CS-334 - Migrer les use cases natals hors `chart_json`;
- CS-335 - Ajouter les guards de frontiere payload LLM.

## Source obligatoire

Lire avant implementation:

- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`
- `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`

Relire les fichiers ou dossiers qui declarent:

- les input schemas LLM;
- les placeholders de prompts;
- les assemblies/use cases natals;
- `NatalExecutionInput`;
- `ExecutionContext`;
- `PromptRenderer`;
- `LLMGateway`;
- les builders historiques de `chart_json` utilises par le chemin LLM.

## Objectif

Retirer les surfaces legacy d'injection LLM natale pour qu'il n'existe plus de fallback ou de carrier parallele a `llm_astrology_input_v1`.

## Perimetre inclus

1. Supprimer les champs legacy du chemin LLM natal quand ils ne servent plus qu'a alimenter le prompt:
   - `chart_json`;
   - `natal_data`;
   - `evidence_catalog` derive de `chart_json`;
   - aliases ou wrappers equivalents.
2. Supprimer les placeholders prompt et input schemas qui exposent `chart_json` ou `natal_data`.
3. Supprimer les fallbacks qui reconstruisent un payload prompt depuis les surfaces legacy.
4. Supprimer les branches conditionnelles de transition devenues inutiles.
5. Supprimer ou simplifier les adapters qui ne servaient qu'a maintenir le double chemin.
6. Mettre a jour la documentation technique qui mentionne encore une compatibilite active.
7. Ajouter ou conserver uniquement les guards qui prouvent l'absence du legacy.

## Hors perimetre

- Modifier le contenu editorial fin des prompts.
- Modifier l'orchestration generale de generation LLM, les providers, retries, politiques d'appel ou workflows hors retrait des carriers legacy.
- Traiter la securite, le CI ou les profils astrologues.
- Modifier les endpoints publics ou le frontend.
- Supprimer `chart_json` s'il reste necessaire a une projection publique non-LLM explicitement ownerisee ailleurs; dans ce cas, seuls ses imports, aliases et usages dans le chemin LLM natal sont retires.

## Criteres d'acceptation

1. Le chemin LLM natal ne peut plus etre alimente par `chart_json` ou `natal_data`.
2. Aucun fallback ne reconstruit une entree prompt depuis le legacy.
3. Les use cases natals ne declarent plus de placeholder legacy.
4. Les schemas modernes ne contiennent plus d'alias legacy.
5. Les branches de transition LLM natales sont supprimees.
6. Les references restantes a `chart_json` sont hors chemin LLM ou justifiees par un owner non-LLM.
7. Les tests valident l'absence du legacy plutot que sa compatibilite.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition-condition" app tests
rg -n "llm_astrology_input_v1" app tests
```

La premiere commande `rg` n'est pas un critere de zero occurrence global: chaque occurrence restante doit etre classee comme usage non-LLM ownerise, guard negatif, documentation historique, ou dette bloquante. Aucune occurrence executee par le chemin LLM natal n'est acceptable.

## Risques

Le risque principal est de supprimer le legacy dans la configuration tout en conservant un adapter ou un fallback qui continue de l'activer silencieusement. La validation doit inspecter le rendu final du payload LLM et les declarations de use case.
