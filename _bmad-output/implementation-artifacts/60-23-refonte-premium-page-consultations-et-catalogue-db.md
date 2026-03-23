# Story 60.23: Refonte premium de `/consultations` et catalogue DB des consultations types

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur authentifié souhaitant lancer une consultation,
I want une page `/consultations` premium, éditoriale et pilotée par un catalogue de consultations stocké en base,
so that je puisse choisir rapidement le bon type de consultation, tandis que l'équipe produit peut faire évoluer les modèles, prompts et microcopies sans recoder le frontend.

## Acceptance Criteria

### AC1 — Source de vérité DB pour les consultations types

1. Le catalogue visible des consultations n'est plus défini uniquement dans des constantes frontend ; il est piloté par une source de vérité persistée en base.
2. La modélisation persiste au minimum, dans une ou plusieurs tables dédiées, les champs suivants :
   - `key` (string, unique, stable)
   - `icon_ref` (lien, chemin d'asset, clé d'icône ou référence exploitable par le front)
   - `title`
   - `subtitle`
   - `description`
   - `prompt_content` associé
3. La solution peut utiliser soit une table unique, soit un couple de tables de type `consultation_templates` / `consultation_template_prompts`, mais le contrat final doit rester simple à administrer.
4. Le catalogue persiste les 5 consultations canoniques suivantes, avec clés métier stables :
   - `period`
   - `career`
   - `orientation`
   - `relationship`
   - `timing`
5. Le frontend affiche les libellés éditoriaux suivants sur les cards visibles :
   - `period` → `Où j’en suis en ce moment`
   - `career` → `Ma vie pro & mes décisions`
   - `orientation` → `Ce qui me correspond vraiment`
   - `relationship` → `Cette relation est-elle faite pour moi ?`
   - `timing` → `Est-ce le bon moment ?`
6. Les sous-titres visibles sont stockés dans le catalogue et correspondent aux formulations premium fournies par le besoin produit, pas à des labels techniques codés en dur dans la page.
7. Les micro-textes wizard et descriptions longues sont également pilotés par la base, afin d'éviter la duplication entre page catalogue et wizard.

### AC2 — Compatibilité et migration des clés legacy

8. La story traite explicitement la compatibilité entre les anciennes clés produit et les nouvelles clés canoniques.
9. Les anciennes clés `work` et `relation` ne cassent ni l'historique, ni les routes, ni les résultats déjà persistés ; elles sont soit migrées, soit normalisées vers :
   - `work` → `career`
   - `relation` → `relationship`
10. La stratégie retenue est documentée et testable :
   - compatibilité lecture pour l'existant
   - nouvelles créations sur les seules clés canoniques
   - absence de régression sur les dossiers ou historiques de consultation déjà enregistrés
11. Les types legacy cachés ou obsolètes (`dating`, `pro`, `event`, `free`) ne réapparaissent pas dans la façade publique `/consultations`.

### AC3 — Contrat API catalogue consultations

12. Le backend expose un contrat explicite pour récupérer le catalogue public des consultations types, sans forcer le frontend à reconstituer les métadonnées depuis des constantes locales.
13. Le contrat permet au minimum de retourner pour chaque consultation :
   - `key`
   - `icon_ref`
   - `title`
   - `subtitle`
   - `description`
   - éventuels tags / pills visibles
   - métadonnées nécessaires au wizard (`required_data`, `fallback_allowed`, `interaction_eligible`, etc.) si elles restent utiles au flow existant
14. Le contrat reste cohérent avec les endpoints consultations existants (`precheck`, `generate`, tiers) et ne crée pas un sous-système parallèle inutile.
15. La persistance prompt/catalogue est conçue pour pouvoir être modifiée simplement par produit/ops sans retoucher les composants React.

### AC4 — Refactor de `/consultations` en page premium chapitre 60

16. La page `/consultations` est refondue pour s'aligner visuellement avec les pages premium déjà livrées au chapitre 60 (`/today`, `/chat`, `/natal`, `/astrologers`, `/astrologers/:id`).
17. Le rendu réutilise au maximum les éléments, classes et styles existants déjà introduits sur les stories précédentes :
   - surfaces et tokens premium de `App.css`
   - patterns de fond clair céleste
   - halos / ornement astrologique
   - CTA, pills, glass cards et retours premium déjà présents
18. Aucun style inline massif ni design system parallèle n'est introduit ; l'implémentation reste dans les fichiers CSS/TSX du repo.
19. Le hero `/consultations` adopte une hiérarchie claire, proche de la maquette fournie :
   - bouton retour premium
   - grand titre éditorial
   - sous-texte centré et respirant
   - décor astrologique subtil en arrière-plan
20. Les consultations sont affichées sous forme de grandes cards premium en liste verticale, avec :
   - icône forte
   - titre
   - sous-titre / promesse
   - chips / tags
   - CTA `Choisir`
21. Le bas de page contient aussi une issue de secours premium du type `Je n’ai pas de préférence`, permettant de continuer sans imposer un type initial.

### AC5 — Nouvelles consultations visibles et wording premium

22. Les 5 cards visibles sur `/consultations` correspondent aux formulations éditoriales validées, et non plus aux titres legacy actuels.
23. Les contenus minimums associés sont les suivants :
   - `period`
     - titre : `Où j’en suis en ce moment`
     - sous-titre : `Faites le point sur la période que vous traversez et les dynamiques qui vous influencent.`
   - `career`
     - titre : `Ma vie pro & mes décisions`
     - sous-titre : `Éclairez vos choix professionnels, vos opportunités et vos prochaines étapes.`
   - `orientation`
     - titre : `Ce qui me correspond vraiment`
     - sous-titre : `Mieux comprendre vos forces, vos aspirations et la direction qui vous ressemble.`
   - `relationship`
     - titre : `Cette relation est-elle faite pour moi ?`
     - sous-titre : `Explorez la dynamique d’une relation amoureuse, personnelle ou professionnelle.`
   - `timing`
     - titre : `Est-ce le bon moment ?`
     - sous-titre : `Identifiez les périodes les plus favorables pour agir, lancer ou décider.`
24. Les descriptions longues/micro-textes wizard fournis dans le besoin sont bien conservés comme contenu piloté par données, et pas perdus dans la refonte visuelle.
25. Les tags visibles peuvent être éditoriaux (`Introspection`, `Bilan actuel`, `Évolution`, etc.), mais ils doivent être pilotés proprement par données et rester cohérents avec chaque consultation.

### AC6 — Wizard aligné sur le catalogue DB

26. Le wizard `/consultations/new` réutilise le nouveau catalogue DB comme source canonique de libellés, descriptions et métadonnées produit.
27. Le frontend ne conserve une configuration locale que comme fallback technique borné ou pour compatibilité historique ; la création normale s'appuie sur le backend.
28. Le choix d'une consultation sur `/consultations` ouvre le wizard avec la bonne clé canonique.
29. Le wizard garde les comportements existants utiles :
   - précheck
   - collecte conditionnelle
   - modes dégradés
   - tiers si applicable
30. Le refactor ne doit pas casser les parcours initiés depuis d'autres surfaces déjà en place, notamment :
   - depuis le profil astrologue
   - depuis le dashboard
   - depuis d'éventuels deep links `/consultations/new?type=...`

### AC7 — Réutilisation maximale et absence de duplication

31. La story privilégie l'extension des services, schémas et composants existants plutôt que l'introduction d'une seconde taxonomie frontend/backend.
32. Les composants existants de `/consultations` et du wizard sont réutilisés ou refactorisés proprement, sans copier-coller de nouvelles variantes.
33. Les prompts associés aux consultations types sont versionnables / administrables dans la continuité des patterns déjà introduits pour les prompts astrologues et autres catalogues.
34. Si des icônes plus visuelles que des emojis sont souhaitées à terme, la story doit prévoir un champ de référence compatible avec des assets publics sans imposer un format rigide cassant.

### AC8 — Responsive, accessibilité et états

35. La page `/consultations` reste parfaitement lisible en mobile avec empilement vertical des cards, CTA visibles et spacing premium cohérent.
36. Les états `loading`, `error`, `empty` et fallback catalogue sont explicitement gérés.
37. Les CTAs et cards restent navigables au clavier, avec libellés accessibles cohérents.
38. La refonte visuelle conserve un contraste lisible sur les fonds premium clairs et réutilise les variables de couleur déjà présentes.

### AC9 — Qualité, migrations et tests

39. Une migration Alembic est prévue si de nouvelles tables consultations types / prompts sont introduites.
40. Un seed ou backfill idempotent alimente les 5 consultations canoniques avec leurs textes et prompts.
41. Les tests backend couvrent au minimum :
   - lecture du catalogue public
   - unicité des clés
   - compatibilité legacy `work` / `relation`
   - seed/backfill idempotent
42. Les tests frontend couvrent au minimum :
   - rendu premium de la page `/consultations`
   - présence des 5 consultations attendues
   - routage correct vers le wizard
   - gestion du bouton `Je n’ai pas de préférence`
   - non-régression des parcours existants
43. Vérifications minimales attendues à l'implémentation :
   - `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` ciblé sur consultations
   - `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` sur les fichiers backend modifiés
   - `cd frontend; npx tsc --noEmit`
   - `cd frontend; npm run test -- ...` avec les suites consultations concernées

## Tasks / Subtasks

- [ ] T1 — Concevoir la source de vérité DB des consultations types (AC: 1, 2, 3, 9)
  - [ ] T1.1 Définir le modèle de persistance consultation type avec au minimum `key`, `icon_ref`, `title`, `subtitle`, `description` et prompt associé.
  - [ ] T1.2 Choisir proprement entre table unique et séparation `catalogue public` / `prompt`.
  - [ ] T1.3 Prévoir l'unicité, les index utiles et l'extensibilité pour tags, ordre d'affichage et métadonnées wizard.

- [ ] T2 — Introduire migration, seed et compatibilité legacy (AC: 1, 2, 9)
  - [ ] T2.1 Créer la migration Alembic des nouvelles tables si nécessaire.
  - [ ] T2.2 Seed les 5 consultations canoniques avec les textes éditoriaux validés et leurs prompts.
  - [ ] T2.3 Documenter et implémenter la stratégie de compatibilité `work/relation` vers `career/relationship`.
  - [ ] T2.4 Vérifier que les types legacy cachés n'apparaissent plus dans la façade publique.

- [ ] T3 — Exposer le catalogue public via l'API consultations (AC: 3, 6, 9)
  - [ ] T3.1 Étendre le router consultations avec un endpoint catalogue lisible par le front.
  - [ ] T3.2 Réutiliser les schémas et services existants autant que possible.
  - [ ] T3.3 Retourner aussi les métadonnées nécessaires au wizard si elles restent déterminantes pour la collecte conditionnelle.

- [ ] T4 — Refondre la page `/consultations` avec le langage premium du chapitre 60 (AC: 4, 5, 8, 9)
  - [ ] T4.1 Recomposer la page autour d'un hero premium, d'un fond clair céleste et d'une liste de cards consultation premium.
  - [ ] T4.2 Réutiliser les classes, surfaces et tokens existants avant toute création de nouveaux styles.
  - [ ] T4.3 Ajouter le fallback éditorial `Je n’ai pas de préférence`.

- [ ] T5 — Brancher le wizard sur le catalogue DB (AC: 5, 6, 7)
  - [ ] T5.1 Remplacer la dépendance primaire aux constantes frontend pour les titres/sous-titres/descriptions.
  - [ ] T5.2 Conserver un fallback technique borné pour robustesse locale/dev si nécessaire.
  - [ ] T5.3 Préserver le précheck, les modes dégradés et la collecte conditionnelle existants.

- [ ] T6 — Verrouiller non-régression, responsive et tests (AC: 6, 8, 9)
  - [ ] T6.1 Adapter le rendu mobile et l'accessibilité des cards / CTA.
  - [ ] T6.2 Ajouter ou mettre à jour les tests backend et frontend concernés.
  - [ ] T6.3 Vérifier les parcours initiés depuis `/consultations`, `/consultations/new`, le dashboard et la page profil astrologue.

## Dev Notes

- Réutiliser le sous-système consultations existant (`precheck`, `generate`, `third-parties`, flow wizard) ; la story vise un refactor piloté par données, pas une réécriture from scratch. [Source: backend/app/api/v1/routers/consultations.py]
- Le frontend possède aujourd'hui une taxonomie locale dans `frontend/src/types/consultation.ts` avec `period`, `work`, `orientation`, `relation`, `timing` plus des types legacy. La story doit la converger vers une source canonique backend, avec stratégie explicite de compatibilité. [Source: frontend/src/types/consultation.ts]
- Le style doit s'appuyer sur les patterns premium clairs déjà consolidés dans les stories 60.17 à 60.22, et rester cohérent avec les pages `/chat`, `/natal`, `/astrologers` et `/astrologers/:id`. [Source: _bmad-output/implementation-artifacts/60-17-refonte-visuelle-premium-page-horoscope.md] [Source: _bmad-output/implementation-artifacts/60-19-refonte-premium-page-chat-et-contexte-conversationnel.md] [Source: _bmad-output/implementation-artifacts/60-20-alignement-premium-page-natal.md] [Source: _bmad-output/implementation-artifacts/60-22-page-profil-astrologue-premium-conversion.md]
- Ne pas introduire Tailwind, styles inline massifs, ni nouvelle couche de design system. Le repo fonctionne déjà sur React + CSS dédié + tokens partagés. [Source: AGENTS.md]
- Les prompts des consultations types doivent être administrables comme contenus produit et rester versionnables/éditables sans duplication front-back.

### Project Structure Notes

- Backend attendu :
  - `backend/app/api/v1/routers/consultations.py`
  - `backend/app/api/v1/schemas/consultation.py`
  - `backend/app/services/consultation_*`
  - `backend/app/infra/db/models/`
  - `backend/migrations/versions/`
  - `backend/scripts/` pour seed/backfill si retenu
- Frontend attendu :
  - `frontend/src/pages/ConsultationsPage.tsx`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/api/consultations.ts` ou équivalent si le client catalogue n'existe pas encore
  - `frontend/src/types/consultation.ts`
  - fichiers CSS dédiés existants de la page consultations
- Éviter d'éparpiller la taxonomie dans plusieurs constantes concurrentes. Une seule source canonique doit piloter les clés, la façade publique et les métadonnées wizard.

### References

- `_bmad-output/implementation-artifacts/60-19-refonte-premium-page-chat-et-contexte-conversationnel.md`
- `_bmad-output/implementation-artifacts/60-20-alignement-premium-page-natal.md`
- `_bmad-output/implementation-artifacts/60-22-page-profil-astrologue-premium-conversion.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `frontend/src/pages/ConsultationsPage.tsx`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/types/consultation.ts`
- `backend/app/api/v1/routers/consultations.py`
- `backend/app/api/v1/schemas/consultation.py`

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Debug Log References

- Story créée via workflow BMAD `bmad-create-story`
- Alignement explicite avec la taxonomie consultations existante et les stories chapitre 60

### Completion Notes List

- Story orientée refactor brownfield, pas greenfield
- Compatibilité legacy `work` / `relation` explicitée pour éviter une implémentation cassante
- Source de vérité DB + façade premium `/consultations` + wizard aligné couverts dans un même lot

### File List

- `_bmad-output/implementation-artifacts/60-23-refonte-premium-page-consultations-et-catalogue-db.md`
