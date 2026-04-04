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
- Section `DayClimateHero` : rendue normalement (contient le résumé — seule section générée pour free par 64.2), avec un encart CTA vers Basic intégré sous le résumé éditorial
- Sections `DomainRankingCard`, `DayTimelineSectionV4`, `TurningPointCard`, `BestWindowCard`, `AstroFoundationSection`, `DailyAdviceCard` : wrapper `LockedSection` avec contenu teaser fixe long (lead + body, i18n), cadenas visible et CTA Basic sur chaque section

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

**AC3 — UpgradeCTA visible dans le hero et sur chaque section lockée**
**Given** un utilisateur free  
**When** la page est rendue  
**Then** `DayClimateHero` affiche un message d'upgrade contextualisé vers Basic sous le résumé  
**And** chaque section lockée contient un `<UpgradeCTA featureCode="horoscope_daily" />`  
**And** chaque CTA pointe vers la page d'abonnement `/settings/subscription`

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
**And** les textes sont aspirationnels et suffisamment longs pour simuler un vrai contenu verrouillé  
**And** chaque teaser contient une structure `lead + body`

**AC7 — Tests de rendu**
**Given** `frontend/src/tests/DailyHoroscopePage.test.tsx` (à créer ou étendre)  
**When** les tests sont exécutés  
**Then** : rendu free (DayClimateHero normal + autres sections lockées), rendu basic (tout déverrouillé)

## Tasks / Subtasks

- [x] T1 — Ajouter les clés teaser dans `horoscope_copy.ts` (AC6)
  - [x] T1.1 Lire `frontend/src/i18n/horoscope_copy.ts`
  - [x] T1.2 Ajouter les clés de teaser :
    - `teaser` court pour le label overlay
    - `lead` long pour le faux contenu flouté
    - `body` long pour renforcer l'effet de contenu premium verrouillé
  - [x] T1.3 Ajouter un message CTA hero et un libellé CTA Basic dédiés à l'horoscope du jour free

- [x] T2 — Intégrer la logique de verrouillage dans `DailyHoroscopePage.tsx` (AC1, AC2, AC3, AC4, AC5)
  - [x] T2.1 Lu entièrement `frontend/src/pages/DailyHoroscopePage.tsx`
  - [x] T2.2 Ajouté `useFeatureAccess("horoscope_daily")` + import `LockedSection`, `UpgradeCTA`, helpers de teaser/CTA hero
  - [x] T2.3 `isLocked = featureAccess?.variant_code === "summary_only"`
  - [x] T2.4 Ajouté un CTA Basic directement dans `DayClimateHero` pour le plan free
  - [x] T2.5 Appliqué le pattern isLocked sur Zones 3,4,5,6,8,9 avec teaser long structuré — non-locked garde le rendu conditionnel original
  - [x] T2.6 CTA Basic présent sur chaque `LockedSection`
  - [x] T2.7 DayClimateHero jamais wrappé

- [x] T3 — Tests (AC7)
  - [x] T3.1 Étendu `frontend/src/tests/DailyHoroscopePage.test.tsx`
  - [x] T3.2 Vérifier les teasers longs structurés pour le plan free
  - [x] T3.3 Vérifier le CTA hero Basic et les CTA sur chaque section lockée
  - [x] T3.4 Vérifier l'absence de régression pour basic/premium

- [x] T4 — Validation finale
  - [x] T4.1-T4.2 N/A (test manuel)
  - [x] T4.3 22/22 tests DailyHoroscopePage ; suite complète : 4 échecs pré-existants uniquement

## Dev Notes

### Donnée de verrouillage : variant_code vs granted

Utiliser `featureAccess.variant_code === "summary_only"` comme critère de verrouillage des sections (et non `!featureAccess.granted` qui indiquerait un accès totalement refusé). Si `granted === false`, la page entière devrait afficher un état différent (accès refusé) — à traiter séparément.

## Dev Agent Record

### File List

- `frontend/src/i18n/horoscope_copy.ts` — modified (HOROSCOPE_TEASERS, TeaserKey, getHoroscopeTeaser)
- `frontend/src/components/DayClimateHero.tsx` — modified (upgrade slot in free hero)
- `frontend/src/components/DayClimateHero.css` — modified (hero upgrade callout styles)
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.tsx` — modified (custom label support)
- `frontend/src/pages/DailyHoroscopePage.tsx` — modified (useFeatureAccess, isLocked, LockedSection wrapping, hero CTA, shared locked teaser component)
- `frontend/src/pages/DailyHoroscopePage.css` — modified (teaser-placeholder lead/body styles)
- `frontend/src/tests/DailyHoroscopePage.test.tsx` — modified (3 tests Story 64.8 + installFetchMock entitlements)

### Implementation Notes

- `horoscope_copy.ts` : ajout d'une structure `HOROSCOPE_LOCKED_COPY` (6 clés, `teaser` + `lead` + `body`) et de helpers dédiés pour le CTA hero/Basic.
- `UpgradeCTA.tsx` : ajout d'une prop `label` optionnelle pour personnaliser le message sans casser le hint backend.
- `DayClimateHero.tsx` : ajout d'un encart CTA free sous `day-climate-hero__summary`, sans wrapper lock.
- `DailyHoroscopePage.tsx` : `isLocked = featureAccess?.variant_code === "summary_only"` via `useFeatureAccess("horoscope_daily")`. Zones 3,4,5,6,8,9 wrappées avec `LockedSection` quand locked, toutes avec CTA vers `/settings/subscription`. DayClimateHero (Zone 2) reste visible mais affiche aussi un CTA Basic contextualisé (AC1/AC3). Comportement non-locked inchangé (AC4).
- Pattern : quand locked → section toujours affichée avec teaser ; quand non-locked → comportement original préservé (null si données absentes).
- Tests : `installFetchMock` étendu avec option `entitlements`. Deux fixtures `makeEntitlementsMeFull()` / `makeEntitlementsMeFree()` créées. Les tests vérifient désormais les teasers longs, le CTA hero, les CTA sur chaque section lockée et l'absence de régression pour basic/premium.

### Le payload backend pour free

Depuis Story 64.2, le backend ne retourne que `day_climate.summary` dans le payload pour les utilisateurs free. Les autres champs seront absents ou null dans `useDailyPrediction`. La logique de verrouillage doit être robuste à ces valeurs nulles — le teaser est affiché à la place du composant réel.

### Position du CTA

Le design final validé place désormais le CTA à deux niveaux :
- dans `DayClimateHero`, juste sous le résumé éditorial free ;
- dans chaque `LockedSection`, avec le même bénéfice Basic et une redirection uniforme vers `/settings/subscription`.

Cette répétition est volontaire pour rendre l'upgrade visible quel que soit le point d'arrêt de lecture sur mobile ou desktop.

### Teaser vs contenu généré incomplet

Les teasers sont des textes **fixes, écrits en dur dans l'i18n**. Ils ne doivent jamais être du contenu API partiellement affiché. Si le composant `DomainRankingCard` reçoit des données nulles, afficher le teaser — pas un état d'erreur.
