# Story 60.9 : Réécrire les microcopies et règles de wording

Status: review

## Story

En tant que membre de l'équipe produit,
je veux définir et appliquer un dictionnaire de libellés cohérents et des guidelines de wording,
afin que la page horoscope parle un langage premium, compréhensible et sans doublons sémantiques.

## Acceptance Criteria

1. Un fichier `backend/app/prediction/public_label_catalog.py` centralise tous les dictionnaires de labels utilisés par les policies backend (climate labels, regime labels, action hints, titles, why templates, etc.).
2. Un fichier `frontend/src/i18n/horoscope_copy.ts` centralise les libellés front utilisés dans les nouveaux composants.
3. Le mot "équilibré" n'apparaît plus que dans un seul bloc maximum sur la page (tolérance : day_climate.summary seulement).
4. Aucun libellé vague sans explication immédiate (interdit : "Une journée équilibrée" seul, "Le relief du moment s'apaise" sans contexte).
5. Tous les niveaux (`level`) ont un libellé public défini dans `horoscope_copy.ts` : très_favorable, favorable, stable, mitigé, exigeant.
6. Tous les régimes (`regime`) ont un libellé et un `action_hint` définis.
7. Tous les `change_type` (emergence, recomposition, attenuation) ont un title de fallback défini.
8. Les labels de domaines publics sont cohérents entre backend (`PUBLIC_DOMAINS`) et front (`horoscope_copy.ts`).
9. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [x] T1 — Consolider `public_label_catalog.py` (AC: 1)
  - [x] T1.1 Centraliser tous les dicts éparpillés dans les policies en Story 60.3–60.7 dans ce fichier
  - [x] T1.2 Structure cible consolidée
  - [x] T1.3 S'assurer que tous les fallbacks sont définis (aucun KeyError possible)
  - [x] T1.4 Vérifier couverture : chaque domaine public a une entrée dans chaque dict

- [x] T2 — Règles de wording à respecter (AC: 3, 4)
  - [x] T2.1 Remplacer "équilibré" par des termes plus évocateurs dans les dictionnaires.
  - [x] T2.2 Appliquer les remplacements obligatoires demandés.

- [x] T3 — Créer `frontend/src/i18n/horoscope_copy.ts` (AC: 2, 5, 6, 7, 8)
  - [x] T3.1 Définir `LEVEL_LABELS`, `REGIME_LABELS`, `CHANGE_TYPE_LABELS`, `DOMAIN_LABELS`.
  - [x] T3.2 Exporter helpers `getDomainLabel`, `getLevelLabel`, `getRegimeLabel`, `getChangeTypeLabel`.

- [x] T4 — Mettre à jour les composants pour utiliser `horoscope_copy.ts` (AC: 8)
  - [x] T4.1 `DomainRankingCard.tsx` → utiliser `DOMAIN_LABELS[domain.key]`
  - [x] T4.2 `DomainRankingCard.tsx` → utiliser `LEVEL_LABELS[domain.level]` pour badge
  - [x] T4.3 `DayTimelineSectionV4.tsx` → utiliser `REGIME_LABELS[window.regime]`
  - [x] T4.4 `TurningPointCard.tsx` → utiliser `CHANGE_TYPE_LABELS[turningPoint.change_type]`

- [x] T5 — Tests (AC: 9)
  - [x] T5.1 Vérifier que `pytest backend/` passe avec le catalogue consolidé.

## Dev Notes
...
### File List

- `backend/app/prediction/public_label_catalog.py` (MOD)
- `frontend/src/i18n/horoscope_copy.ts` (NEW)
- `frontend/src/components/DomainRankingCard.tsx` (MOD)
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx` (MOD)
- `frontend/src/components/TurningPointCard.tsx` (MOD)
