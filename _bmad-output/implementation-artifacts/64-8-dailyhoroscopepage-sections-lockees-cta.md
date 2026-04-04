# Story 64.8 — DailyHoroscopePage : sections lockées free + CTA upgrade

Status: done

## Story

En tant qu'utilisateur free sur la page `/dashboard/horoscope`,
je veux voir mon horoscope du jour avec le résumé réel généré pour mon plan et les autres sections affichées comme teasers floutés,
afin de comprendre la valeur des contenus auxquels j'aurais accès en passant à l'abonnement Basic.

## Context

Dépend de **Stories 64.5** (hook) et **64.6** (composants LockedSection + UpgradeCTA).

`DailyHoroscopePage.tsx` consomme `useDailyPrediction(token)` qui retourne le payload de l'horoscope du jour.

**Comportement cible pour le plan free :**
- Section `DayClimateHero` : rendue normalement (contient le résumé — seule section générée pour free par 64.2)
- Sections `DomainRankingCard`, `DayTimelineSectionV4`, `TurningPointCard`, `BestWindowCard`, `AstroFoundationSection`, `DailyAdviceCard` : wrapper `LockedSection` avec contenu teaser fixe (i18n)

**Important (FR64-12) :** Les teasers sont des textes fixes marketing, pas du contenu généré incomplet.

**Comportement pour basic/premium :** Page rendue normalement, sans aucun verrouillage.

## Acceptance Criteria

**AC1 — Utilisateur free : DayClimateHero rendu normalement**
**Given** un utilisateur free sur `/dashboard/horoscope`  
**When** la page est rendue  
**Then** `DayClimateHero` affiche le contenu généré (summary) normalement  
**And** aucun blur ni overlay n'est appliqué à cette section

**AC2 — Utilisateur free : autres sections en LockedSection avec teaser**
**Given** un utilisateur free sur `/dashboard/horoscope`  
**When** la page est rendue  
**Then** les sections `DomainRankingCard`, `DayTimelineSectionV4`, `TurningPointCard`, `BestWindowCard`, `AstroFoundationSection`, `DailyAdviceCard` sont wrappées dans `<LockedSection>`  
**And** chaque section lockée affiche un contenu teaser fixe (texte marketing i18n)  
**And** l'effet blur est visible sur le teaser

**AC3 — UpgradeCTA visible sur au moins une section lockée**
**Given** un utilisateur free  
**When** la page est rendue  
**Then** au moins une section lockée contient un `<UpgradeCTA featureCode="horoscope_daily" />`  
**And** le CTA pointe vers la page d'abonnement

**AC4 — Utilisateur basic ou premium : page inchangée**
**Given** un utilisateur basic ou premium  
**When** la page `/dashboard/horoscope` est rendue  
**Then** toutes les sections sont rendues normalement sans aucun verrouillage  
**And** aucune régression visuelle

**AC5 — Décision d'affichage pilotée par entitlements (pas par plan_code hardcodé)**
**Given** le code de `DailyHoroscopePage.tsx`  
**When** inspecté  
**Then** la décision de locker les sections repose sur `variant_code` ou `granted` de la feature `horoscope_daily` (depuis `useFeatureAccess`)  
**And** aucune condition du type `if plan_code === 'free'` n'est présente dans la logique de verrouillage

**AC6 — Contenus teaser définis dans les fichiers i18n**
**Given** les fichiers `frontend/src/i18n/horoscope_copy.ts`  
**When** inspecté  
**Then** des clés de teaser existent pour chaque section lockée  
**And** les textes sont aspirationnels (ex: "Découvrez vos domaines d'énergie prioritaires ce jour...")

**AC7 — Tests de rendu**
**Given** `frontend/src/tests/DailyHoroscopePage.test.tsx` (à créer ou étendre)  
**When** les tests sont exécutés  
**Then** : rendu free (DayClimateHero normal + autres sections lockées), rendu basic (tout déverrouillé)

## Tasks / Subtasks

- [x] T1 — Ajouter les clés teaser dans `horoscope_copy.ts` (AC6)
  - [x] T1.1 Lire `frontend/src/i18n/horoscope_copy.ts`
  - [x] T1.2 Ajouter les clés de teaser :
    ```ts
    teasers: {
      domainRanking: {
        fr: "Découvrez vos domaines d'énergie prioritaires ce jour et comment les naviguer...",
        en: "Discover your priority energy domains for today and how to navigate them..."
      },
      dayTimeline: {
        fr: "Vos meilleures fenêtres temporelles pour agir, vous reposer et décider...",
        en: "Your best time windows to act, rest and decide..."
      },
      turningPoint: {
        fr: "Un tournant astrologique particulier est prévu ce jour — découvrez lequel...",
        en: "A particular astrological turning point is expected today — discover it..."
      },
      bestWindow: {
        fr: "La fenêtre idéale de votre journée, révélée par votre thème personnel...",
        en: "Your ideal time window, revealed by your personal chart..."
      },
      astroFoundation: {
        fr: "Les mouvements planétaires qui influencent votre journée en profondeur...",
        en: "The planetary movements deeply influencing your day..."
      },
      dailyAdvice: {
        fr: "Votre conseil personnalisé du jour, aligné à votre thème natal...",
        en: "Your personalized daily advice, aligned with your natal chart..."
      }
    }
    ```

- [x] T2 — Intégrer la logique de verrouillage dans `DailyHoroscopePage.tsx` (AC1, AC2, AC3, AC4, AC5)
  - [x] T2.1 Lu entièrement `frontend/src/pages/DailyHoroscopePage.tsx`
  - [x] T2.2 Ajouté `useFeatureAccess("horoscope_daily")` + import `LockedSection`, `UpgradeCTA`, `getHoroscopeTeaser`
  - [x] T2.3 `isLocked = featureAccess?.variant_code === "summary_only"`
  - [x] T2.4 Appliqué le pattern isLocked sur Zones 3,4,5,6,8,9 — non-locked garde le rendu conditionnel original
  - [x] T2.5 CTA uniquement sur DomainRankingCard (première section lockée)
  - [x] T2.6 DayClimateHero jamais wrappé

- [x] T3 — Tests (AC7)
  - [x] T3.1 Étendu `frontend/src/tests/DailyHoroscopePage.test.tsx`
  - [x] T3.2-T3.3 3 tests ajoutés dans describe "Story 64.8" + `installFetchMock` étendu avec `entitlements`

- [x] T4 — Validation finale
  - [x] T4.1-T4.2 N/A (test manuel)
  - [x] T4.3 22/22 tests DailyHoroscopePage ; suite complète : 4 échecs pré-existants uniquement

## Dev Notes

### Donnée de verrouillage : variant_code vs granted

Utiliser `featureAccess.variant_code === "summary_only"` comme critère de verrouillage des sections (et non `!featureAccess.granted` qui indiquerait un accès totalement refusé). Si `granted === false`, la page entière devrait afficher un état différent (accès refusé) — à traiter séparément.

## Dev Agent Record

### File List

- `frontend/src/i18n/horoscope_copy.ts` — modified (HOROSCOPE_TEASERS, TeaserKey, getHoroscopeTeaser)
- `frontend/src/pages/DailyHoroscopePage.tsx` — modified (useFeatureAccess, isLocked, LockedSection wrapping)
- `frontend/src/pages/DailyHoroscopePage.css` — modified (teaser-placeholder)
- `frontend/src/tests/DailyHoroscopePage.test.tsx` — modified (3 tests Story 64.8 + installFetchMock entitlements)

### Implementation Notes

- `horoscope_copy.ts` : ajout de `HOROSCOPE_TEASERS` (6 clés, fr/en/es) + `getHoroscopeTeaser(key, lang)`.
- `DailyHoroscopePage.tsx` : `isLocked = featureAccess?.variant_code === "summary_only"` via `useFeatureAccess("horoscope_daily")`. Zones 3,4,5,6,8,9 wrappées avec `LockedSection` quand locked. CTA `UpgradeCTA` uniquement sur Zone 3 (DomainRankingCard). DayClimateHero (Zone 2) jamais wrappé (AC1). Comportement non-locked inchangé (AC4).
- Pattern : quand locked → section toujours affichée avec teaser ; quand non-locked → comportement original préservé (null si données absentes).
- Tests : `installFetchMock` étendu avec option `entitlements`. Deux fixtures `makeEntitlementsMeFull()` / `makeEntitlementsMeFree()` créées. 3 tests pour AC2, AC3, AC4.

### Le payload backend pour free

Depuis Story 64.2, le backend ne retourne que `day_climate.summary` dans le payload pour les utilisateurs free. Les autres champs seront absents ou null dans `useDailyPrediction`. La logique de verrouillage doit être robuste à ces valeurs nulles — le teaser est affiché à la place du composant réel.

### Position du CTA

Mettre le CTA sur la deuxième section lockée (DomainRankingCard) — c'est la section la plus visible après le hero. Éviter de mettre un CTA sur chaque section (trop agressif).

### Teaser vs contenu généré incomplet

Les teasers sont des textes **fixes, écrits en dur dans l'i18n**. Ils ne doivent jamais être du contenu API partiellement affiché. Si le composant `DomainRankingCard` reçoit des données nulles, afficher le teaser — pas un état d'erreur.
