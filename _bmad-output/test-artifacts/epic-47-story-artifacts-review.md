# Epic 47 Story Artifacts Review

Date: 2026-03-13
Statut: validé pour lancement en `ready-for-dev`

## Objectif de la revue

Vérifier que les artefacts story 47.x:

- sont alignés avec `docs/backlog_epics_consultation_complete.md`
- respectent l'état réel du code actuel autour de `/consultations`
- n'impliquent pas de régression sur les fonctionnalités hors consultations
- restent compatibles avec la méthode BMAD et les workflows `create-story` / `dev-story`

## Résultat global

Les stories 47.1 à 47.7 sont cohérentes avec le backlog de référence et avec l'architecture actuelle.

Elles respectent les garde-fous suivants:

- la route `/consultations` reste stable
- les deep links `/consultations/new` et `/consultations/result` restent stables
- l'historique local et l'ouverture dans le chat sont préservés comme invariants
- la logique métier nouvelle est déplacée vers des contrats consultation dédiés, sans refonte transverse du chat, du profil ou du natal
- le scope des futures implémentations reste limité au code consultations et à ses tests associés
- les safeguards sensibles sont désormais explicités comme matrice consultation `fallback / refusal / reframing`
- la gouvernance MVP des données tiers est explicitée sans persistance backend implicite
- le wording de fallback est traité comme un contrat i18n testable, pas comme une simple copie UI
- les enums partagées et exemples JSON canoniques sont désormais figés avant lancement dev

## Vérification story par story

### 47.1 Catalogue et taxonomie

Alignement backlog:

- couvre EPIC-CC-01 et la partie catalogue visible d'EPIC-CC-09
- réintroduit une taxonomie consultation complète adaptée au MVP

Alignement code:

- s'appuie sur `frontend/src/types/consultation.ts` et `frontend/src/i18n/consultations.ts`
- préserve la lecture des types legacy gérés par `consultationStore`

Risque de régression: faible

- aucun changement requis hors module consultations

### 47.2 Précheck consultation

Alignement backlog:

- couvre EPIC-CC-02
- formalise `user_profile_quality`, `precision_level`, `available_modes`
- fige les enums partagées et un exemple canonique de contrat `/precheck`

Alignement code:

- réutilise `UserBirthProfileService`, `UserAstroProfileService` et `/v1/users/me/birth-data`
- évite de dupliquer les règles côté frontend

Risque de régression: maîtrisé

- nouveau routeur consultation dédié, sans modification fonctionnelle des routes existantes `users` ou `guidance`

### 47.3 Wizard et collecte conditionnelle

Alignement backlog:

- couvre EPIC-CC-03 et la partie parcours d'EPIC-CC-09

Alignement code:

- corrige une dette réelle du flow actuel: étape `astrologer` bloquante alors qu'elle n'est pas consommée par la génération
- reste bornée au module consultations
- borne explicitement les données tiers au draft / run courant sans créer une persistance backend cachée

Risque de régression: moyen mais cadré

- le store et les tests consultations existants sont explicitement mentionnés comme garde-fous

### 47.4 Fallbacks et modes dégradés

Alignement backlog:

- couvre EPIC-CC-04
- formalise `nominal / degraded / blocked`

Alignement code:

- s'appuie sur la base existante de `GuidanceService` sans faire croire qu'elle suffit déjà côté produit
- propage `fallback_mode` jusqu'au runtime consultations
- rend explicite la matrice de safeguards consultation au lieu de la laisser implicite dans les prompts ou politiques techniques

Risque de régression: moyen mais nécessaire

- les messages et métadonnées sont explicitement confinés au parcours consultations

### 47.5 Dossier consultation et routing LLM

Alignement backlog:

- couvre EPIC-CC-05 et EPIC-CC-06
- introduit le pivot `ConsultationDossier`
- fige la liste exacte des `route_key` MVP et un exemple canonique de contrat `/generate`

Alignement code:

- réutilise `GuidanceService`, `AIEngineAdapter`, `llm_orchestration`
- n'impose pas une refonte du pipeline chat/natal
- ajoute une matrice MVP de résolution `route_key` exploitable par les prompts, les tests et l'observabilité

Risque de régression: maîtrisé

- la story force le réemploi de la pile LLM existante au lieu d'un second pipeline

### 47.6 Génération et restitution structurée

Alignement backlog:

- couvre EPIC-CC-07 et la restitution visible d'EPIC-CC-09

Alignement code:

- s'appuie sur `ConsultationResultPage`, `consultationStore` et l'historique local existant
- garde le localStorage comme persistance MVP pour ne pas ouvrir un chantier DB hors scope
- verrouille le wording contractuel par fallback et limite la persistance locale des données tiers

Risque de régression: moyen mais cadré

- la compatibilité 46.x et legacy est un critère d'acceptation explicite

### 47.7 QA, observabilité et gate final

Alignement backlog:

- couvre EPIC-CC-10
- prolonge la discipline de clôture déjà utilisée en epic 46

Alignement code:

- réutilise les patterns de tests consultations et les briques d'observabilité existantes
- n'élargit pas le scope au monitoring global de l'application
- tranche explicitement la politique snapshots UI: obligatoires sur les fallback wording critiques, pas sur toute l'UI

Risque de régression: faible

- story de verrouillage, pas de refonte fonctionnelle

## Points d'attention conservés dans les artefacts

1. Le choix d'astrologue est explicitement traité comme une dette du flow actuel, pas comme une vérité métier consultation complète.
2. La persistance DB des consultations n'est pas imposée en epic 47 afin d'éviter un chantier transverse non demandé.
3. Les anciens types `dating/pro/event/free` restent lisibles en historique pour ne pas casser les deep links et le localStorage.
4. Le précheck et les fallbacks sont backend-driven pour éviter la duplication de règles dans le frontend.
5. Le réemploi de `guidance_contextual` est encadré comme brique interne, pas comme contrat produit final.
6. Les safeguards sensibles sont explicitement résolus en `fallback`, `refusal` ou `reframing`.
7. Les données tiers brutes restent bornées au draft / run et ne deviennent pas une persistance backend implicite.
8. Le wording affiché à l'utilisateur est contractualisé par `fallback_mode`, notamment pour `relation` et `timing`.
9. Les enums partagées consultation et les exemples JSON `/precheck` et `/generate` sont suffisamment figés pour éviter une dérive d'implémentation.

## Limites et arbitrages encore ouverts

- Le niveau exact de granularité du type `timing` reste à cadrer finement pendant l'implémentation.
- Le stockage éventuel des profils tiers reste volontairement borné au périmètre consultations tant qu'un choix de persistance n'est pas tranché.
- La place future d'un choix d'astrologue réellement routé côté backend n'est pas incluse dans l'epic 47.
- La matrice MVP exacte des `route_key` au-delà des cas explicitement listés reste à étendre après implémentation initiale.

## Ordre d'implémentation recommandé

Chemin critique retenu:

- 47.1 -> 47.2 -> 47.5 -> 47.3 -> 47.4 -> 47.6 -> 47.7

Justification:

- 47.2 et 47.5 figent d'abord les contrats backend et d'orchestration.
- 47.3, 47.4 et 47.6 peuvent ensuite consommer ces contrats sans double refactor frontend.

## Conclusion

Les artefacts sont prêts pour un enchaînement BMAD `dev-story`.

Ils sont:

- suffisamment précis pour guider l'implémentation
- suffisamment bornés pour éviter les régressions hors consultation
- suffisamment alignés avec le backlog de référence pour matérialiser une vraie "consultation complète" sur `/consultations`
