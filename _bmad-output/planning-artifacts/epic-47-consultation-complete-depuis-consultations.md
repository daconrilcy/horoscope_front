# Epic 47: Faire évoluer `/consultations` vers une consultation complète pilotée par précheck, fallback et orchestration métier

Status: split-into-stories

## Contexte

L'epic 46 a recentré `/consultations` sur une guidance astrologique ciblée sans tirage, avec:

- une route stable `/consultations`
- un wizard frontend léger
- une génération branchée sur `POST /v1/guidance/contextual`
- une persistance locale de l'historique
- une réouverture dans le chat

Ce socle reste cependant très en dessous du backlog de référence `docs/backlog_epics_consultation_complete.md`. Le produit actuel ne couvre pas encore:

- la taxonomie MVP de consultation complète
- le précheck de complétude et de précision
- les parcours dégradés explicites
- la collecte conditionnelle des données manquantes
- les consultations relationnelles avec tiers
- un dossier de consultation et un contrat backend dédiés
- le routing LLM versionné par consultation / fallback
- l'observabilité métier complète du parcours

L'epic 47 doit faire converger `/consultations` vers cette nouvelle mouture sans casser:

- la route `/consultations`
- les deep links `/consultations/new` et `/consultations/result`
- l'historique local existant
- l'ouverture dans le chat
- les flows non consultations (`/chat`, `/natal`, `/profile`, `/dashboard`)

## Objectif Produit

Transformer `/consultations` en point d'entrée d'une consultation complète MVP qui:

1. réutilise les données natales déjà présentes dans l'application
2. expose le niveau réel de précision avant génération
3. demande uniquement les compléments nécessaires
4. supporte les parcours mono-profil, relationnels et timing dégradé
5. rend explicites les fallbacks et les limitations
6. délègue la génération à un contrat backend consultation dédié, au lieu d'orchestrer la logique métier côté frontend

## Non-objectifs

- ne pas renommer `/consultations`
- ne pas réécrire le chat, la page profil ou la page thème natal
- ne pas introduire un nouveau moteur astro parallèle à l'existant
- ne pas casser la lecture des historiques legacy `dating/pro/event/free`
- ne pas imposer une persistance DB des consultations tant que le localStorage reste suffisant pour le périmètre consultations
- ne pas disperser la logique de précheck ou de fallback dans plusieurs couches frontend

## Diagnostic Technique

### Frontend actuel

Le module consultations repose aujourd'hui sur:

- `frontend/src/types/consultation.ts`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/pages/ConsultationsPage.tsx`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/features/consultations/components/*`
- `frontend/src/api/guidance.ts`

Forces actuelles:

- route stable et tests déjà en place
- normalisation legacy du localStorage
- réouverture dans le chat stabilisée
- séparation raisonnable entre store, pages et client API

Limites actuelles:

- taxonomie `dating/pro/event/free` non alignée avec le backlog consultation complète
- étape `astrologer` bloquante alors que la génération réelle repose sur `guidance_contextual` et non sur ce choix
- absence de précheck explicite avant génération
- absence de `precision_level`, `fallback_mode`, `available_modes`
- aucune collecte conditionnelle tiers / relation
- page résultat encore couplée à un payload guidance générique, pas à un contrat consultation

### Backend actuel

Le backend réutilisable existe déjà partiellement:

- `backend/app/api/v1/routers/users.py`
- `backend/app/services/user_birth_profile_service.py`
- `backend/app/services/user_astro_profile_service.py`
- `backend/app/api/v1/routers/guidance.py`
- `backend/app/services/guidance_service.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/app/llm_orchestration/seeds/use_cases_seed.py`

Forces actuelles:

- les données natales utilisateur sont accessibles via `/v1/users/me/birth-data`
- `astro_profile.missing_birth_time` existe déjà
- la guidance contextuelle et l'orchestration LLM V2 existent
- les formats API et enveloppes d'erreur sont standardisés

Limites actuelles:

- aucun endpoint consultation dédié
- aucune modélisation `ConsultationDossier`
- aucune matrice de `fallback_mode` ou `route_key`
- aucun contrat stable pour résultat consultation complet
- observabilité guidance existante mais pas encore consultation-centric

## Principe de mise en oeuvre

- garder `/consultations` comme hub fonctionnel unique
- introduire d'abord la taxonomie et le précheck avant de refaire profondément le wizard
- garder la compatibilité legacy en lecture pour l'historique
- déplacer la logique métier de consultation vers un contrat backend dédié
- conserver `guidance_contextual` comme brique interne réutilisable, pas comme API produit finale de la feature
- traiter explicitement les modes dégradés avant la restitution finale
- formaliser les safeguards sensibles consultation et leur issue `fallback / refusal / reframing`
- encadrer la gouvernance des données tiers en MVP sans introduire de persistance backend implicite

## Découpage en stories

### Chapitre 1 - Référentiel et éligibilité

- 47.1 Redéfinir le catalogue produit et la taxonomie des consultations complètes
- 47.2 Exposer le précheck de complétude et de précision des consultations

### Chapitre 2 - Contrat backend et orchestration

- 47.5 Construire le dossier de consultation et le routing LLM versionné

### Chapitre 3 - Parcours de collecte, fallbacks et restitution

- 47.3 Refondre le wizard consultations avec cadrage et collecte conditionnelle
- 47.8 Etendre la collecte tiers aux consultations d'interaction ciblee
- 47.9 Persister et reutiliser les profils tiers de consultation
- 47.4 Implémenter les modes dégradés et fallbacks des consultations
- 47.6 Refondre la génération et la restitution structurée des consultations

### Chapitre 4 - Verrouillage final

- 47.7 Verrouiller QA, observabilité et non-régression des consultations complètes

## Risques et mitigations

### Risque 1: casser l'historique et les deep links existants

Mitigation:

- garder la normalisation legacy dans `consultationStore`
- traiter les anciens types en lecture seule
- vérifier `?id=...` sur schémas 46 et 47

### Risque 2: dupliquer la logique de complétude entre frontend et backend

Mitigation:

- centraliser le calcul dans un service/backend consultation dédié
- limiter le frontend à l'affichage et à la collecte

### Risque 3: introduire une UX trop ambitieuse par rapport au code actuel

Mitigation:

- phaser le chantier: taxonomie -> précheck -> collecte -> fallback -> génération -> résultat
- réutiliser les API existantes (`birth-data`, `guidance`, `geocoding`) là où c'est déjà stable

### Risque 4: coupler trop tôt la feature au choix d'astrologue

Mitigation:

- conserver `astrologerId` comme métadonnée UI / chat tant qu'aucun routage backend par persona n'est réellement implémenté
- ne pas en faire un prérequis métier de génération consultation

### Risque 5: toucher des zones hors scope utilisateur

Mitigation:

- limiter les futures implémentations au code consultations et aux tests associés
- s'appuyer sur les routes et services existants sans refactor transverse hors feature

### Risque 6: laisser implicites les safeguards sensibles et la gouvernance des données tiers

Mitigation:

- formaliser une matrice consultation des issues `fallback / refusal / reframing`
- documenter noir sur blanc que les données tiers brutes ne sont pas persistées côté backend dans l'epic 47
- verrouiller le wording contractuel par `fallback_mode` dans le module i18n consultations

### Risque 7: limiter à tort la collecte tiers au seul type `relation`

Mitigation:

- expliciter les consultations d'interaction ciblee au-dela de `relation`
- introduire un critere metier pour l'affichage du module tiers
- couvrir le cas `work` par une story dediee et des tests wizard explicites

### Risque 8: laisser les profils tiers en simple saisie jetable, sans reutilisation ni gouvernance explicite

Mitigation:

- introduire une persistance opt-in des profils tiers avec pseudonyme non identifiant
- documenter clairement qu'un tiers peut etre enregistre a la demande pendant la consultation, pas automatiquement
- ajouter une reutilisation depuis les parcours eligibles pour eviter la ressaisie
- stocker un journal minimal des consultations ayant utilise ce tiers, sans refonte transverse de la persistance globale des consultations

## Ordre recommandé d'implémentation

### Lot 1 - Référentiel et précheck

- 47.1
- 47.2

### Lot 2 - Backend de consultation complet

- 47.5

### Lot 3 - UX conditionnelle et fallbacks

- 47.3
- 47.8
- 47.9
- 47.4
- 47.6

### Lot 4 - Gate final

- 47.7

Chemin critique recommandé:

- 47.1 -> 47.2 -> 47.5 -> 47.3 -> 47.8 -> 47.4 -> 47.6 -> 47.7
- 47.1 -> 47.2 -> 47.5 -> 47.3 -> 47.8 -> 47.9 -> 47.4 -> 47.6 -> 47.7

## Références

- [Source: docs/backlog_epics_consultation_complete.md]
- [Source: _bmad-output/planning-artifacts/epic-46-consultations-astrologiques-sans-tirage.md]
- [Source: _bmad-output/implementation-artifacts/46-1-rebrancher-les-consultations-ciblees-sur-la-guidance-contextuelle.md]
- [Source: _bmad-output/implementation-artifacts/46-2-refondre-le-wizard-et-le-modele-de-donnees-des-consultations-sans-tirage.md]
- [Source: _bmad-output/implementation-artifacts/46-3-migrer-l-historique-local-et-preserver-l-ouverture-dans-le-chat.md]
- [Source: _bmad-output/implementation-artifacts/46-6-verrouiller-qa-coherence-bmad-et-non-regression-de-la-refonte.md]
- [Source: frontend/src/types/consultation.ts]
- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/pages/ConsultationsPage.tsx]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]
- [Source: frontend/src/pages/ConsultationResultPage.tsx]
- [Source: frontend/src/api/guidance.ts]
- [Source: frontend/src/api/birthProfile.ts]
- [Source: backend/app/api/v1/routers/users.py]
- [Source: backend/app/api/v1/routers/guidance.py]
- [Source: backend/app/services/user_birth_profile_service.py]
- [Source: backend/app/services/user_astro_profile_service.py]
- [Source: backend/app/services/guidance_service.py]
- [Source: backend/app/services/ai_engine_adapter.py]
