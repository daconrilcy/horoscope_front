# Story 47.6: Refondre la génération et la restitution structurée des consultations

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a consultations frontend engineer,
I want consommer le contrat backend consultation complet et refaire la page résultat autour de la précision, des limitations et des sections structurées,
so that `/consultations/result` reflète réellement la nouvelle consultation complète tout en préservant l'historique local et l'ouverture dans le chat.

## Acceptance Criteria

1. Le frontend consultations appelle le nouvel endpoint consultation dédié et ne consomme plus directement le payload brut de `guidance_contextual` comme contrat produit final.
2. `ConsultationResultPage` affiche au minimum une synthèse, des sections structurées, les limitations, le `precision_level`, le `fallback_mode` et les métadonnées utiles à l'utilisateur.
3. Le schéma d'historique consultations en localStorage est versionné et reste backward-compatible avec les entrées 46.x et legacy déjà normalisées.
4. L'action `Ouvrir dans le chat` reste disponible et inclut dans le message les informations pertinentes du résultat consultation complet, y compris limitations et précision quand elles existent.
5. Les états `loading`, `error`, `retry`, `empty` et `reload via ?id=` restent gérés proprement.
6. Le wording utilisateur affiché pour `relation`, `timing` et les autres parcours dégradés est contractuel, dérivé de `fallback_mode` et n'emploie jamais des formulations laissant croire à une précision ou à une complétude absente.
7. L'historique local 47.x ne conserve pas un profil tiers brut complet; seules les métadonnées minimales utiles au réaffichage et au prefill chat sont persistées.
8. Les tests frontend couvrent le rendu nominal, un résultat dégradé, un résultat legacy, un retry en erreur, le wording fallback et l'ouverture dans le chat.

## Tasks / Subtasks

- [ ] Task 1: Mettre à jour le contrat frontend consultation (AC: 1, 2, 3, 7)
  - [ ] Étendre `ConsultationResult` avec les nouveaux champs consultation complète
  - [ ] Versionner la normalisation locale pour supporter 46.x et 47.x
  - [ ] Ajouter un mapping explicite entre payload backend consultation et modèle frontend
  - [ ] Limiter la persistance locale aux métadonnées de résultat nécessaires, sans stocker un profil tiers brut complet

- [ ] Task 2: Rebrancher la génération sur l'endpoint consultation dédié (AC: 1, 5)
  - [ ] Remplacer l'appel direct à `useContextualGuidance()` dans le flow résultat
  - [ ] Conserver la redirection vers `/consultations/new` si le draft est incomplet
  - [ ] Gérer proprement les erreurs consultation-specific

- [ ] Task 3: Refaire la page résultat autour de la précision et des limitations (AC: 2, 6)
  - [ ] Ajouter les sections consultation complète hiérarchisées
  - [ ] Afficher explicitement la précision et le mode dégradé éventuel
  - [ ] Consommer un wording i18n contractuel par `fallback_mode` et par issue sensible
  - [ ] Conserver les actions `save`, `open in chat`, `back to consultations`

- [ ] Task 4: Préserver historique local et deep links (AC: 3, 5)
  - [ ] Adapter `normalizeConsultationResult`
  - [ ] Vérifier la lecture des anciens objets 46.x
  - [ ] Vérifier que `?id=` recharge correctement un résultat 47.x

- [ ] Task 5: Mettre à jour le prefill chat et les tests (AC: 4, 8)
  - [ ] Composer un message chat orienté consultation complète
  - [ ] Éviter tout bruit inutile ou faux niveau de précision
  - [ ] Couvrir nominal, degraded, legacy, retry et wording fallback avec snapshots ciblés si utile

## Dev Notes

- Le résultat consultation actuel reste une projection légère d'un payload guidance générique. Cette story doit le transformer en vue consultation dédiée sans casser la reprise locale.
- Le localStorage peut rester la persistance MVP de la feature tant qu'il n'y a pas de table backend consultation. Ne pas ouvrir un chantier DB transverse ici.
- Le message `open in chat` doit rester utile et compact; il ne faut pas coller l'intégralité du résultat structuré.
- Le wording affiché doit être contractuel: si `fallback_mode` ou une issue sensible réduit la portée réelle du résultat, l'interface doit le dire explicitement et de façon cohérente dans `i18n/consultations.ts`.

### Previous Story Intelligence

- La story 46.3 a déjà fiabilisé la migration legacy et le prefill chat; il faut enrichir ces mécanismes, pas les contourner.
- Les stories 47.4 et 47.5 introduisent les métadonnées `precision_level`, `fallback_mode`, `route_key`; la page résultat doit en être le premier usage visible.
- Les routes et actions de sauvegarde ont déjà des tests solides; les conserver est moins risqué qu'une réécriture complète du flow résultat.

### Project Structure Notes

- Fichiers principalement concernés:
  - `frontend/src/api/consultations.ts`
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/i18n/consultations.ts`
  - `frontend/src/tests/ConsultationReconnection.test.tsx`
  - `frontend/src/tests/ConsultationMigration.test.tsx`
  - `frontend/src/tests/ConsultationsPage.test.tsx`

### Technical Requirements

- Le schéma local doit rester compatible lecture avec les objets antérieurs.
- La page résultat ne doit pas dépendre de champs optionnels implicites non normalisés.
- Les sections affichées doivent être dérivées d'un contrat stable, pas d'un bricolage textuel côté composant.
- La persistance locale ne doit pas devenir un stockage implicite de données tiers brutes hors besoin direct de réaffichage.

### Architecture Compliance

- Réutiliser store et route existants du module consultations.
- Préserver le pattern `api client -> page -> store`.
- Ne pas modifier le contrat du chat hors prefill consultation.

### Testing Requirements

- Ajouter des tests de rendu sur résultat nominal et dégradé.
- Couvrir l'historique local versionné.
- Couvrir l'ouverture chat depuis un résultat 47.x.
- Vérifier le wording contractuel par fallback avec snapshots ciblés si la granularité UI le justifie.

### References

- [Source: docs/backlog_epics_consultation_complete.md#11-epic-cc-07-generation-llm-et-restitution-structuree]
- [Source: docs/backlog_epics_consultation_complete.md#13-epic-cc-09-integration-ux-front-de-lexperience-end-to-end]
- [Source: _bmad-output/planning-artifacts/epic-47-consultation-complete-depuis-consultations.md]
- [Source: _bmad-output/implementation-artifacts/46-3-migrer-l-historique-local-et-preserver-l-ouverture-dans-le-chat.md]
- [Source: frontend/src/pages/ConsultationResultPage.tsx]
- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/api/guidance.ts]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 47 et du backlog consultation complète.

### Completion Notes List

- Artefact créé uniquement; aucun code applicatif n'a été modifié.
- Le localStorage reste explicitement le mécanisme de persistance MVP consultations dans cette story.

### File List

- TBD pendant `dev-story`
