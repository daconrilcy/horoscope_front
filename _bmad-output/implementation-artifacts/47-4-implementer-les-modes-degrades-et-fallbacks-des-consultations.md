# Story 47.4: Implémenter les modes dégradés et fallbacks des consultations

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a consultation domain engineer,
I want rendre explicites les modes dégradés et les sorties bloquantes du parcours consultations,
so that le produit reste honnête sur son niveau de précision et utile même quand les données disponibles sont incomplètes.

## Acceptance Criteria

1. Le domaine consultation expose un `fallback_mode` stable au minimum pour `user_no_birth_time`, `other_no_birth_time`, `relation_user_only`, `timing_degraded`, `blocking_missing_data`.
2. Le backend distingue clairement `nominal`, `degraded` et `blocked` et n'autorise pas une génération qui simulerait une capacité absente.
3. Le frontend consultations affiche un message standardisé de limitation et une action claire (`continuer en mode dégradé`, `compléter les données`, `retour`) pour chaque fallback.
4. Les parcours `relation` et `timing` n'affichent jamais un wording laissant croire à une synastrie complète ou à un timing fin si les données nécessaires sont absentes.
5. Le résultat sauvegardé et l'ouverture dans le chat conservent la trace du `fallback_mode` et du `precision_level`.
6. Une matrice de safeguards consultation distingue explicitement pour les catégories sensibles au minimum `health`, `emotional_distress`, `obsessive_relation`, `pregnancy`, `death`, `legal_finance`, `third_party_manipulation` les issues `fallback`, `refusal` ou `reframing`.
7. `i18n/consultations.ts` expose un wording contractuel par `fallback_mode` et par issue sensible, sans formulation trompeuse sur le niveau de certitude.
8. Les tests couvrent au minimum un parcours nominal, un fallback sans heure utilisateur, un fallback sans heure tiers, un mode `relation_user_only`, un cas bloquant et un cas sensible menant à refus ou recadrage.

## Tasks / Subtasks

- [ ] Task 1: Définir le référentiel de fallback consultation (AC: 1, 2)
  - [ ] Introduire les constantes / enums consultation pour les fallbacks autorisés
  - [ ] Documenter pour chaque fallback son déclencheur, sa promesse UX et sa limitation
  - [ ] Prévoir la compatibilité avec les résultats persistés

- [ ] Task 2: Implémenter la matrice de safeguards et la résolution backend nominal / degraded / blocked (AC: 1, 2, 4, 6)
  - [ ] Formaliser la table de décision `fallback / refusal / reframing` pour les catégories sensibles consultation
  - [ ] Brancher la résolution sur le précheck et les données collectées
  - [ ] Refuser explicitement les cas réellement bloquants
  - [ ] Éviter toute logique qui "inventerait" des données tiers ou une granularité temporelle absente

- [ ] Task 3: Intégrer les messages et confirmations frontend (AC: 3, 4, 7)
  - [ ] Ajouter un composant ou bandeau fallback consultation réutilisable
  - [ ] Standardiser le wording FR/EN/ES dans `i18n/consultations.ts` avec une clé dédiée par `fallback_mode` et par issue sensible
  - [ ] Prévoir les actions de poursuite ou de retour selon le mode

- [ ] Task 4: Propager fallback et précision jusqu'au runtime frontend (AC: 5, 7)
  - [ ] Étendre le modèle `ConsultationResult`
  - [ ] Mettre à jour le store / history / chat prefill pour porter ces métadonnées
  - [ ] Préserver la compatibilité de lecture des résultats 46.x qui ne possèdent pas encore ces champs

- [ ] Task 5: Tester les cas dégradés, bloquants et sensibles (AC: 8)
  - [ ] Ajouter des scénarios frontend sur les panneaux de limitation
  - [ ] Ajouter des tests backend de résolution de fallback
  - [ ] Ajouter un scénario de refus / recadrage sur catégorie sensible
  - [ ] Vérifier qu'aucun wording trompeur n'apparaît sur relation / timing

## Dev Notes

- Les modes dégradés sont l'élément de confiance central du backlog consultation complète. Le système actuel a déjà une forme de fallback via `SAFE_FALLBACK_MESSAGE`, mais pas de fallback produit explicite.
- Cette story ne doit pas se limiter à un simple message UI. Le `fallback_mode` doit devenir une donnée métier stable portée par le backend et le runtime consultations.
- Le wording doit rester consultation-centric et non anxiogène.
- Les safeguards sensibles ne doivent pas rester implicites dans `hard_policy` ou dans des prompts cachés. La feature consultation doit exposer une matrice explicite: ce qui peut continuer en mode dégradé, ce qui doit être refusé et ce qui doit être recadré vers une réponse de portée limitée.

### Previous Story Intelligence

- La story 47.2 établit les niveaux de précision et les cas bloquants; cette story transforme ces états en parcours produits assumés.
- La story 47.3 introduit la collecte et les choix "je ne sais pas"; ils doivent ici déboucher sur des fallbacks utiles.
- L'epic 46 a déjà fiabilisé l'historique local et l'ouverture dans le chat; ces chemins doivent continuer à fonctionner avec les nouveaux champs.

### Project Structure Notes

- Backend probable:
  - `backend/app/services/consultation_precheck_service.py`
  - `backend/app/services/consultation_fallback_service.py`
  - `backend/app/api/v1/routers/consultations.py`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend probable:
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/features/consultations/components/*`
  - `frontend/src/i18n/consultations.ts`

### Technical Requirements

- `fallback_mode` doit être un identifiant stable, pas une simple phrase UI.
- La limitation affichée doit être dérivée du mode calculé, pas d'une devinette côté composant.
- Les cas bloquants doivent expliquer ce qui manque et proposer une action claire.
- Les catégories sensibles doivent être mappées vers une issue stable (`fallback`, `refusal`, `reframing`) avant tout rendu frontend.

### Architecture Compliance

- Le backend reste source de vérité des états consultation.
- Le frontend ne formule pas lui-même les règles nominal/degraded/blocked.
- Les nouveaux champs doivent rester confinés au module consultations et à ses contrats API.

### Testing Requirements

- Backend: résolution des fallbacks et statuts bloquants.
- Frontend: affichage de bannière / panneau fallback, persistance des métadonnées et wording contractuel par mode.
- Vérifier la reprise de consultation sauvegardée avec fallback déjà calculé.

### References

- [Source: docs/backlog_epics_consultation_complete.md#8-epic-cc-04-gestion-des-modes-degrades-et-parcours-de-fallback]
- [Source: docs/backlog_epics_consultation_complete.md#18-criteres-dacceptation-transverses-reutilisables-dans-les-stories]
- [Source: _bmad-output/planning-artifacts/epic-47-consultation-complete-depuis-consultations.md]
- [Source: backend/app/services/guidance_service.py]
- [Source: frontend/src/pages/ConsultationResultPage.tsx]
- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/i18n/consultations.ts]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 47 et du backlog consultation complète.

### Completion Notes List

- Artefact créé uniquement; aucun code applicatif n'a été modifié.
- Le `SAFE_FALLBACK_MESSAGE` existant n'est pas la cible produit finale; il devient ici un filet technique, pas la feature.

### File List

- TBD pendant `dev-story`
