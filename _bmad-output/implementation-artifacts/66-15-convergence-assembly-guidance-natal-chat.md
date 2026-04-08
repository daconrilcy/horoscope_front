# Story 66.15 : Faire converger guidance/natal/chat vers une gouvernance assembly complète

Status: ready-for-dev

## Story

En tant qu'**architecte plateforme**,
je veux **migrer les familles guidance, natal et chat vers une gouvernance assembly complète (feature/subfeature/plan/astrologue/execution_profile)** et dans un second temps horoscope_daily/daily_prediction/support,
afin de **supprimer les chemins use_case-first redondants pour ces familles et d'atteindre une architecture unifiée autour du chemin assembly**.

## Prérequis d'implémentation

> **Cette story est une story d'intégration.** Elle dépend des fondations posées par les stories suivantes et ne doit pas partir avant qu'elles soient au minimum en cours de stabilisation :
> - **66.9** (doctrine abonnement — plan_rules vs use_case distinct)
> - **66.10** (bornes stylistiques persona)
> - **66.11** (ExecutionProfile avec profils internes stables)
> - **66.12** (LengthBudget dans PromptAssemblyConfig)
> - **66.13** (placeholders required/optional/fallback)
> - **66.14** (context_quality actif dans le renderer)
> - **66.18** (encapsulation des options provider derrière des profils internes stables, y compris l'injection `verbosity_profile` et la priorité `max_output_tokens`)
>
> Le statut `ready-for-dev` indique que la story est spécifiée et prête à être développée, **pas qu'elle peut partir immédiatement**. Elle est positionnée après 66.18 dans la séquence finale.

## Intent

Le document d'architecture identifie un système hybride : certaines familles sont partiellement assemblées, d'autres restent majoritairement use_case-first. Cette story vise à faire converger les familles les plus matures (guidance, natal, chat) vers une gouvernance assembly complète, puis à planifier la convergence des familles secondaires.

**Périmètre Phase 1 (scope de cette story) :** guidance, natal, chat.
**Périmètre Phase 2 (prévu mais hors scope) :** horoscope_daily, daily_prediction, support.

**Gouvernance assembly complète = :**
- `PromptAssemblyConfig` active pour chaque combinaison `feature/subfeature/plan` utilisée en production
- `ExecutionProfile` associé (story 66.11)
- `LengthBudget` défini si applicable (story 66.12)
- Chemin use_case-first désactivé ou en mode fallback-only pour ces familles
- `context_quality` traité comme paramètre actif (story 66.14)

## Décisions d'architecture

**D1 — La migration est additive, pas soustractive dans un premier temps.** On crée les `PromptAssemblyConfig` pour chaque combinaison feature/subfeature/plan, on valide la sortie, puis on désactive le chemin use_case-first en passant le use_case en `deprecated` (story 66.9).

**D2 — L'ordre de migration par sous-famille :**
1. `natal` (le plus mature, déjà migration story 66.7) — compléter avec plan et execution_profile
2. `guidance` (guidance_daily, guidance_weekly, guidance_contextual, event_guidance)
3. `chat` (chat_astrologer avec support historique conversationnel)

**D3 — Le chemin use_case-first devient un fallback** : il reste actif pour les familles non encore migrées et comme filet de sécurité pour les familles migrées pendant une période de transition.

**D4 — Le service appelant (`AIEngineAdapter` ou équivalent)** est modifié pour passer `feature/subfeature/plan` dans `ExecutionUserInput` au lieu d'un simple `use_case`, pour les familles migrées.

**D5 — La migration de `support` et `horoscope_daily` est planifiée dans le backlog mais hors scope de cette story.** Une section "Plan Phase 2" dans le PR suffira.

## Acceptance Criteria

1. **Given** que la famille `natal` est en gouvernance assembly complète
   **When** le service natal appelle le gateway avec `feature="natal", subfeature="natal_interpretation", plan="premium"`
   **Then** la résolution passe exclusivement par `AssemblyRegistry` → `ExecutionProfileRegistry`, aucun appel à `PromptRegistryV2.get_active_prompt()` n'est effectué pour cette combinaison

2. **Given** que la famille `guidance` est en gouvernance assembly complète
   **When** le service guidance appelle avec `feature="guidance", subfeature="daily", plan="free"`
   **Then** la résolution utilise le `PromptAssemblyConfig` correspondant, avec les `plan_rules` free appropriées

3. **Given** que la famille `chat` est en gouvernance assembly complète
   **When** `AIEngineAdapter.generate_chat_reply()` construit l'`ExecutionUserInput`
   **Then** il passe `feature="chat", subfeature="astrologer"` dans les métadonnées — le chemin assembly est activé

4. **Given** que le chemin assembly est activé pour une famille migrée
   **When** aucun `PromptAssemblyConfig` publié n'existe pour la combinaison demandée
   **Then** le gateway revient sur le chemin use_case-first existant (fallback de sécurité) avec un log `assembly_fallback: use_case_used`

5. **Given** que la migration est complète pour les 3 familles
   **When** la suite de tests d'intégration est exécutée
   **Then** 100% des tests existants pour natal, guidance et chat passent — aucune régression fonctionnelle

6. **Given** que la famille `horoscope_daily` est hors scope de cette story
   **When** le gateway reçoit un appel `use_case=horoscope_daily_full`
   **Then** il continue de passer par le chemin use_case-first sans changement — la migration Phase 2 est documentée dans le PR mais non implémentée

7. **Given** qu'une `PromptAssemblyConfig` est créée pour chaque combinaison feature/subfeature/plan en production
   **When** l'admin consulte la liste des configurations assembly
   **Then** il voit au minimum les combinaisons : `natal/natal_interpretation/free`, `natal/natal_interpretation/premium`, `natal/natal_short/free`, `guidance/daily/free`, `guidance/daily/premium`, `guidance/weekly/free`, `guidance_contextual/contextual/premium`, `chat/astrologer/free`, `chat/astrologer/premium`

## Tasks / Subtasks

- [ ] Inventaire complet des combinaisons feature/subfeature/plan en production (AC: 7)
  - [ ] Analyser `backend/app/prompts/catalog.py` pour lister tous les use_cases des familles natal, guidance, chat
  - [ ] Mapper use_case → feature/subfeature/plan selon la doctrine story 66.9
  - [ ] Documenter le mapping dans un tableau dans le PR

- [ ] Créer les `PromptAssemblyConfig` pour la famille `natal` (AC: 1, 7)
  - [ ] Pour chaque combinaison natal identifiée : créer via script ou migration la `PromptAssemblyConfig` en DB avec :
    - `feature_template_ref` → référence vers le `LlmPromptVersionModel` existant du use_case correspondant
    - `plan_rules_ref` si applicable
    - `execution_profile_ref` (après story 66.11 — sinon `None` avec fallback `resolve_model()`)
  - [ ] Valider la sortie générée vs l'ancienne sortie use_case (tests de non-régression)

- [ ] Créer les `PromptAssemblyConfig` pour la famille `guidance` (AC: 2, 7)
  - [ ] Même démarche que natal pour guidance_daily, guidance_weekly, guidance_contextual, event_guidance
  - [ ] S'assurer que `situation` et `last_user_msg` sont dans l'allowlist avec classification correcte (story 66.13)

- [ ] Modifier `AIEngineAdapter` pour passer `feature/subfeature` dans la famille `chat` (AC: 3)
  - [ ] Dans `backend/app/services/ai_engine_adapter.py` (ou équivalent) : ajouter `feature="chat", subfeature="astrologer"` dans `ExecutionUserInput` pour `generate_chat_reply()`
  - [ ] Créer la `PromptAssemblyConfig` pour chat/astrologer/free et chat/astrologer/premium

- [ ] Activer le fallback assembly→use_case dans le gateway (AC: 4)
  - [ ] Dans `gateway._resolve_plan()` : si résolution assembly échoue (aucune config trouvée), tenter use_case-first avec log `assembly_fallback: use_case_used`
  - [ ] Ce mécanisme est déjà partiellement en place (story 66.8) — vérifier et consolider

- [ ] Marquer les use_cases migrés en deprecated (AC: 5)
  - [ ] Après validation des configs assembly pour chaque famille, appliquer le mécanisme deprecated de la story 66.9 sur les use_cases correspondants

- [ ] Documenter le plan Phase 2 (AC: 6)
  - [ ] Ajouter dans `docs/llm-prompt-generation-by-feature.md` une section "Migration assembly — plan Phase 2" pour horoscope_daily, daily_prediction, support avec les critères de priorité et les bloqueurs identifiés

- [ ] Tests de non-régression (AC: 5)
  - [ ] Vérifier que tous les tests d'intégration existants pour natal, guidance, chat passent après migration
  - [ ] Ajouter des tests comparant la sortie assembly vs use_case sur fixtures partagées

## Dev Notes

- **Fichiers principaux à toucher :**
  - `backend/app/services/ai_engine_adapter.py` — ajout feature/subfeature dans ExecutionUserInput pour chat
  - `backend/app/llm_orchestration/gateway.py` — consolidation fallback assembly→use_case
  - Scripts de migration DB pour créer les `PromptAssemblyConfig` (ou migration Alembic data)
  - `docs/llm-prompt-generation-by-feature.md` — mise à jour état de gouvernance

- **Dépendances de stories :** Cette story bénéficie des fondations posées par 66.8 (PromptAssemblyConfig), 66.9 (doctrine abonnement), 66.11 (ExecutionProfile), 66.12 (LengthBudget), 66.13 (placeholders), 66.14 (context_quality) et 66.18 (encapsulation provider / `verbosity_profile`). Elle peut être préparée en parallèle, mais elle n'est pleinement cohérente qu'après stabilisation de ces stories.

- **Non-régression critique :** Les features natal, guidance et chat sont des features core. Le fallback assembly→use_case (AC: 4) est **obligatoire** comme filet de sécurité pendant la transition.

### References

- [Source: docs/llm-prompt-generation-by-feature.md#Source de vérité par famille de features]
- [Source: backend/app/services/ai_engine_adapter.py]
- [Source: backend/app/llm_orchestration/gateway.py]
- [Source: _bmad-output/implementation-artifacts/66-7-migration-natal-contrats-canoniques.md]
- [Source: _bmad-output/implementation-artifacts/66-8-catalogue-administrable-composition-llm.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
