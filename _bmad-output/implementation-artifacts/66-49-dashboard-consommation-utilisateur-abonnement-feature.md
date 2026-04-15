# Story 66.49: Dashboard consommation par utilisateur / abonnement / feature

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / produit / finance,
I want disposer d'un dashboard de consommation LLM par utilisateur, abonnement et feature,
so that je puisse piloter les coûts, repérer les dérives et descendre rapidement jusqu'aux appels LLM récents corrélés.

## Contexte

L'espace admin LLM a déjà été réaligné sur la vérité runtime pour le catalogue, les détails de composition et l'historisation release :

- [66-45-vue-catalogue-canonique-prompts-actifs.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md)
- [66-46-vue-detail-resolved-prompt-assembly.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md)
- [66-47-historisation-orientee-release-snapshot.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-47-historisation-orientee-release-snapshot.md)

En parallèle :

- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) expose encore un dashboard historique centré sur `use_case`.
- [backend/app/services/llm_ops_monitoring_service.py](/c:/dev/horoscope_front/backend/app/services/llm_ops_monitoring_service.py) apporte déjà un read model d'exploitation LLM par dimensions canoniques, utile pour réutiliser les patterns d'agrégation et d'alerte.
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py) contient déjà les signaux nécessaires pour corréler une ligne de consommation à un `llm_call_log`.
- la story 66.48 pose la base read model coût/tokens qui doit être consommée ici.

Le besoin de 66.49 est donc une **surface admin exploitable**, pas une nouvelle logique d'agrégation locale dans le frontend.

Contrat UX/API à figer dans cette story :

- la granularité d'affichage par défaut des vues `par utilisateur`, `par abonnement` et `par feature/subfeature` est **une ligne agrégée par période sélectionnée** ;
- le drill-down expose par défaut les **50 appels les plus récents**, triés par `timestamp` décroissant ;
- les clés minimales visibles dans le drill-down sont `request_id`, `timestamp`, `feature`, `subfeature`, `provider`, `active_snapshot_version` ou `manifest_entry_id` si disponible, `validation_status` ;
- le format d'export MVP imposé est **CSV**.

## Diagnostic exact à préserver

- Le dashboard de consommation doit être fondé sur la taxonomie canonique (`feature`, `subfeature`, `plan`, `locale`, `executed_provider`, `active_snapshot_version`) et non sur `use_case`.
- La granularité par défaut des vues est l'agrégat par période sélectionnée.
- La vue `par utilisateur` doit être utile au support et au pilotage produit, tout en évitant l'exposition de contenu sensible.
- La vue `par abonnement` doit refléter les plans commerciaux réellement utilisés par le runtime/billing.
- La vue `par feature/subfeature` doit rester cohérente avec les surfaces admin 66.45 à 66.47.
- Le drill-down doit pointer vers les appels récents corrélés aux `llm_call_logs`, pas vers une reconstruction opaque en frontend.
- Le drill-down par défaut est borné à 50 lignes, triées du plus récent au plus ancien.
- Le format d'export MVP est CSV.
- Aucun style inline ne doit être introduit ; réutiliser les patterns CSS/admin déjà présents.

## Acceptance Criteria

1. **AC1 — Vue par utilisateur** : une vue admin `par utilisateur` expose historique, `input_tokens`, `output_tokens`, `total_tokens`, coût estimé, latence et taux d'erreur pour chaque utilisateur, avec pagination serveur.
2. **AC2 — Export vue utilisateur** : la vue `par utilisateur` propose un export CSV gouverné des lignes visibles ou du périmètre filtré.
3. **AC3 — Vue par abonnement** : une vue `par abonnement` expose la ventilation au minimum par `free`, `basic`, `premium` ou équivalent canonique, avec volumes, tokens, coûts et erreurs.
4. **AC4 — Vue par feature/subfeature** : une vue `par feature/subfeature` expose les agrégats sur la taxonomie canonique runtime, sans axe nominal `use_case`.
5. **AC5 — Filtres temporels** : la surface supporte des filtres temporels explicites au minimum journaliers, mensuels et bornes custom.
6. **AC6 — Drill-down vers logs corrélés** : depuis une ligne agrégée, l'admin peut consulter les 50 appels les plus récents corrélés aux `llm_call_logs`, triés par `timestamp` décroissant.
7. **AC7 — Safe-by-design** : le drill-down n'expose pas de prompt, `raw_output`, `structured_output` complet ni contenu utilisateur sensible.
8. **AC8 — Cohérence avec 66.48** : toutes les vues lisent le modèle canonique de consommation défini en 66.48, sans réimplémentation concurrente.
9. **AC9 — Pagination / tri / recherche serveur** : les listes principales utilisent pagination, tri et recherche serveur, pas un filtrage limité à la page courante.
10. **AC10 — Export canonique** : les exports CSV reflètent la taxonomie canonique et les filtres actifs.
11. **AC11 — Granularité par défaut explicite** : chaque vue principale affiche par défaut des lignes agrégées par période sélectionnée, pas un mélange ambigu de granularités.
12. **AC12 — Non-régression admin** : l'ajout de cette surface ne casse pas les vues 66.45 à 66.47 ni le dashboard historique tant qu'il reste présent.
13. **AC13 — Responsive et sans inline style** : la page reste exploitable sur desktop/mobile via tableaux scrollables ou cartes dérivées, sans style inline.

## Tasks / Subtasks

- [ ] Task 1: Définir l'API admin de consommation (AC: 1 à 10)
  - [ ] Exposer un endpoint backend dédié du type `GET /v1/admin/llm/consumption` ou équivalent stable.
  - [ ] Prévoir des modes/vues `user`, `subscription`, `feature`.
  - [ ] Supporter filtres temporels, pagination, tri, recherche et export CSV.

- [ ] Task 2: Brancher l'API sur le modèle canonique 66.48 (AC: 1, 3, 4, 8, 10)
  - [ ] Réutiliser le service/query layer de consommation canonique.
  - [ ] Définir les DTO API des trois vues.
  - [ ] Rendre explicites les dimensions affichées et les mesures disponibles.

- [ ] Task 3: Ajouter le drill-down corrélé aux logs LLM (AC: 6, 7)
  - [ ] Définir la relation entre agrégat et appels récents (`request_id`, `trace_id`, `timestamp`, `manifest_entry_id`, `validation_status`, etc.).
  - [ ] Verrouiller le volume par défaut à 50 appels et l'ordre `timestamp desc`.
  - [ ] Réutiliser les surfaces de `llm_call_logs` existantes ou exposer une projection dédiée.
  - [ ] Garantir la non-fuite de contenu sensible.

- [ ] Task 4: Implémenter la surface frontend admin (AC: 1 à 13)
  - [ ] Ajouter une page ou un onglet dédié dans l'espace admin LLM.
  - [ ] Construire les trois vues `par utilisateur`, `par abonnement`, `par feature/subfeature`.
  - [ ] Ajouter filtres temporels, tri, pagination, export CSV et drill-down.
  - [ ] Afficher explicitement la granularité agrégée par période sélectionnée.
  - [ ] Réutiliser les composants/tokens/CSS admin existants.

- [ ] Task 5: Ajouter les tests backend/frontend (AC: 1 à 13)
  - [ ] Tests backend sur pagination, filtres, tri, export, drill-down.
  - [ ] Tests backend sur la borne à 50 lignes et l'ordre `timestamp desc` du drill-down.
  - [ ] Tests frontend sur les trois vues et la disparition de `use_case` comme axe primaire.
  - [ ] Tests frontend sur filtres temporels + pagination serveur.
  - [ ] Tests frontend sur la granularité par période affichée.
  - [ ] Tests de non-fuite et de cohérence des exports.

- [ ] Task 6: Validation locale et documentation
  - [ ] Documenter la nouvelle surface de pilotage consommation.
  - [ ] Exécuter les validations backend/frontend pertinentes.

## Dev Notes

### Ce que le dev doit retenir avant d'implémenter

- La story est d'abord une **surface admin de pilotage**, fondée sur le modèle canonique 66.48.
- Le backend doit rester responsable de l'agrégation, du tri, de la pagination et des exports.
- Les vues doivent parler le même langage que le runtime canonique et que le billing tokenisé.
- Le drill-down doit faciliter l'investigation ops/support sans fuite de données.

### Ce que le dev ne doit pas faire

- Ne pas recalculer les métriques d'agrégation dans le frontend.
- Ne pas remettre `use_case` comme colonne primaire "par commodité".
- Ne pas dériver les options de filtres uniquement de la page courante si pagination serveur.
- Ne pas construire une deuxième logique de corrélation différente de celle des `llm_call_logs`.
- Ne pas introduire de styles inline.

### Fichiers à inspecter en priorité

- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/services/llm_ops_monitoring_service.py](/c:/dev/horoscope_front/backend/app/services/llm_ops_monitoring_service.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [frontend/src/pages/admin/AdminPromptsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)
- [frontend/src/pages/admin/AdminPromptsPage.css](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css)
- [65-14-supervision-ia-tableau-bord-metier.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-14-supervision-ia-tableau-bord-metier.md)
- [66-45-vue-catalogue-canonique-prompts-actifs.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md)
- [66-47-historisation-orientee-release-snapshot.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-47-historisation-orientee-release-snapshot.md)
- [66-48-modele-canonique-comptage-consommation-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-48-modele-canonique-comptage-consommation-llm.md)

### Previous Story Intelligence

- **65.14** prouve l'existence du besoin dashboard admin LLM, mais sur un axe `use_case` désormais insuffisant.
- **66.37** fournit déjà les patterns de read model ops, alertes structurées et agrégats canoniques.
- **66.45 à 66.47** ont imposé l'alignement admin sur la vérité runtime canonique ; la consommation doit s'y conformer.
- **66.48** doit fournir le socle d'agrégation sur lequel 66.49 s'appuie.
- Le séquencement recommandé de delivery est `66.48 -> 66.50 -> 66.49`.

### Testing Requirements

- Ajouter un test backend pour la vue `par utilisateur`.
- Ajouter un test backend pour la vue `par abonnement`.
- Ajouter un test backend pour la vue `par feature/subfeature`.
- Ajouter un test backend d'export avec filtres temporels actifs.
- Ajouter un test backend de drill-down corrélé aux `llm_call_logs`.
- Ajouter un test backend sur la borne à 50 lignes et l'ordre `timestamp desc` du drill-down.
- Ajouter un test frontend montrant que `use_case` n'est plus l'axe primaire.
- Ajouter un test frontend sur filtres temporels + pagination serveur.
- Ajouter un test frontend sur la granularité par période affichée.
- Vérifier l'absence de contenu sensible dans les réponses d'API et dans le drill-down.
- Commandes obligatoires si code backend modifié, après activation venv :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`

### Project Structure Notes

- Story backend + frontend admin.
- Réutiliser les patterns API/admin déjà présents autour de `/admin/prompts` et du monitoring LLM.
- Si la page vit dans `/admin/prompts`, garder une navigation explicite et non ambiguë avec les vues 66.45 à 66.47.
- Si un nouvel écran est créé, rester dans le domaine admin LLM et la même langue visuelle.

### References

- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/services/llm_ops_monitoring_service.py](/c:/dev/horoscope_front/backend/app/services/llm_ops_monitoring_service.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [65-14-supervision-ia-tableau-bord-metier.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-14-supervision-ia-tableau-bord-metier.md)
- [66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md)
- [66-45-vue-catalogue-canonique-prompts-actifs.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md)
- [66-47-historisation-orientee-release-snapshot.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-47-historisation-orientee-release-snapshot.md)
- [66-48-modele-canonique-comptage-consommation-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-48-modele-canonique-comptage-consommation-llm.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story créée pour la surface admin de pilotage consommation LLM, dépendante du modèle canonique 66.48.

### File List

- `_bmad-output/implementation-artifacts/66-49-dashboard-consommation-utilisateur-abonnement-feature.md`
