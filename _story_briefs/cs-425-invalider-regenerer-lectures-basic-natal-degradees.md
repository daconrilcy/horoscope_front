# CS-425 - Invalider Ou Regenerer Les Lectures Basic Natal Degradees

<!-- Commentaire global: ce brief cadre la politique de cache/versioning pour eviter de resservir les anciennes lectures Basic illisibles. -->

## Resume

Empêcher les anciennes lectures Basic V2 generees avant CS-421/CS-424 d'etre servies comme
lectures valides apres correction du contrat redactionnel et du prompt final.

Sans cette story, le code peut etre corrige, les tests peuvent passer, et `/natal` peut continuer
d'afficher une interpretation historique degradee parce qu'elle est deja persistee et compatible
avec `basic_natal_interpretation_v2` au sens strict du schema.

## Objectif

Introduire une version editoriale Basic qui distingue:

```text
Lecture Basic compatible
=> schema Basic V2 present
=> engine basic-natal-reading-v1
=> version editoriale recente
=> contenu sans tokens interdits
=> peut etre servie depuis le cache.

Lecture Basic degradee historique
=> version editoriale absente/ancienne ou contenu mecanique detecte
=> ne doit pas etre servie comme "Complet" valide.
=> regeneration corrective ou etat controle.
```

## Perimetre Inclus

1. Ajouter une version editoriale persistante pour Basic, par exemple
   `basic_editorial_contract_version`, rattachee au payload public ou aux metadata de persistence.
2. Declarer la version issue de CS-421/CS-424 comme minimum compatible.
3. Classer les lectures Basic existantes sans version editoriale comme legacy/degraded.
4. Refuser la relecture cachee d'une Basic degradee contenant les tokens interdits du baseline:
   `cette lecture s'appuie uniquement`, `Ce repere retient`,
   `avec une confiance editoriale controlee`, labels anglais bruts, formes publiques non accentuees.
5. Reutiliser la politique corrective existante de CS-398/CS-418 quand une regeneration gratuite et
   atomique est applicable.
6. Si la regeneration n'est pas possible, exposer un etat controle demandant une regeneration sans
   afficher le contenu degrade comme lecture complete valide.
7. Ajouter des tests cache/persistence pour:
   - lecture Basic sans version editoriale;
   - lecture Basic avec ancienne version;
   - lecture Basic avec nouvelle version compatible;
   - contenu degrade detecte malgre version presente.
8. Produire un snapshot avant/apres du profil utilisateur exemple ou d'une fixture equivalente.

## Hors Perimetre

- Migrer en masse toutes les lectures historiques.
- Consommer un quota avant acceptation d'une nouvelle lecture valide.
- Modifier le rendu frontend hors etat controle necessaire.
- Changer le contrat public Basic V2 au-dela de la metadata de version editoriale.
- Faire un appel provider live en test automatise.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-150` - les rejets restent audit-only et exclus des routes publiques.
  - `RG-152` - le public ne doit pas exposer audit, carriers legacy ou signaux internes.
  - `RG-155` - pas de padding semantique ni sources vides.
  - `RG-157` - le quota `natal_chart_long` reste consomme seulement apres acceptance valide.
  - `RG-164` - Basic reste plan-backed.
  - `RG-165` - payload Basic sans PII, scores, chemins et IDs bruts.
  - `RG-166` - drafts acceptes conformes au plan.
  - `RG-167` - Basic complete persiste et relit `basic-natal-reading-v1`.
  - `RG-168` - `BasicNatalInterpretationV2` reste le contrat public canonique.
  - `RG-169` - qualite redactionnelle Basic, seulement si cree par CS-421.
  - `RG-171` - prompt final Basic redactionnel, seulement si cree par CS-424.
- Required regression evidence:
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
  - Scan: `rg -n "check_and_consume" backend/app/api/v1/routers/public/natal_interpretation.py`
  - Scan: `rg -n "basic_editorial_contract_version|basic-natal-editorial" backend/app backend/tests`
  - Snapshot avant/apres d'une relecture cache degradee.
- Registry enrichment expected:
  - Ajouter `RG-172` si la story cree une garde durable de version editoriale Basic/cache.
- Allowed differences:
  - Les anciennes lectures Basic sans version editoriale ne sont plus servies comme cache compatible.
  - Une regeneration corrective peut etre declenchee selon la politique existante.
  - Un etat controle peut remplacer l'affichage d'une lecture degradee.

## Criteres D'acceptation

1. Une lecture Basic V2 sans version editoriale est classee legacy/degraded.
2. Une lecture Basic V2 avec version editoriale inferieure au minimum compatible est classee
   legacy/degraded.
3. Une lecture Basic V2 contenant les tokens interdits du baseline est classee legacy/degraded
   meme si le schema public est valide.
4. Une lecture Basic V2 avec version editoriale compatible et contenu propre est servie depuis le
   cache sans consommer de quota.
5. Une lecture degradee eligible declenche la regeneration corrective existante sans debit quota
   avant acceptation valide.
6. Une lecture degradee non regenerable n'est pas affichee comme `Complet`; l'API/frontend expose
   un etat controle de regeneration.
7. Le frontend ou la QA live peut distinguer cache compatible, regeneration controlee et legacy
   invalidee.
8. Les rejets restent audit-only et ne sont pas exposes publiquement.
9. Aucun nouveau chemin de migration batch n'est introduit.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short
python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short
python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short
```

Scans:

```powershell
rg -n "check_and_consume" backend/app/api/v1/routers/public/natal_interpretation.py
rg -n "basic_editorial_contract_version|basic-natal-editorial" backend/app backend/tests
rg -n "cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node" backend/app backend/tests
```

## Dependances

- CS-421.
- CS-424.
- CS-423 doit s'executer apres CS-425 pour verifier le profil live.

## Risques

Le risque principal est de laisser un cache historiquement valide au niveau schema mais invalide au
niveau editorial. Cette story introduit une compatibilite cache plus stricte sans migration de masse
et sans debit quota premature.
