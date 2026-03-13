# Epic 46: Recentrer les consultations sur une guidance astrologique ciblée sans tirage

Status: draft-for-story-splitting

## Contexte

Le parcours `/consultations` a été conçu à l'origine comme une hybridation entre:

- des consultations astrologiques ciblées (`dating`, `pro`, `event`, `free`)
- un choix d'astrologue ou de persona
- une option de tirage (`none`, `tarot`, `runes`)

Cette construction sort désormais du périmètre produit visé. Le besoin confirmé est de:

- conserver les demandes ciblées de type rendez-vous amoureux, choix professionnel, événement important ou question libre
- supprimer toute notion de tirage de cartes ou de runes de l'application
- conserver une expérience cohérente avec la promesse coeur du produit: guidance astrologique contextualisée

Le risque principal n'est pas visuel mais fonctionnel: aujourd'hui la page résultat des consultations utilise deux branches incompatibles avec le périmètre cible:

- branche `tarot/runes` via `useExecuteModule()`
- branche `none` qui retombe sur l'interprétation du thème natal, ce qui ne correspond pas à une demande contextuelle ciblée

Epic 46 doit donc supprimer le tirage sans casser:

- la route `/consultations`
- le wizard et l'historique local
- l'ouverture dans le chat
- la cohérence i18n FR/EN/ES
- les seeds/contrats LLM et les tests existants

## Objectif Produit

Transformer `/consultations` en un parcours de guidance astrologique ciblée qui:

1. conserve les types de demandes `dating`, `pro`, `event`, `free`
2. supprime toute notion de tirage, cartes, runes ou spread
3. s'appuie sur la guidance contextuelle existante plutôt que sur un module tarot
4. garde la route `/consultations` et les deep links existants
5. préserve l'historique utile et l'ouverture dans le chat
6. réaligne navigation, dashboard, backend et artefacts BMAD sur ce nouveau périmètre

## Non-objectifs

- ne pas changer la stack ou le shell de navigation global
- ne pas renommer la route `/consultations`
- ne pas réinventer un nouveau moteur de guidance alors que `/v1/guidance/contextual` existe déjà
- ne pas supprimer le backend tarot/runes avant que le frontend n'ait cessé de l'utiliser
- ne pas casser l'historique local existant ni les liens déjà partagés

## Diagnostic Technique

### Frontend

Le frontend de consultations dépend directement de la sémantique de tirage:

- `frontend/src/types/consultation.ts`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/i18n/consultations.ts`

Les points de dérive produit les plus visibles sont:

- `WIZARD_STEPS = ["type", "astrologer", "drawing", "validation"]`
- `DrawingOption = "none" | "tarot" | "runes"`
- rendu conditionnel de `currentResult.drawing`
- wording `step_drawing`, `select_drawing`, `drawing_tarot`, `drawing_runes`

### Navigation et dashboard

Le parcours `/consultations` est encore promu comme un espace de tirage:

- `frontend/src/ui/nav.ts`
- `frontend/src/components/ShortcutsSection.tsx`
- `frontend/src/i18n/dashboard.tsx`

### Backend

Le backend expose encore un sous-système tarot/runes autonome:

- `frontend/src/api/chat.ts` consomme `/v1/chat/modules/*`
- `backend/app/services/feature_flag_service.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/schemas.py`
- `backend/app/llm_orchestration/policies/hard_policy.py`
- `backend/app/llm_orchestration/seeds/use_cases_seed.py`
- `backend/app/ai_engine/prompts/card_reading_v1.jinja2`

### Backend déjà réutilisable

La bonne fondation métier existe déjà et doit être réemployée:

- `backend/app/api/v1/routers/guidance.py`
- `backend/app/services/guidance_service.py`

## Principe de refonte

- conserver la route `/consultations`
- faire du backend `guidance_contextual` la source de vérité
- transformer le wizard en parcours `type -> astrologue -> demande`
- migrer l'historique local au lieu de le casser
- supprimer tarot/runes en deux temps: d'abord front, ensuite backend profond

## Découpage en chapitres

### Chapitre 1 — Fondations de génération

- 46.1 Rebrancher les consultations ciblées sur la guidance contextuelle

### Chapitre 2 — Refactor UI et modèle

- 46.2 Refondre le wizard et le modèle de données des consultations sans tirage
- 46.3 Migrer l'historique local et préserver l'ouverture dans le chat

### Chapitre 3 — Sémantique produit visible

- 46.4 Revoir navigation, dashboard et wording i18n des consultations

### Chapitre 4 — Nettoyage technique profond

- 46.5 Retirer le sous-système tarot/runes du backend et des contrats LLM

### Chapitre 5 — Verrouillage final

- 46.6 Verrouiller QA, cohérence BMAD et non-régression de la refonte

## Risques et mitigations

### Risque 1: suppression visuelle sans rebranchement métier

Mitigation:

- traiter 46.1 avant la suppression backend
- ajouter des tests de bout de chaîne sur `dating`, `pro`, `event`, `free`

### Risque 2: perte de l'historique local

Mitigation:

- lecture backward-compatible
- migration de normalisation à la lecture
- écriture uniquement du schéma v2

### Risque 3: incohérence sémantique entre menu, dashboard et page consultations

Mitigation:

- story dédiée sur navigation et i18n
- suppression explicite des clés et handlers nommés `tirage`

### Risque 4: casse backend tardive

Mitigation:

- story dédiée de retrait backend
- couverture tests et recherche `rg` ciblée sur `tarot`, `runes`, `tirage`, `cards`, `spread`

## Ordre d'implémentation recommandé

### Lot 1 — Rebranchement fonctionnel

- 46.1

### Lot 2 — Refactor parcours et donnée

- 46.2
- 46.3

### Lot 3 — Nettoyage produit visible

- 46.4

### Lot 4 — Retrait backend profond

- 46.5

### Lot 5 — Verrouillage final

- 46.6

## Références

- [Source: _bmad-output/implementation-artifacts/16-5-consultations-pages.md]
- [Source: _bmad-output/implementation-artifacts/11-2-modules-tarot-runes-derriere-feature-flags.md]
- [Source: _bmad-output/implementation-artifacts/17-1-fondations-ui-tokens-typo-lucide.md]
- [Source: _bmad-output/implementation-artifacts/17-5-raccourcis-shortcut-card.md]
- [Source: _bmad-output/implementation-artifacts/45-1-refondre-le-routing-dashboard-et-isoler-la-page-horoscope-detaillee.md]
- [Source: _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]
- [Source: frontend/src/pages/ConsultationResultPage.tsx]
- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/types/consultation.ts]
- [Source: frontend/src/i18n/consultations.ts]
- [Source: frontend/src/ui/nav.ts]
- [Source: frontend/src/components/ShortcutsSection.tsx]
- [Source: frontend/src/i18n/dashboard.tsx]
- [Source: backend/app/api/v1/routers/guidance.py]
- [Source: backend/app/services/guidance_service.py]
- [Source: backend/app/services/feature_flag_service.py]
- [Source: backend/app/llm_orchestration/gateway.py]
- [Source: backend/app/llm_orchestration/schemas.py]
- [Source: backend/app/llm_orchestration/policies/hard_policy.py]
- [Source: backend/app/llm_orchestration/seeds/use_cases_seed.py]
