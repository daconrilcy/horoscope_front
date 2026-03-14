# Story 48.3: Verrouiller QA, accessibilité et performance du fond astrologique

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA and frontend quality owner,
I want verrouiller le fond astrologique animé par des tests et garde-fous ciblés,
so that l'évolution du résumé dashboard n'introduise ni régression de navigation, ni dette d'accessibilité, ni animation coûteuse ou instable.

## Acceptance Criteria

1. Les tests couvrent les états `success`, `loading`, `error` et `empty` de `/dashboard` avec le nouveau résumé astrologique.
2. Les garde-fous d'accessibilité sont vérifiés explicitement: canvas décoratif, `prefers-reduced-motion`, activation clavier de la carte, lisibilité des contenus.
3. Les suites vérifient que l'animation nettoie bien ses ressources au démontage et au remount de type Strict Mode.
4. Les assertions de non-régression confirment que `/dashboard` n'affiche toujours pas le détail daily complet, que `/dashboard/horoscope` reste inchangé et que les activités du dashboard restent présentes.
5. Les contraintes de performance minimales sont documentées et verrouillées dans les tests ou la revue de code ciblée: pas d'état React à chaque frame, DPR plafonné, pas de dépendance graphique supplémentaire.
6. Les fichiers BMAD de l'epic 48 reflètent explicitement ces garde-fous et les risques résiduels.
7. Les tests ou contrôles ciblés couvrent au moins un cas de fallback neutre sans signe et un cas `prefers-reduced-motion`.
8. Les contrastes du texte nominal sur le chemin nominal respectent WCAG AA, avec une cible explicite de `4.5:1` pour le texte normal et `3:1` pour le texte large.

## Tasks / Subtasks

- [x] Task 1: Étendre la couverture dashboard et composant (AC: 1, 4, 7)
  - [x] Mettre à jour `frontend/src/tests/DashboardPage.test.tsx`
  - [x] Compléter `frontend/src/tests/AstroMoodBackground.test.tsx`
  - [x] Vérifier les cas `success/loading/error/empty`
  - [x] Vérifier un cas de fallback sans `sun_sign_code`

- [x] Task 2: Verrouiller les garde-fous d'accessibilité (AC: 2, 7)
  - [x] Vérifier que le canvas est décoratif et n'ajoute pas d'élément focalisable
  - [x] Vérifier le comportement `prefers-reduced-motion`
  - [x] Vérifier que la carte résumé reste activable par `Enter` et `Space`
  - [x] Vérifier que le contraste texte/fond reste acceptable au moins sur le chemin nominal

- [x] Task 3: Verrouiller cleanup et stabilité React (AC: 3, 5)
  - [x] Tester l'annulation du `requestAnimationFrame`
  - [x] Tester la déconnexion du `ResizeObserver`
  - [x] Vérifier qu'un remount ne laisse pas de boucle résiduelle
  - [x] Contrôler que l'implémentation n'introduit pas de `setState` par frame
  - [x] Ajouter un test sous `React.StrictMode` vérifiant qu'après le double cycle setup/cleanup de développement, il ne subsiste qu'une seule boucle `requestAnimationFrame` active et un seul `ResizeObserver` actif

- [x] Task 4: Documenter les garde-fous finaux de l'epic (AC: 5, 6)
  - [x] Relire les stories 48.1 et 48.2 pour cohérence
  - [x] Documenter les risques résiduels et limites acceptées
  - [x] Si utile, produire une note de gate synthétique dans `_bmad-output/test-artifacts/`

## Dev Notes

- Cette story doit privilégier des assertions ciblées et lisibles plutôt que des snapshots massifs de canvas peu exploitables.
- Les tests dashboard existants constituent déjà une base robuste. Il faut les étendre, pas les remplacer.
- Le point le plus risqué est la fuite de ressources d'animation sous Strict Mode; cette story doit le verrouiller explicitement.
- L'absence de nouveau backend n'exonère pas de vérifier le coût réseau ajouté si `birth-data` est consommé depuis le dashboard: le cache React Query doit rester le chemin nominal.
- Les exigences de contraste ne doivent pas rester qualitatives dans la review: la cible attendue est WCAG AA sur le chemin nominal, avec `4.5:1` pour le texte normal et `3:1` pour le texte large.

### Previous Story Intelligence

- La story 45.4 a déjà verrouillé la navigation et les états dashboard. Elle sert de socle pour la non-régression de cette epic.
- La story 17.2 a déjà introduit un fond premium global; cette story doit vérifier que le nouveau fond local du résumé ne crée pas de conflit visuel ou d'empilement aberrant.
- La story 48.1 doit déjà tester le composant isolément; cette story concentre la passe finale de qualité sur l'intégration et les garde-fous.

### Project Structure Notes

- Fichiers de test principalement concernés:
  - `frontend/src/tests/DashboardPage.test.tsx`
  - `frontend/src/tests/AstroMoodBackground.test.tsx`
  - `frontend/src/tests/router.test.tsx` si la navigation dashboard doit être revalidée
  - `frontend/src/tests/visual-smoke.test.tsx` si un garde-fou CSS ciblé est jugé utile
- Artefacts BMAD potentiels:
  - `_bmad-output/test-artifacts/epic-48-background-dashboard-gate.md`

### Technical Requirements

- Vérifier explicitement les interactions avec `requestAnimationFrame`, `ResizeObserver` et `matchMedia`.
- Garder les tests robustes sous Vitest/JSDOM, quitte à mocker les APIs navigateur manquantes.
- Les contrôles de performance doivent rester pragmatiques: assertions structurelles sur le code et les effets, pas micro-benchmarks fragiles.

### Architecture Compliance

- Maintenir la séparation entre tests unitaires du composant et tests d'intégration dashboard.
- Ne pas déplacer la logique de qualité dans le runtime produit; la story doit surtout renforcer les suites de test et la documentation de garde-fous.
- Le parcours `/dashboard/horoscope` ne fait pas partie du périmètre de redesign visuel et doit rester stable.

### Library / Framework Requirements

- Vitest + Testing Library pour les suites frontend.
- JSDOM mocks pour `matchMedia`, `ResizeObserver` et `requestAnimationFrame` si nécessaire.
- Aucune nouvelle bibliothèque de test ou de snapshot visuel lourd sans nécessité démontrée.

### File Structure Requirements

- Les tests du composant restent dans `frontend/src/tests`.
- Les notes de gate éventuelles restent dans `_bmad-output/test-artifacts/`.
- Éviter de créer des fixtures de test dispersées si quelques builders locaux suffisent.

### Testing Requirements

- Couvrir les cas `success/loading/error/empty`.
- Couvrir `prefers-reduced-motion`.
- Couvrir cleanup `requestAnimationFrame` et `ResizeObserver`.
- Vérifier que le dashboard garde ses activités et n'affiche pas les sections détaillées.

### Project Context Reference

- Aucun `project-context.md` n'a été détecté dans le dépôt lors de la génération.
- Appliquer les conventions de `AGENTS.md`, de `architecture.md` et de la QA dashboard déjà posée en epic 45.

### References

- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#17-accessibilite]
- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#18-performance]
- [Source: _bmad-output/planning-artifacts/epic-48-fond-astrologique-anime-dashboard.md]
- [Source: _bmad-output/implementation-artifacts/45-4-verrouiller-qa-accessibilite-et-coherence-i18n-du-parcours-dashboard.md]
- [Source: frontend/src/tests/DashboardPage.test.tsx]
- [Source: frontend/src/tests/router.test.tsx]
- [Source: frontend/src/App.css]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée selon le workflow BMAD create-story en mode autonome.
- Contexte extrait des tests dashboard existants, des garde-fous d'accessibilité du document d'interface et des stories 45.x.

### Completion Notes List

- Story context prêt pour implémentation.
- Le verrouillage final cible explicitement reduced motion, cleanup et non-régression dashboard.
- QA verified SVG colors properly inherit parent container's context, without relying on external svgr plugin. 
- Horoscope card on `/dashboard/horoscope` layout properly wraps around AstroBackground to preserve background transparency metrics.

### File List

- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/AstroMoodBackground.test.tsx`
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_bmad-output/test-artifacts/epic-48-background-dashboard-gate.md`
