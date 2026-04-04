# Story 64.9 — NatalChartPage : sections lockées free + CTA upgrade

Status: done

## Story

En tant qu'utilisateur free sur la page du thème natal,
je veux voir mon summary et mes titres de sections générés, mes evidence tags et le disclaimer toujours visibles, et les sections thématiques complètes affichées comme teasers floutés,
afin de comprendre la profondeur d'analyse disponible avec l'abonnement Basic et d'être incité à upgrader.

## Context

Dépend de **Stories 64.5** (hook) et **64.6** (composants LockedSection + UpgradeCTA).

`NatalChartPage.tsx` consomme `useLatestNatalChart` et `NatalInterpretationSection`. La réponse de l'interprétation natale contient plusieurs sections thématiques (PSY_PROFILE, SHADOW_INTEGRATION, RELATIONSHIP_STYLE, etc.).

**Comportement cible pour le plan free (résultat de Story 64.3) :**
- `summary` : rendu normalement (texte global généré pour free)
- `ni-accordion-title` par section : rendus comme titres (sans le contenu détaillé)
- `ni-evidence-tags` : **toujours visible et inchangé**
- `disclaimer` : **toujours visible et inchangé**
- Sections thématiques complètes : wrappées dans `LockedSection` avec teaser

**Comportement pour basic/premium :** Page rendue normalement.

## Acceptance Criteria

**AC1 — Utilisateur free : summary et accordion-titles rendus normalement**
**Given** un utilisateur free sur la page du thème natal  
**When** la page est rendue  
**Then** le `summary` global est affiché normalement sans blur  
**And** les titres de sections (`ni-accordion-title`) sont affichés normalement

**AC2 — ni-evidence-tags et disclaimer toujours visibles sans restriction**
**Given** un utilisateur free  
**When** la page est rendue  
**Then** les `ni-evidence-tags` sont visibles et non floutés  
**And** le disclaimer est visible et non floutés  
**And** ces deux éléments sont identiques à l'affichage basic/premium

**AC3 — Sections thématiques complètes en LockedSection avec teaser**
**Given** un utilisateur free  
**When** la page est rendue  
**Then** les sections thématiques complètes (ex: PSY_PROFILE, SHADOW_INTEGRATION, etc.) sont wrappées dans `<LockedSection>`  
**And** un texte teaser fixe (i18n) est affiché dans l'overlay  
**And** l'effet blur est visible

**AC4 — UpgradeCTA visible sur au moins une section lockée**
**Given** un utilisateur free  
**When** la page du thème natal est rendue  
**Then** au moins une section lockée contient `<UpgradeCTA featureCode="natal_chart_long" />`  
**And** le CTA pointe vers la page d'abonnement

**AC5 — Utilisateur basic ou premium : page inchangée**
**Given** un utilisateur basic ou premium  
**When** la page du thème natal est rendue  
**Then** toutes les sections sont rendues normalement sans verrouillage  
**And** aucune régression visuelle

**AC6 — Décision de verrouillage pilotée par variant_code (pas hardcodée)**
**Given** le code de `NatalChartPage.tsx`  
**When** inspecté  
**Then** la décision de locker repose sur `variant_code === "free_short"` depuis `useFeatureAccess("natal_chart_long")`  
**And** aucune condition du type `if plan_code === 'free'` n'est présente

**AC7 — Contenus teaser définis dans les fichiers i18n**
**Given** `frontend/src/i18n/natalChart.ts`  
**When** inspecté  
**Then** des clés de teaser existent pour les sections thématiques  
**And** les textes sont aspirationnels

**AC8 — Tests de rendu**
**Given** `frontend/src/tests/NatalChartPage.test.tsx` (à créer ou étendre)  
**When** les tests sont exécutés  
**Then** : rendu free (summary + titres normaux, sections thématiques lockées, evidence tags toujours visibles), rendu basic (tout déverrouillé)

## Tasks / Subtasks

- [x] T1 — Ajouter les clés teaser dans `natalChart.ts` (AC7)
  - [x] T1.1 Lire `frontend/src/i18n/natalChart.ts`
  - [x] T1.2 Ajouter les clés :
    ```ts
    teasers: {
      psyProfile: {
        fr: "Votre profil psychologique profond, révélé par la structure de votre thème natal...",
        en: "Your deep psychological profile, revealed by the structure of your natal chart..."
      },
      shadowIntegration: {
        fr: "Les ombres et ressources cachées que votre thème révèle...",
        en: "The shadows and hidden resources your chart reveals..."
      },
      relationshipStyle: {
        fr: "Votre façon d'aimer et de vous relier aux autres, selon votre Vénus et Maison VII...",
        en: "Your way of loving and relating to others, according to your Venus and House VII..."
      },
      // ... ajouter pour chaque module thématique
      generic: {
        fr: "Section disponible avec l'abonnement Basic — analyse approfondie de votre thème.",
        en: "Section available with Basic subscription — in-depth analysis of your chart."
      }
    }
    ```

- [x] T2 — Intégrer la logique de verrouillage dans `NatalChartPage.tsx` (AC1, AC2, AC3, AC4, AC5, AC6)
  - [x] T2.1 Lire entièrement `frontend/src/pages/NatalChartPage.tsx`
  - [x] T2.2 Lire `frontend/src/components/NatalInterpretation.tsx` pour comprendre comment les sections sont rendues
  - [x] T2.3 Ajouter `useFeatureAccess("natal_chart_long")` et calculer :
    ```tsx
    const natalAccess = useFeatureAccess("natal_chart_long")
    const isLockedFree = natalAccess?.variant_code === "free_short"
    ```
  - [x] T2.4 Identifier les sections thématiques dans le rendu (PSY_PROFILE, etc.) et appliquer le pattern :
    ```tsx
    {isLockedFree ? (
      <LockedSection
        cta={index === 0 ? <UpgradeCTA featureCode="natal_chart_long" /> : undefined}
        label={t.teasers[sectionKey]?.[lang] ?? t.teasers.generic[lang]}
      >
        <div className="teaser-placeholder">
          <h3>{accordionTitle}</h3>  {/* ni-accordion-title toujours rendu */}
          <p>{t.teasers[sectionKey]?.[lang] ?? t.teasers.generic[lang]}</p>
        </div>
      </LockedSection>
    ) : (
      <NatalSectionComponent section={section} />
    )}
    ```
  - [x] T2.5 S'assurer que `ni-evidence-tags` et `disclaimer` sont **TOUJOURS** rendus, hors de toute logique de verrouillage
  - [x] T2.6 S'assurer que le `summary` global est hors de la logique de verrouillage

- [x] T3 — Tests (AC8)
  - [x] T3.1 Créer ou étendre `frontend/src/tests/NatalChartPage.test.tsx`
  - [x] T3.2 Mock `useFeatureAccess("natal_chart_long")` avec `variant_code="free_short"` :
    - Vérifier : summary visible, evidence-tags visibles, disclaimer visible
    - Vérifier : sections thématiques dans LockedSection
  - [x] T3.3 Mock `useFeatureAccess` avec `variant_code="full"` → aucun verrouillage

- [x] T4 — Validation finale
  - [x] T4.1 Test manuel : compte free → layout conforme
  - [x] T4.2 Test manuel : compte basic → page complète sans lock
  - [x] T4.3 `npx vitest run` → 0 erreur

## Dev Notes

### Architecture de NatalInterpretation

Lire `frontend/src/components/NatalInterpretation.tsx` avant d'implémenter. Il est possible que les sections soient déjà rendues dans une boucle sur les modules — dans ce cas, la logique de verrouillage sera plus propre à injecter au niveau de ce composant plutôt que dans `NatalChartPage`.

Si `NatalInterpretation` est un composant lourd qui itère les sections, ajouter une prop `isLockedFree: boolean` et gérer le verrouillage à l'intérieur.

### ni-accordion-title dans les sections lockées

Pour le plan free, le backend retourne des titres (`accordion_titles`) mais pas le contenu des sections. Ces titres doivent être affichés dans le wrapper `LockedSection` (par-dessus le blur), pour que l'utilisateur voie *de quoi* parle la section avant de décider d'upgrader.

### Données null vs teaser

Si la section thématique est `null` dans la réponse API (cas free via Story 64.3), le composant doit détecter `section === null && isLockedFree` et afficher le teaser. Ne pas afficher d'état d'erreur pour du contenu intentionnellement absent.

### Position du CTA

Mettre `<UpgradeCTA>` sur la première section thématique lockée uniquement (index === 0). Éviter la multiplication des CTA sur une même page.

### Exceptions absolues : evidence-tags et disclaimer

Ces deux éléments doivent être rendus **avant ou après la boucle de sections thématiques**, jamais à l'intérieur d'une section lockée. Ils sont toujours visibles, quelle que soit la valeur de `isLockedFree`.

## Dev Agent Record

### File List

- `frontend/src/i18n/natalChart.ts` — modified (NATAL_SECTION_TEASERS, NatalTeaserKey, getNatalSectionTeaser)
- `frontend/src/components/NatalInterpretation.tsx` — modified (isLockedFree prop, LockedSection wrapping in SectionAccordion)
- `frontend/src/components/NatalInterpretation.css` — modified (.ni-accordion-header--locked, .teaser-placeholder)
- `frontend/src/pages/NatalChartPage.tsx` — modified (useFeatureAccess, isLockedFree, passed to NatalInterpretationSection)
- `frontend/src/tests/NatalChartPage.test.tsx` — modified (useEntitlementSnapshot mock + 3 tests Story 64.9)

### Implementation Notes

- `natalChart.ts` : ajout de `NATAL_SECTION_TEASERS` puis `NATAL_SECTION_LOCKED_COPY` (copies longues fixes, fr/en/es) avec helpers d'accès.
- `NatalInterpretation.tsx` : ajout de `isLockedFree?: boolean` à `Props`, passé via `InterpretationContent` → `SectionAccordion`. Dans `SectionAccordion`, quand `isLockedFree`, chaque section affiche le titre via `.ni-accordion-header--locked` + `LockedSection` avec faux contenu long flouté. CTA `UpgradeCTA` présent sur chaque section et routé vers `/settings/subscription`. EvidenceTags et disclaimer hors de la logique de verrouillage (toujours rendus par `InterpretationContent`). Summary toujours rendu (hors accordion).
- `NatalChartPage.tsx` : `isLockedFree = natalAccess?.variant_code === "free_short"` via `useFeatureAccess("natal_chart_long")`, passé à `NatalInterpretationSection`.
- Tests : `vi.mock("../hooks/useEntitlementSnapshot", ...)` ajouté. 3 tests dans describe "Story 64.9": AC2/AC3 (sections lockées), AC1 (summary visible), AC4/AC5 (basic déverrouillé). 64/64 tests passent.
- Ajustement final UX free natal :
  - le cadre résumé n'affiche plus le label générique `Résumé` ;
  - le titre visible dans la carte est maintenant une phrase de synthèse issue du payload free-short ;
  - le backend `natal_long_free` génère désormais `title + summary + accordion_titles` pour aligner le rendu avec la maquette produit.

### Post-Completion Hardening

- CTA header et CTA de régénération sur le flux free routés vers `/settings/subscription` au lieu de relancer une génération complète.
- Chaque section verrouillée du thème natal affiche désormais :
  - le titre réel issu du payload `free_short` ;
  - un faux contenu long fixe, défini en i18n, rendu sous blur ;
  - l'overlay lock standard ;
  - un `UpgradeCTA` direct vers l'abonnement Basic.
- Le badge `ni-level-badge` du flux free natal n'affiche plus `Complet` mais un badge de résumé pour éviter une promesse trompeuse.
- Backend `natal_interpretation_service_v2` durci pour réutiliser/mettre à jour la ligne `free_short` existante et éviter les erreurs `UNIQUE constraint failed` lors des clics répétés.
- Le cadre résumé free natal reprend une hiérarchie visuelle homogène avec les autres cartes, avec une accroche synthétique générée dans l'en-tête au lieu d'un titre statique.

### Validation Produit

- validation manuelle finale effectuée sur le rendu free du thème natal ;
- la carte résumé n'affiche plus `Résumé` comme intitulé interne et repose désormais sur la phrase de synthèse générée ;
- le comportement CTA/upgrade est confirmé conforme pour l'utilisateur free.
- le tunnel de conversion free → Basic reste cohérent jusqu'à `/settings/subscription`, avec ouverture d'un Checkout Stripe initial quand aucun profil Stripe n'existe encore pour l'utilisateur.
