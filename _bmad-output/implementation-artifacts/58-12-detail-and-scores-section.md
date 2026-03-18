# Story 58.12 : Section DetailAndScoresSection — FocusMomentCard + DailyDomainsCard

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir sous la timeline une section à deux colonnes articulant le moment focal interprétatif (gauche) et les scores par domaine de la journée (droite),
afin d'avoir une lecture à la fois narrative et analytique de ma journée astrologique.

## Acceptance Criteria

1. [x] Le composant `DetailAndScoresSection` remplace le bloc inline `daily-layout__detail-scores` dans `DailyHoroscopePage.tsx` (Zone 5).
2. [x] `DetailAndScoresSection` utilise un grid asymétrique desktop (~1.6fr / 1fr) et un stack mobile vertical (FocusMomentCard d'abord).
3. [x] `FocusMomentCard` affiche : heure du créneau, titre interprétatif, tags de contexte (catégories dominantes), description/recommandation, CTA secondaire « Voir le détail ».
4. [x] `FocusMomentCard` affiche le slot 2h le plus significatif de la **période sélectionnée** dans `DayTimelineSection` ; si aucune période n'est sélectionnée, elle affiche le slot courant ou le meilleur slot de la journée.
5. [x] `DailyDomainsCard` affiche le titre « Domaines du jour », les 3 domaines principaux (icône + label + score + barre), les domaines secondaires (icône + label + mini-barre), et un CTA primaire violet.
6. [x] `DailyDomainsCard` se base sur les **scores de la journée complète** (`prediction.categories`), indépendamment de la période sélectionnée.
7. [x] Un décor abstrait radial mauve est présent en bas-droite de `FocusMomentCard` (pseudo-élément, purement décoratif).
8. [x] Les deux cartes partagent le même langage glassmorphism premium cohérent avec `PeriodCard` et `agenda-slot` existants.
9. [x] `tsc --noEmit` passe sans erreur.
10. [x] Les tests Vitest existants (≥ 1071) continuent de passer.

## Tasks / Subtasks

- [x] T1 — Créer les types TypeScript (AC: 3, 5)
  - [x] T1.1 Créer `frontend/src/types/detailScores.ts` avec `FocusMomentTag`, `FocusMomentCardModel`, `DailyDomainScore`, `DailyDomainsCardModel`

- [x] T2 — Créer les mappers (AC: 4, 6)
  - [x] T2.1 Créer `frontend/src/utils/focusMomentCardMapper.ts` : `buildFocusMomentCardModel(selectedPeriodKey, agendaSlots, prediction, lang)`
  - [x] T2.2 Créer `frontend/src/utils/dailyDomainsCardMapper.ts` : `buildDailyDomainsCardModel(categories, lang)`

- [x] T3 — Créer `FocusMomentCard` (AC: 3, 7, 8)
  - [x] T3.1 Créer `frontend/src/components/prediction/FocusMomentCard.tsx`
  - [x] T3.2 Créer `frontend/src/components/prediction/FocusMomentCard.css`

- [x] T4 — Créer `DailyDomainsCard` (AC: 5, 8)
  - [x] T4.1 Créer `frontend/src/components/prediction/DailyDomainsCard.tsx`
  - [x] T4.2 Créer `frontend/src/components/prediction/DailyDomainsCard.css`

- [x] T5 — Créer `DetailAndScoresSection` (AC: 1, 2)
  - [x] T5.1 Créer `frontend/src/components/prediction/DetailAndScoresSection.tsx`
  - [x] T5.2 Créer `frontend/src/components/prediction/DetailAndScoresSection.css`

- [x] T6 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 1, 4)
  - [x] T6.1 Remonter `selectedPeriod` depuis `DayTimelineSection` via callback prop ou lift state
  - [x] T6.2 Remplacer le bloc `daily-layout__detail-scores` inline par `<DetailAndScoresSection ... />`
  - [x] T6.3 Ajouter les clés i18n manquantes dans `frontend/src/i18n/predictions.ts` si nécessaire

- [x] T7 — Validation (AC: 9, 10)
  - [x] T7.1 `tsc --noEmit` — 0 erreur
  - [x] T7.2 `npx vitest run` — ≥ 1071 tests verts

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Post-implementation design corrections (claude-sonnet-4-6, 2026-03-18) — round 1

**Bugs corrigés :**

- `focusMomentCardMapper` : `semantic.description` → `semantic.transition || semantic.implication` — le champ `description` n'existe pas sur le retour de `humanizeTurningPointSemantic` ; la description enrichie des turning points n'était jamais affichée.
- `DailyDomainsCard` : garde ajoutée sur `secondaryDomains.length > 0` pour éviter un espace mort `var(--space-6)` quand la liste secondaire est vide.

**Corrections visuelles — passe 1 (audit comparatif maquette) :**

- `DetailAndScoresSection.css` : grid `minmax(0, 1.55fr) minmax(300px, 0.95fr)`, gap 18px.
- `FocusMomentCard.css` : surface blanche/lavande dominante (`rgba(255,255,255,.34→.22)`), border `rgba(255,255,255,.42)`, ombre diffuse. Décor `::after` radial mauve bas-droite + `.background-glow` second halo. Badge temps pill fine `rgba(.40)`. Titre `clamp(1.9rem, 3vw, 3rem)` poids 600. Tags pills soft normal-case `rgba(.42)`. Description `1.06rem max-width 36ch`. CTA capsule 48px `rgba(.72)` ombre violette légère.
- `DailyDomainsCard.css` : même glassmorphism. Top 3 : mini-cartes internes `rgba(.50)`, barres 5px. Secondaires : layout flex colonne, barres 3px, limités à 3 items (`slice(3,6)`). Scores : `Math.round()` (entiers, suppression des `.0`). CTA 52px `padding-top 18px`.

**Corrections visuelles — passe 2 (polish glass-premium) :**

- `FocusMomentCard.css` : surface encore plus claire et perlée (`rgba(255,255,255,.62→.44)`), border `rgba(230,220,255,.30)`. Badge temps 26px / 0.68rem poids 500 très discret, border `rgba(160,130,220,.14)`. Tags 28px pills `rgba(.55)` border `rgba(220,210,255,.28)` 0.76rem poids 500. Description `1.02rem max-width 32ch`. Décor halo élargi blur 22px + second glow `rgba(210,195,255,.12)`. CTA 46px `rgba(.78)` ombre 0.08. `justify-content: space-between` pour meilleure répartition verticale.
- `DailyDomainsCard.css` : surface unifiée avec FocusMomentCard (`rgba(.58→.40)`). Titre `opacity 0.60`. Items primaires `rgba(.60)` gap 9px. Séparation top 3 / secondaires par `border-top rgba(220,210,255,.20)` + `padding-top 12px`. Icônes secondaires `opacity 0.45`. Labels secondaires `0.72rem weight-400 opacity 0.70`. Scores secondaires `opacity 0.50`. Barres secondaires 2px fills plats `rgba(.35)`. CTA 50px `padding-top 22px` ombre `rgba(.18)`.

### Post-implementation fixes (claude-sonnet-4-6, 2026-03-18) — round 2

**Bugs corrigés :**

- `focusMomentCardMapper` : source du titre corrigée — utilise désormais `semantic.cause || semantic.title` (même source que `key-point-card__label`), au lieu du tone label ou du timeline block summary.
- `focusMomentCardMapper` : le lookup du TP était contraint au slot de 2h exact, qui pouvait être vide si `hasTurningPoint` était positionné par une frontière de timeline (pas un TP de `turning_points`). Désormais, le TP est recherché au niveau de la période sélectionnée, avec fallback sur `turning_points[0]`.
- `focusMomentCardMapper` : `prediction.turning_points` peut être vide (API sans TPs explicites) — dans ce cas `keyPointsSectionMapper` utilisait son fallback interne (`buildDailyKeyMoments`) mais `focusMomentCardMapper` tombait sur le titre par défaut. Correction : `keyMoments` (moments enrichis + fallback, déjà calculés dans `DailyHoroscopePage`) est maintenant passé en paramètre via `DetailAndScoresSection`.
- `DailyHoroscopePage.test.tsx` : fixture `predictionTechnical` — `turning_point.summary: "delta_note"` (valeur technique brute) remplacé par `null` ; le mapper affiche maintenant le titre sémantique calculé, pas la valeur brute.

**Corrections visuelles — passe 3 (polish manuel) :**

- `FocusMomentCard.css` — time badge : pill supprimée (`background: transparent`, `border: none`) ; texte horaire `0.9rem weight-600 var(--text-2)`. Titre `clamp(1.75rem, 1.7vw, 2.9rem)`. Tags : padding `0.5rem 1rem`, fond `var(--background-unselected-cell)`, border `rgba(220,210,255,0.7)`, `weight-600`, `box-shadow` léger ; icône tag `stroke-width: 3` + `fill: var(--primary)`. Description : `max-width: 32ch` supprimé. CTA : fond `var(--background-unselected-cell)`, border `rgba(230,220,255,0.8)` ; flèche `ArrowRight` ajoutée à droite (`strokeWidth 3, color: var(--primary)`).

### File List

- `frontend/src/types/detailScores.ts`
- `frontend/src/utils/focusMomentCardMapper.ts`
- `frontend/src/utils/dailyDomainsCardMapper.ts`
- `frontend/src/components/prediction/DetailAndScoresSection.tsx`
- `frontend/src/components/prediction/DetailAndScoresSection.css`
- `frontend/src/components/prediction/FocusMomentCard.tsx`
- `frontend/src/components/prediction/FocusMomentCard.css`
- `frontend/src/components/prediction/DailyDomainsCard.tsx`
- `frontend/src/components/prediction/DailyDomainsCard.css`
- `frontend/src/components/prediction/DayTimelineSection.tsx`
- `frontend/src/components/prediction/DayAgenda.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
