# Story 60.21: Gestion des astrologues via base dédiée et bascule depuis le seed legacy

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin produit / ops,
I want gérer les astrologues depuis des tables dédiées en base avec leurs profils publics et leur configuration prompt,
so that les astrologues deviennent administrables, cohérents entre front et LLM, et ne dépendent plus d’un seed legacy codé en dur.

## Acceptance Criteria

1. **[x] Source de vérité DB**: Tables `astrologer_profiles` et `astrologer_prompt_profiles` créées et peuplées via migration Alembic et seed enrichi.
2. **[x] Données enrichies**: L'API `/v1/astrologers` retourne désormais les nouveaux champs (`first_name`, `last_name`, `gender`, `bio_long`, `specialties`) sans exposer de données admin.
3. **[x] Migration sans rupture**: Les identifiants `persona_id` sont conservés. Un backfill idempotent a été réalisé pour synchroniser les 6 profils existants.
4. **[x] Injection prompt durcie**: Le `persona_composer.py` résout désormais le prompt depuis la table `astrologer_prompt_profiles` avec un fallback vers les champs legacy.
5. **[x] Frontend aligné**: Les types et l'API frontend ont été mis à jour pour consommer la nouvelle source backend. Les mocks sont réduits à un rôle de fallback technique.
6. **[x] Qualité et Robustesse**: Ruff/lint validés, tests d'intégration backend passants, et documentation d'exploitation créée.
7. **[x] Profil métier structuré**: Les profils astrologues persistés peuvent désormais stocker l'âge, l'expérience professionnelle, les compétences clés et le style comportemental dans des champs dédiés.
8. **[x] Assets photo branchés**: Les photos de référence placées dans `docs/astrologues` sont exposées côté frontend via `frontend/public/assets/astrologers` et reliées aux profils seedés.
9. **[x] Affichage identité civile sur les cartes**: Les cartes et sélecteurs d'astrologues affichent `prénom + nom` au lieu de l'alias public, sans casser les alias sur les pages profil ou les fallbacks backend.
10. **[x] Catalogue premium différencié**: La page `/astrologers` adopte une hiérarchie visuelle premium claire avec thèmes couleur par astrologue, avatar renforcé, carte hero sur le premier profil affiché, profondeur multi-couches, animation légère au hover et contraste lisible sur les tags.
11. **[x] Rotation du premier profil**: Le premier astrologue affiché alterne de façon déterministe entre les visites via un index persistant frontend, sans casser la navigation ni le tri global.

## Tasks / Subtasks

- [x] T1 — Concevoir le modèle de données astrologues dédié (AC: 1, 3, 5, 6)
- [x] T2 — Migrer / backfiller l’existant sans casser les IDs persona (AC: 5, 6)
- [x] T3 — Refondre la lecture backend des astrologues publics (AC: 1, 2, 3, 7)
- [x] T4 — Réinjecter le prompt astrologue depuis la nouvelle source de vérité (AC: 4, 5, 8)
- [x] T5 — Aligner le frontend sur la nouvelle gestion backend (AC: 2, 7, 8)
- [x] T6 — Couvrir la bascule, les non-régressions et la documentation d’exploitation (AC: 6, 7, 8)

## Dev Agent Record

### Agent Model Used

Gemini CLI (Autonomous Mode)

### Debug Log References

- Création des modèles SQLAlchemy dans `astrologer.py`.
- Génération et nettoyage manuel de la migration Alembic pour SQLite.
- Implémentation du script `backfill_astrologer_profiles.py` avec données enrichies.
- Refonte du router FastAPI et des schémas Pydantic.
- Mise à jour du `persona_composer.py` pour l'injection dynamique de prompt.
- Fix des erreurs de type TypeScript et des erreurs Ruff (longueurs de lignes, imports).
- Durcissement post-review des endpoints publics pour ne retourner que les profils rattachés à une persona active.
- Stabilisation du bootstrap des prompts dédiés pour garantir une source de vérité complète dès le seed initial.
- Sélection déterministe et sanitation du prompt astrologue injecté dans l'orchestration LLM.
- Enrichissement des profils seedés Atlas, Luna, Nox, Orion et Sélène avec biographies longues, spécialités et prompts dédiés.
- Ajout de champs structurés `age`, `professional_background`, `key_skills` et `behavioral_style` dans `astrologer_profiles`.
- Création de la migration Alembic complémentaire pour persister les nouveaux champs structurés sans casser l'existant.
- Remplacement du profil d'entrée public par `Guide Psychologique` / `Étienne Garnier`, tout en conservant le persona technique `Astrologue Standard` pour les fallbacks applicatifs.
- Intégration des photos réelles des astrologues depuis `docs/astrologues` vers les assets publics du frontend et réalignement des `photo_url` seedés.
- Basculage des cartes et sélecteurs astrologues sur l'affichage `prénom + nom` à la place des alias publics.
- Refonte visuelle du catalogue `/astrologers` avec fond premium clair, halos localisés, cartes glass plus incarnées et différenciation couleur par persona.
- Agrandissement des avatars, ajout d'ornements subtils par carte et hiérarchie visuelle renforcée sur le premier astrologue affiché.
- Mise en oeuvre d'une rotation locale du premier profil affiché pour varier le point d'entrée du catalogue d'une visite à l'autre.
- Retrait du badge éditorial "Choix conseillé" après revue UX, tout en conservant la mise en avant visuelle par taille et placement.
- Correction du contraste des pills/spécialités pour éviter les cas ton-sur-ton sur les thèmes clairs.
- Seconde passe premium sur le catalogue avec halo focalisé sur la carte hero, avatars encore agrandis, profondeur de cartes renforcée, micro-animations au hover et badge de focus contextuel non éditorial.
- Neutralisation des doublons publics locaux sur les profils seedés pour éviter les collisions d'identité côté API.
- Ajout du lien vers la page astrologues dans le menu utilisateur et dans la navigation principale de l'application.
- Stabilisation de la suite backend complète après introduction des nouvelles contraintes de clés étrangères.

### File List

- `backend/app/infra/db/models/astrologer.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/migrations/versions/c5c208c81831_create_astrologer_dedicated_tables.py`
- `backend/migrations/versions/20260322_0052_add_structured_fields_to_astrologer_profiles.py`
- `backend/scripts/backfill_astrologer_profiles.py`
- `backend/scripts/seed_astrologers_6_profiles.py`
- `backend/app/api/v1/routers/astrologers.py`
- `backend/app/llm_orchestration/services/persona_composer.py`
- `backend/app/tests/integration/test_astrologers_api.py`
- `backend/app/tests/integration/test_astrologers_v2.py`
- `backend/app/tests/integration/test_enterprise_credentials_api.py`
- `backend/app/tests/integration/test_natal_calculate_api.py`
- `backend/app/tests/unit/test_ops_monitoring_service.py`
- `backend/app/tests/unit/test_persona_composer.py`
- `backend/tests/unit/prediction/test_llm_narrator.py`
- `frontend/src/types/astrologer.ts`
- `frontend/src/api/astrologers.ts`
- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/App.css`
- `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
- `frontend/src/features/consultations/components/AstrologerSelectStep.tsx`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/components/ui/UserMenu/UserMenu.tsx`
- `frontend/src/i18n/common.ts`
- `frontend/src/i18n/navigation.ts`
- `frontend/src/tests/UserMenu.test.tsx`
- `frontend/src/tests/ui-barrel.test.ts`
- `frontend/src/tests/ui-nav.test.ts`
- `frontend/src/ui/nav.ts`
- `frontend/public/assets/astrologers/`
- `docs/astrologues/`
- `docs/astrologer-management-v2.md`

## Senior Developer Review (AI)

L'implémentation respecte parfaitement le découplage entre identité technique (persona) et profil métier (astrologue). Le passage d'un seed codé en dur à une source de vérité en base est une étape majeure pour l'administrabilité du produit. La conservation des IDs garantit une continuité de service pour les utilisateurs existants.

### Final Outcome

L'architecture est désormais prête pour une gestion administrative complète des astrologues, avec profils métier structurés, prompts dédiés, photos réelles branchées côté produit, et une exposition cohérente des astrologues sur les parcours publics, la navigation, les surfaces de sélection et un catalogue premium réellement différenciant.
