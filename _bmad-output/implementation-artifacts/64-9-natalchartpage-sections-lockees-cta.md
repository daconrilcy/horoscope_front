# Story 64.9 — NatalChartPage : sections lockées free + CTA upgrade

Status: todo

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

- [ ] T1 — Ajouter les clés teaser dans `natalChart.ts` (AC7)
  - [ ] T1.1 Lire `frontend/src/i18n/natalChart.ts`
  - [ ] T1.2 Ajouter les clés :
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

- [ ] T2 — Intégrer la logique de verrouillage dans `NatalChartPage.tsx` (AC1, AC2, AC3, AC4, AC5, AC6)
  - [ ] T2.1 Lire entièrement `frontend/src/pages/NatalChartPage.tsx`
  - [ ] T2.2 Lire `frontend/src/components/NatalInterpretation.tsx` pour comprendre comment les sections sont rendues
  - [ ] T2.3 Ajouter `useFeatureAccess("natal_chart_long")` et calculer :
    ```tsx
    const natalAccess = useFeatureAccess("natal_chart_long")
    const isLockedFree = natalAccess?.variant_code === "free_short"
    ```
  - [ ] T2.4 Identifier les sections thématiques dans le rendu (PSY_PROFILE, etc.) et appliquer le pattern :
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
  - [ ] T2.5 S'assurer que `ni-evidence-tags` et `disclaimer` sont **TOUJOURS** rendus, hors de toute logique de verrouillage
  - [ ] T2.6 S'assurer que le `summary` global est hors de la logique de verrouillage

- [ ] T3 — Tests (AC8)
  - [ ] T3.1 Créer ou étendre `frontend/src/tests/NatalChartPage.test.tsx`
  - [ ] T3.2 Mock `useFeatureAccess("natal_chart_long")` avec `variant_code="free_short"` :
    - Vérifier : summary visible, evidence-tags visibles, disclaimer visible
    - Vérifier : sections thématiques dans LockedSection
  - [ ] T3.3 Mock `useFeatureAccess` avec `variant_code="full"` → aucun verrouillage

- [ ] T4 — Validation finale
  - [ ] T4.1 Test manuel : compte free → layout conforme
  - [ ] T4.2 Test manuel : compte basic → page complète sans lock
  - [ ] T4.3 `npx vitest run` → 0 erreur

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
