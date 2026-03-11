# Story 42.5: Repositionner les exactitudes comme couche impulsionnelle

Status: review

## Story

As a backend maintainer,
I want conserver les événements ponctuels comme une couche d'accentuation locale,
so that `E(c,t)` mette en évidence les moments forts sans porter seule toute la narration quotidienne.

## Acceptance Criteria

1. Les exactitudes, ingressions majeures et hits d'angles restent détectés.
2. Leur rôle est borné à une accentuation locale du signal, et non à la création d'un récit autonome.
3. La couche impulsionnelle est explicitement séparée des couches de fond `T(c,t)` et `A(c,t)`.
4. Un exact event isolé ne génère plus un relief produit disproportionné sur une journée faible.
5. Les tests montrent que `E(c,t)` accentue un régime existant sans le fabriquer seule.

## Tasks / Subtasks

- [x] Task 1: Définir la responsabilité fonctionnelle de `E(c,t)` (AC: 1, 2, 3)
  - [x] Identifier les événements qui restent impulsionnels
  - [x] Définir leur contribution maximale
  - [x] Séparer explicitement les responsabilités dans le code

- [x] Task 2: Brancher la couche impulsionnelle dans le pipeline v3 (AC: 2, 3)
  - [x] Réutiliser la détection existante quand pertinente
  - [x] Produire une sortie compatible avec le signal composite

- [x] Task 3: Garder la détection d'événements utile pour debug et evidence pack (AC: 1)
  - [x] Conserver les drivers astro explicites
  - [x] Éviter la perte de traçabilité

- [x] Task 4: Tests (AC: 4, 5)
  - [x] Tester le bornage de la couche impulsionnelle
  - [x] Tester l'absence de faux relief quand le fond de signal est faible

## Dev Notes

- La couche impulsionnelle est utile produit, mais elle doit devenir un accent, pas la charpente.
- Cette story est l'endroit où corriger définitivement le biais “un exact event = un turning point potentiel”.
- Le futur evidence pack devra continuer à exposer ces drivers, mais comme causes locales d'un signal, pas comme narration autonome.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/event_detector.py`
  - `backend/app/prediction/contribution_calculator.py`
  - `backend/app/prediction/engine_orchestrator.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/event_detector.py]
- [Source: backend/app/prediction/contribution_calculator.py]
- [Source: backend/app/prediction/turning_point_detector.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- `E(c,t)` n'utilise plus `B(c)` comme multiplicateur caché et s'appuie désormais sur un support local `T+A` pour n'accentuer qu'un régime déjà présent.
- `moon_sign_ingress` reste détecté et traçable comme impulsion locale, sans être doublonné dans la couche `A(c,t)`.
- Le runtime v3 expose maintenant des diagnostics dédiés `v3_impulse_signal` pour le debug et le futur evidence pack.

### File List

- `_bmad-output/implementation-artifacts/42-5-repositionner-les-exactitudes-comme-couche-impulsionnelle.md`
- `backend/app/prediction/impulse_signal_builder.py`
- `backend/app/prediction/intraday_activation_builder.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_impulse_signal_v3.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
