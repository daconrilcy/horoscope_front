# Story 66.46: Vue detail "Resolved Prompt Assembly"

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / LLM platform operator,
I want ouvrir le detail d'une cible canonique et voir le prompt reellement compose par le gateway,
so that l'admin puisse comprendre la chaine exacte `hard policy -> assembly -> injecteurs -> rendu final -> execution profile` sans la reduire a un simple texte de prompt historique.

## Contexte

Une fois le catalogue canonique expose par 66.45, l'etape suivante consiste a pouvoir ouvrir une cible precise (`feature/subfeature/plan/locale` ou `manifest_entry_id`) et inspecter ce que le gateway execute reellement.

Le document [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) pose deja la doctrine runtime :

- il n'existe plus "un prompt unique"
- la persona reste un bloc separe du developer prompt
- la sequence de composition suit un ordre fixe
- `context_quality` peut etre gere soit par template, soit par injecteur
- les placeholders peuvent etre obligatoires, optionnels ou avec fallback
- le `ResolvedExecutionPlan` est la verite immuable de l'execution

Le backend dispose deja d'une preview assembly utile mais insuffisante pour l'ops produit :

- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py) expose `GET /preview`
- [backend/app/llm_orchestration/services/assembly_resolver.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_resolver.py) sait resoudre l'assembly et produire une preview locale
- [backend/app/llm_orchestration/services/context_quality_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/context_quality_injector.py), [backend/app/llm_orchestration/services/length_budget_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/length_budget_injector.py) et [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py) portent deja les transformations reelles
- [backend/app/llm_orchestration/policies/hard_policy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/policies/hard_policy.py) reste separee de l'assembly et de la persona

Mais la surface admin actuelle ne permet pas encore de voir clairement :

- les panneaux distincts `feature template`, `subfeature template`, `plan rules`, `persona block`, `hard policy`, `execution profile`
- le "avant / apres" du developer prompt assemble, puis enrichi par injecteurs, puis rendu
- si `context_quality` a ete traite par template ou compense par injecteur
- l'etat de resolution des placeholders (optionnel, fallback, bloquant)

Le risque actuel est de continuer a raisonner sur une notion obsolete de "prompt courant", alors que l'operateur a besoin de voir une assembly resolue fidele au gateway. Cette story doit donc produire une vue detaillee d'inspection runtime, sans appel provider reel.

## Glossaire UI canonique

- `ResolvedAssemblyView` : projection admin de lecture seule de l'inspection runtime d'une entree canonique
- `manifest_entry_id` : entree nominale d'acces a la vue detail
- `composition_sources` : artefacts sources de composition (`feature template`, `subfeature template`, `plan rules`, `persona block`, `hard policy`, `execution profile`)
- `transformation_pipeline` : etats intermediaires du developer prompt (`assembled`, `post_injectors`, `rendered`)
- `resolved_result` : resultat affiche pour comprehension operateur, incluant messages envoyes au provider, metadata de resolution et placeholders

## Scope et permissions

- Scope de la story : **lecture seule + navigation croisee**. Aucun appel provider, aucun replay, aucune mutation d'assembly ou de snapshot.
- Entree nominale : la vue detail est ouverte par `manifest_entry_id` resolu depuis le catalogue 66.45. Le tuple `feature/subfeature/plan/locale` reste contextuel, non la cle primaire d'acces.
- Affichage detaille reserve aux profils admin autorises a consulter la gouvernance LLM.
- Toute valeur sensible ou potentiellement issue de donnees utilisateur doit suivre la politique de redaction admin avant affichage.

## Acceptance Criteria

1. **Given** l'admin ouvre le detail d'une cible canonique depuis `/admin/prompts`  
   **When** la vue detail se charge  
   **Then** l'entree nominale est `manifest_entry_id`  
   **And** la vue identifie explicitement le contexte `feature`, `subfeature`, `plan`, `locale`  
   **And** elle expose la source de verite utilisee (`active_snapshot` ou fallback explicite).

2. **Given** que la vue detail melange potentiellement plusieurs natures d'information  
   **When** la story est implementee  
   **Then** l'UI est structuree en trois zones fixes :
   **And** `Sources de composition`
   **And** `Pipeline de transformation`
   **And** `Resultat resolu`
   **And** aucun ecran monolithique ne melange sans structure artefacts source, etats intermediaires et metadata finales.

3. **Given** que la composition reelle distingue plusieurs couches  
   **When** la vue detail est affichee  
   **Then** des panneaux separes affichent au minimum : `feature template`, `subfeature template`, `plan rules`, `persona block`, `hard policy`, `execution profile`.

4. **Given** que la persona est une couche stylistique separee  
   **When** la vue detail est affichee  
   **Then** la persona n'est pas fondue dans le developer prompt principal  
   **And** son bloc apparait distinctement avec son identifiant et son nom si disponibles.

5. **Given** que le prompt suit des transformations successives  
   **When** l'admin consulte la vue detail  
   **Then** un rendu `avant/apres` est disponible pour : `developer prompt assemble brut`, `developer prompt apres injecteurs`, `developer prompt rendu final`.

6. **Given** que l'operateur ne doit pas croire qu'il existe un "texte final unique"  
   **When** la zone `Resultat resolu` est affichee  
   **Then** un encart explicite liste ce qui part reellement au provider :
   **And** `system / hard policy`
   **And** `developer content rendu`
   **And** `persona block` separe si present
   **And** `execution parameters`
   **And** la vue n'emploie pas le terme ambigu `prompt final` sans expliquer cette decomposition.

7. **Given** que `context_quality` peut etre gere de deux manieres  
   **When** la cible est resolue  
   **Then** la vue detail affiche clairement si `context_quality` est `handled_by_template`, `injector_applied`, `not_needed` ou `unknown`.

8. **Given** que le rendu peut echouer sur des placeholders bloquants  
   **When** l'admin consulte l'inspection des placeholders  
   **Then** chaque placeholder visible expose au minimum :
   **And** son nom
   **And** son statut (`resolved`, `optional_missing`, `fallback_used`, `blocking_missing`)
   **And** sa source de resolution ou sa raison de fallback si disponible
   **And** un indicateur `safe_to_display` ou equivalent
   **And** la valeur brute n'est affichee integralement que si elle est explicitement classifiee comme sure pour l'admin.

9. **Given** qu'une preview admin ne doit pas declencher un appel LLM reel  
   **When** la vue detail est affichee ou rafraichie  
   **Then** aucune execution provider n'est lancee  
   **And** la vue repose exclusivement sur resolution locale, injecteurs, rendering et metadata runtime.

10. **Given** qu'un execution profile pilote les parametres techniques  
   **When** la vue detail est affichee  
   **Then** elle montre le provider, le modele, les profils stables (`reasoning`, `verbosity`) et les parametres provider resolus quand disponibles.

11. **Given** qu'une cible est resolue depuis un snapshot actif  
   **When** la vue detail est affichee  
   **Then** elle relie l'inspection au `active_snapshot_id`, `active_snapshot_version` et `manifest_entry_id` correspondants.

12. **Given** qu'un placeholder bloquant, une dependance manquante, une manifest entry orpheline ou un snapshot absent est rencontre  
    **When** la vue detail est affichee  
    **Then** l'admin voit explicitement l'etat d'erreur ou de blocage  
    **And** le systeme n'essaie pas de "corriger" silencieusement la preview par une logique alternative.

13. **Given** que certains blocs peuvent contenir des donnees sensibles ou du contenu utilisateur  
    **When** la vue detail affiche des placeholders resolus, du contexte rendu ou des messages  
    **Then** la politique de redaction admin existante est appliquee avant affichage  
    **And** les champs non surs sont masques, tronques ou remplaces par une representation redacted stable.

## Tasks / Subtasks

- [x] Task 1: Auditer la preview assembly existante et definir la projection detail cible (AC: 2, 4, 5, 6, 7, 8, 9)
  - [x] Lire `PromptAssemblyPreview` et les modeles associes dans [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py)
  - [x] Identifier les donnees deja disponibles et les trous a combler pour afficher la chaine complete de composition
  - [x] Definir un schema de reponse detail stable oriente "inspection runtime", distinct d'un CRUD assembly brut

- [x] Task 2: Etendre le backend de preview/detail sans appel provider (AC: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
  - [x] Ajouter ou enrichir un endpoint du type `GET /v1/admin/llm/catalog/{manifest_entry_id}/resolved` ou equivalent stable
  - [x] Y exposer les blocs separes : `feature_template`, `subfeature_template`, `plan_rules`, `persona_block`, `hard_policy`, `execution_profile`
  - [x] Exposer les etats de transformation : `assembled_prompt`, `post_injectors_prompt`, `rendered_prompt`
  - [x] Exposer les metadata `context_quality_handled_by_template`, `context_quality_instruction_injected`, `context_compensation_status`
  - [x] Exposer un tableau structure de resolution des placeholders avec leur classification, leur etat final, leur source de resolution et leur niveau de redaction
  - [x] Appliquer la politique de redaction admin avant serialization de la reponse detail
  - [x] Verrouiller le chemin detail pour qu'il n'appelle ni provider runtime manager, ni client provider, ni methode reseau de generation

- [x] Task 3: Construire l'ecran detail frontend (AC: 1, 2, 3, 4, 5, 6, 8, 9, 10)
  - [x] Ajouter un panneau detail ou une sous-route dediee depuis `/admin/prompts`
  - [x] Afficher les couches du pipeline dans l'ordre du runtime reel
  - [x] Afficher clairement la separation entre hard policy, developer prompt et persona
  - [x] Ajouter une presentation "avant / apres" facilement lisible, sans styles inline

- [x] Task 4: Tester la fidelite de l'inspection (AC: 4, 5, 6, 7, 8, 10)
  - [x] Ajouter des tests backend couvrant un cas `context_quality` gere par template et un cas injecte
  - [x] Ajouter des tests backend couvrant placeholder resolu, fallback utilise et placeholder bloquant
  - [x] Ajouter des tests frontend couvrant l'affichage des panneaux separes et la vue avant/apres

- [x] Task 5: Verification locale obligatoire
  - [x] Si du code Python est modifie, activer le venv avec `.\.venv\Scripts\Activate.ps1`, puis executer `cd backend`, `ruff format .`, `ruff check .`, `pytest -q`
  - [x] Executer aussi les tests frontend cibles lies a la page admin prompts/detail si le frontend est modifie

## Dev Notes

### Diagnostic exact a preserver

- Le point a montrer n'est pas "quel texte de prompt est stocke en base", mais "quelle assembly resolue le gateway utiliserait maintenant"
- La persona doit rester un bloc separe. Une UI qui la concatene dans le prompt principal masque la doctrine 66.17
- L'ordre d'inspection doit suivre le runtime : assembly brute, injecteurs, rendu final
- La preview doit rester locale et deterministe. Si l'ecran detail fait un appel provider, il sort du scope et devient un replay ou une simulation, pas une inspection
- Les placeholders et `context_quality` sont des sujets de gouvernance prioritaires. La vue detail doit les rendre lisibles sans lecture de code

### Ce que le dev ne doit pas faire

- Ne pas reduire l'ecran detail a un simple `textarea` de prompt final
- Ne pas melanger persona et developer prompt dans la meme boite de texte
- Ne pas dupliquer une logique divergente de rendering juste pour l'admin
- Ne pas masquer les placeholders bloquants par des valeurs fictives en UI
- Ne pas introduire un endpoint "preview detail" qui execute une reponse LLM reelle
- Ne pas exposer brut des valeurs de placeholders ou contenus qui devraient etre redacted

### Fichiers a inspecter en priorite

- [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/llm_orchestration/services/assembly_admin_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_admin_service.py)
- [backend/app/llm_orchestration/services/assembly_resolver.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_resolver.py)
- [backend/app/llm_orchestration/services/context_quality_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/context_quality_injector.py)
- [backend/app/llm_orchestration/services/length_budget_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/length_budget_injector.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/policies/hard_policy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/policies/hard_policy.py)
- [frontend/src/pages/admin/AdminPromptsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)
- [frontend/src/pages/admin/AdminPromptsPage.css](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css)

### Previous Story Intelligence

- **66.8** a introduit `PromptAssemblyPreview` et le pattern de preview locale, sans appel LLM
- **66.12**, **66.13** et **66.14** ont fait des budgets de longueur, placeholders et `context_quality` des dimensions structurelles du prompt ; l'ecran detail doit donc les rendre visibles
- **66.17** a verrouille la responsabilite exclusive des couches ; la vue detail doit respecter cette separation
- **66.27** a insiste sur la propagation fidele de `context_quality_handled_by_template` jusqu'a l'observabilite ; cette metadata doit etre exposee telle quelle, pas rederivee de maniere approximative
- **66.45** fournit la table catalogue d'entree vers ce detail

### Testing Requirements

- Ajouter un test backend sur un detail resolu contenant les panneaux distincts `feature/subfeature/plan/persona/hard_policy/profile`
- Ajouter un test backend sur la chaine `assembled -> post_injectors -> rendered`
- Ajouter un test backend sur l'etat des placeholders (`resolved`, `fallback_used`, `blocking_missing`)
- Ajouter un test backend de redaction appliquée sur des placeholders sensibles
- Ajouter un test explicite qui echoue si le chemin admin detail appelle `ProviderRuntimeManager`, un client provider ou une methode reseau de generation
- Ajouter un test frontend d'affichage des panneaux separes et du rendu avant/apres
- Verifier explicitement qu'aucun endpoint de detail n'appelle le provider runtime reel

### Project Structure Notes

- Story backend + frontend admin
- Reutiliser les services de rendering existants ; pas de nouvel engine de composition ad hoc
- Les styles doivent rester dans les CSS admin existantes ou dans un fichier CSS dedie
- Reutiliser si possible un schema partage `ResolvedAssemblyView`

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [backend/app/api/v1/routers/admin_llm_assembly.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm_assembly.py)
- [backend/app/llm_orchestration/services/assembly_resolver.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_resolver.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/services/context_quality_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/context_quality_injector.py)
- [backend/app/llm_orchestration/services/length_budget_injector.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/length_budget_injector.py)
- [backend/app/llm_orchestration/policies/hard_policy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/policies/hard_policy.py)
- [66-8-catalogue-administrable-composition-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md)
- [66-12-budgets-longueur-par-section.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-12-budgets-longueur-par-section.md)
- [66-13-durcissement-placeholders.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-13-durcissement-placeholders.md)
- [66-14-context-quality-strategie-redaction.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-14-context-quality-strategie-redaction.md)
- [66-17-source-verite-canonique-composition.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-17-source-verite-canonique-composition.md)
- [66-27-propagation-complete-context-quality-handled-by-template-observabilite.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-27-propagation-complete-context-quality-handled-by-template-observabilite.md)
- [66-45-vue-catalogue-canonique-prompts-actifs.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `.\.venv\Scripts\Activate.ps1 && cd backend && ruff format . && ruff check . && pytest -q tests/integration/test_admin_llm_catalog.py`
- `npm run test -- AdminPromptsPage.test.tsx` (depuis `frontend/`)

### Completion Notes List

- Story creee pour donner a l'admin une inspection fidele de l'assembly resolue, sans appel provider
- Le detail doit suivre l'ordre runtime reel et rendre visibles les couches separees du pipeline
- La story depend fonctionnellement du catalogue canonique 66.45 et prepare la timeline snapshot 66.47
- Endpoint detail implemente: `GET /v1/admin/llm/catalog/{manifest_entry_id}/resolved` avec projection structuree `composition_sources`, `transformation_pipeline`, `resolved_result`.
- La reponse detail applique la politique de redaction admin sur les valeurs affichees et expose l'etat de resolution des placeholders (`resolved`, `optional_missing`, `fallback_used`, `blocking_missing`, `unknown`).
- Ecran admin enrichi avec ouverture de detail depuis le catalogue et affichage des 3 zones fixes: Sources de composition, Pipeline de transformation, Resultat resolu.
- Tests ajoutes/etendus backend + frontend pour couvrir le detail resolved et son affichage.

### File List

- `_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`

### Change Log

- 2026-04-15: implementation completee de la vue detail `Resolved Prompt Assembly` (backend + frontend + tests) avec statut passe a `review`.
