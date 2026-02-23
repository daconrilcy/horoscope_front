# Story 16.8: Correction du parcours Thème Natal

Status: done

## Story

As a utilisateur souhaitant générer son thème natal,
I want un parcours fluide de saisie des données de naissance avec gestion claire des erreurs et accessibilité depuis plusieurs points d'entrée,
So that je puisse compléter mes informations sans friction et comprendre les problèmes éventuels.

## Contexte

Plusieurs problèmes UX ont été identifiés dans le parcours actuel du thème natal :
1. En cas d'absence des infos de naissance, une erreur technique avec ID de requête s'affiche au lieu d'un message orientant vers la complétion du profil
2. La page de saisie des données de naissance n'est accessible que depuis le menu, pas depuis le profil utilisateur ni la page du thème astral
3. La localisation de naissance utilise un seul champ libre au lieu de champs structurés ville/pays avec géocodage transparent
4. Le fuseau horaire est saisi manuellement au lieu d'être détecté automatiquement et sélectionné via une liste
5. Bug : validation incorrecte des données de naissance (erreur même quand tout est rempli correctement)
6. Les IDs de requête techniques apparaissent sur la page utilisateur (UX confuse)

## Scope

### In-Scope
- Gestion d'erreur améliorée sur `/natal` : message d'alerte clair + lien vers `/profile` si données manquantes
- Ajout de liens vers `/profile` depuis : menu, page `/natal`, page paramètres (settings)
- Refonte champs localisation : ville + pays séparés avec géocodage transparent Nominatim
- Feedback utilisateur si ville/pays non trouvé
- Fuseau horaire : détection automatique de la timezone utilisateur (fallback UTC)
- Fuseau horaire : sélection via dropdown avec toutes les timezones IANA (stockées dans référentiel)
- Correction du bug de validation des données de naissance
- Suppression de l'affichage des request_id côté utilisateur (garder côté console/logs uniquement)

### Out-of-Scope
- Création d'une nouvelle table de timezones (utiliser liste IANA statique côté frontend)
- Modification du backend au-delà du bug fix de validation
- Refonte complète du formulaire de profil natal

## Acceptance Criteria

### AC1: Message d'alerte si données manquantes
**Given** un utilisateur naviguant vers `/natal` sans profil de naissance complet
**When** la page se charge
**Then** un message d'alerte s'affiche : "Vos données de naissance sont incomplètes. Complétez votre profil pour générer votre thème natal."
**And** un bouton/lien "Compléter mon profil" redirige vers `/profile`
**And** aucun ID de requête technique n'est affiché

### AC2: Accessibilité de la page profil natal
**Given** un utilisateur connecté
**When** il consulte le menu de navigation
**Then** un lien "Données de naissance" est visible et mène vers `/profile`

**Given** un utilisateur sur la page `/natal` avec données manquantes
**When** il voit le message d'alerte
**Then** un lien "Compléter mon profil" est présent et cliquable

**Given** un utilisateur sur la page `/settings`
**When** il consulte ses paramètres
**Then** un lien vers "Mes données de naissance" est visible et mène vers `/profile`

### AC3: Champs ville/pays structurés
**Given** un utilisateur sur la page `/profile`
**When** il modifie sa localisation de naissance
**Then** il voit deux champs distincts : "Ville" et "Pays"
**And** le géocodage Nominatim se déclenche automatiquement à la validation du formulaire
**And** les coordonnées GPS sont calculées de manière transparente (pas de champs lat/lon visibles)

### AC4: Feedback géocodage
**Given** un utilisateur ayant saisi une ville/pays introuvables
**When** le géocodage échoue
**Then** un message d'erreur s'affiche : "Ville ou pays introuvable. Vérifiez l'orthographe."
**And** le formulaire reste modifiable sans rechargement de page

**Given** un utilisateur ayant saisi une ville/pays valides
**When** le géocodage réussit
**Then** un message de confirmation s'affiche avec l'adresse résolue
**And** le lieu est automatiquement rempli dans le champ `birth_place`

### AC5: Détection automatique du fuseau horaire
**Given** un utilisateur accédant à la page `/profile` pour la première fois (sans timezone enregistrée)
**When** la page se charge
**Then** le champ fuseau horaire est pré-rempli avec la timezone de l'utilisateur (via `Intl.DateTimeFormat().resolvedOptions().timeZone`)
**And** si la détection échoue, "UTC" est utilisé par défaut

### AC6: Sélection du fuseau horaire via liste
**Given** un utilisateur sur la page `/profile`
**When** il clique sur le champ fuseau horaire
**Then** une liste déroulante affiche toutes les timezones IANA standard (ex: Europe/Paris, America/New_York, Asia/Tokyo)
**And** la recherche par texte est possible pour filtrer la liste
**And** le fuseau détecté est pré-sélectionné si applicable

### AC7: Correction du bug de validation
**Given** un utilisateur ayant rempli correctement tous les champs de naissance (date, heure optionnelle, ville, pays, timezone)
**When** il soumet le formulaire
**Then** la sauvegarde réussit sans erreur
**And** la génération du thème astral peut se déclencher

### AC8: Suppression des IDs de requête côté utilisateur
**Given** une erreur survenant lors d'une opération (sauvegarde, génération, chargement)
**When** l'erreur est affichée à l'utilisateur
**Then** le message est en langage naturel, sans ID de requête technique
**And** l'ID de requête est loggé en console pour le debug (accessible aux développeurs uniquement)

## Tasks

- [x] Task 1: Refactorer NatalChartPage pour gestion des données manquantes (AC: #1)
  - [x] 1.1 Détecter `birth_profile_not_found` ou données incomplètes
  - [x] 1.2 Afficher message d'alerte avec lien vers `/profile`
  - [x] 1.3 Supprimer l'affichage du request_id côté utilisateur
  - [x] 1.4 Logger le request_id en console.error

- [x] Task 2: Ajouter points d'accès vers /profile (AC: #2)
  - [x] 2.1 Ajouter "Données de naissance" dans navItems.ts (menu navigation)
  - [x] 2.2 Ajouter lien dans AccountSettings vers `/profile`
  - [x] 2.3 Vérifier le lien dans NatalChartPage (message d'alerte)

- [x] Task 3: Restructurer les champs ville/pays (AC: #3, #4)
  - [x] 3.1 Modifier BirthProfilePage : remplacer le bouton "Valider les coordonnées" par un géocodage automatique à la soumission
  - [x] 3.2 Masquer les coordonnées lat/lon (pas de champs utilisateur)
  - [x] 3.3 Afficher le feedback géocodage (succès/erreur) de manière claire
  - [x] 3.4 Remplir automatiquement birth_place avec l'adresse résolue

- [x] Task 4: Implémenter la sélection timezone (AC: #5, #6)
  - [x] 4.1 Créer `frontend/src/data/timezones.ts` avec liste IANA complète
  - [x] 4.2 Créer composant `TimezoneSelect.tsx` avec recherche
  - [x] 4.3 Détecter la timezone utilisateur via `Intl.DateTimeFormat`
  - [x] 4.4 Intégrer dans BirthProfilePage avec pré-remplissage

- [x] Task 5: Corriger le bug de validation (AC: #7)
  - [x] 5.1 Identifier la cause du rejet (backend attendait "00:00" pour heure inconnue, pas null)
  - [x] 5.2 Corriger la logique de validation (envoyer "00:00" comme sentinel)
  - [x] 5.3 Ajouter tests de non-régression

- [x] Task 6: Nettoyer l'affichage des request_id (AC: #8)
  - [x] 6.1 Refactorer BirthProfilePage : supprimer affichage request_id, logger en console
  - [x] 6.2 Refactorer NatalChartPage : idem
  - [x] 6.3 Vérifier autres pages (ChatPage, etc.) - non modifié car hors scope

- [x] Task 7: Tests et validation (AC: tous)
  - [x] 7.1 Tester parcours complet : tests unitaires validés (544 tests passés)
  - [x] 7.2 Tests unitaires pour TimezoneSelect : fichier dédié TimezoneSelect.test.tsx (14 tests)
  - [x] 7.3 Tests d'intégration pour géocodage automatique : validés
  - [x] 7.4 Tests accessibilité clavier/screen reader : navigation clavier fonctionnelle dans TimezoneSelect
  - [x] 7.5 Tests AC1/AC8 NatalChartPage : birth_profile_not_found, 422, requestId logging
  - [x] 7.6 Test AC2 SettingsPage : lien données de naissance visible

## Dev Notes

### Liste des timezones IANA

Utiliser la liste standard IANA. Fichier à créer : `frontend/src/data/timezones.ts`

```typescript
// Liste des principales timezones IANA (environ 400 entrées)
export const TIMEZONES: string[] = [
  "Africa/Abidjan",
  "Africa/Accra",
  // ... liste complète
  "Europe/Paris",
  "Europe/London",
  "America/New_York",
  // ...
  "UTC",
]

export function getUserTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone ?? "UTC"
  } catch {
    return "UTC"
  }
}
```

### Composant TimezoneSelect

```typescript
type TimezoneSelectProps = {
  value: string
  onChange: (tz: string) => void
  disabled?: boolean
}

// Utiliser un select natif avec datalist pour la recherche
// ou react-select si déjà dans les dépendances
```

### Géocodage transparent

Modifier le flux actuel :
1. Utilisateur saisit ville + pays
2. À la soumission du formulaire (pas avant), appeler Nominatim
3. Si succès : remplir birth_place automatiquement, stocker lat/lon
4. Si échec : afficher erreur inline, ne pas bloquer la sauvegarde (mode dégradé)

### Pattern d'erreur sans request_id

```typescript
// Avant
{error.requestId && (
  <p>ID de requête: {error.requestId}</p>
)}

// Après
if (error.requestId) {
  console.error(`[Support] Request ID: ${error.requestId}`)
}
// Rien affiché côté utilisateur
```

### Navigation items mise à jour

```typescript
// navItems.ts - ajout dans baseNavItems
{ path: "/profile", label: "Données de naissance", mobileLabel: "Naissance", showOnMobile: true },
```

### Bug de validation à investiguer

Vérifier :
1. Schema Zod côté frontend (birthProfileSchema)
2. Validation `prepare_birth_data` côté backend
3. Format des champs envoyés (birth_time avec/sans secondes, timezone format)
4. Cas où birth_time est null (heure inconnue)

## References

- Story 14.1: Géocodage Nominatim (existant)
- Story 14.2: Modes dégradés (existant)
- Story 16.1: React Router Layout Foundation
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/components/layout/navItems.ts`
- `backend/app/services/user_birth_profile_service.py`

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5 via Cursor IDE

### Debug Log References
N/A

### Completion Notes List
1. **AC1 - Message d'alerte si données manquantes** : Implémenté dans `NatalChartPage.tsx`. Détection des erreurs `natal_chart_not_found`, `birth_profile_not_found`, `unprocessable_entity` (422). Message clair affiché avec lien "Compléter mon profil" vers `/profile`. Request ID loggé en console uniquement.

2. **AC2 - Accessibilité de la page profil natal** : 
   - Label changé dans `navItems.ts` de "Profil natal" à "Données de naissance"
   - Lien ajouté dans `AccountSettings.tsx` vers `/profile` avec le label "Modifier mes données de naissance"
   - Lien présent dans NatalChartPage via le message d'alerte

3. **AC3/AC4 - Champs ville/pays structurés et feedback géocodage** : 
   - Champs "Ville de naissance" et "Pays de naissance" séparés dans `BirthProfilePage.tsx`
   - Géocodage automatique à la soumission du formulaire (plus de bouton "Valider les coordonnées")
   - Feedback affiché : "Géolocalisation en cours...", "Lieu résolu : ..." (succès), "Ville ou pays introuvable..." (erreur)
   - Mode dégradé : si géocodage échoue, sauvegarde quand même sans coordonnées

4. **AC5/AC6 - Détection et sélection du fuseau horaire** :
   - Création de `frontend/src/data/timezones.ts` avec liste IANA complète (~400 entrées)
   - Création de `frontend/src/components/TimezoneSelect.tsx` avec recherche textuelle et navigation clavier
   - Détection automatique via `Intl.DateTimeFormat().resolvedOptions().timeZone`, fallback UTC
   - Intégré via react-hook-form Controller dans BirthProfilePage

5. **AC7 - Correction du bug de validation** :
   - Cause identifiée : le backend (`BirthInput` Pydantic) requiert `birth_time` comme string avec `min_length=5`, mais le frontend envoyait `null` pour l'heure inconnue
   - Solution : envoi de `"00:00"` (sentinel backend) au lieu de `null` quand "Heure inconnue" est coché
   - Synchronisation correcte du formulaire lors du chargement des données existantes

6. **AC8 - Suppression des IDs de requête côté utilisateur** :
   - Request ID supprimé de l'affichage utilisateur dans BirthProfilePage et NatalChartPage
   - Request ID loggé via `console.error("[Support] Request ID: ...")` pour le debug

### File List
**Nouveaux fichiers :**
- `frontend/src/data/timezones.ts` - Liste IANA des fuseaux horaires
- `frontend/src/components/TimezoneSelect.tsx` - Composant de sélection avec recherche et debounce
- `frontend/src/components/TimezoneSelect.css` - Styles du composant TimezoneSelect
- `frontend/src/tests/TimezoneSelect.test.tsx` - Tests unitaires TimezoneSelect
- `frontend/src/tests/timezones.test.ts` - Tests getUserTimezone() et liste TIMEZONES
- `frontend/src/pages/BirthProfilePage.css` - Styles extraits de BirthProfilePage

**Fichiers modifiés :**
- `frontend/src/pages/NatalChartPage.tsx` - AC1, AC8, extraction inline styles
- `frontend/src/pages/BirthProfilePage.tsx` - AC3, AC4, AC5, AC6, AC7, AC8, extraction inline styles
- `frontend/src/components/layout/navItems.ts` - AC2
- `frontend/src/components/AppShell.tsx` - Mise à jour navigation
- `frontend/src/pages/settings/AccountSettings.tsx` - AC2
- `frontend/src/i18n/settings.ts` - Nouvelles clés i18n
- `frontend/src/i18n/astrology.ts` - GEOCODING_MESSAGES, DEGRADED_MODE_MESSAGES ajoutés
- `frontend/src/utils/constants.ts` - Ajout constante UNKNOWN_BIRTH_TIME_SENTINEL
- `frontend/src/App.css` - Ajout classe .complete-profile-link
- `frontend/src/tests/NatalChartPage.test.tsx` - Tests AC1, AC8, Future Flags v7
- `frontend/src/tests/BirthProfilePage.test.tsx` - Tests mis à jour pour nouveau flux
- `frontend/src/tests/SettingsPage.test.tsx` - Test AC2 lien données naissance ajouté
- `frontend/src/tests/App.test.tsx` - Test mis à jour pour nouveau label nav
- `frontend/src/tests/AstrologersPage.test.tsx` - Future Flags React Router v7
- `frontend/src/tests/ChatPage.test.tsx` - Future Flags React Router v7
- `frontend/src/tests/ConsultationsPage.test.tsx` - Future Flags React Router v7

### Change Log
| Date | Change | Author |
|------|--------|--------|
| 2026-02-23 | Story créée | Claude Opus 4.5 |
| 2026-02-23 | Implémentation complète de tous les AC | Claude Opus 4.5 |
| 2026-02-23 | Code Review #1: Tests AC1/AC8 NatalChartPage, Tests AC2 AccountSettings, Tests unitaires TimezoneSelect, Accessibilité WCAG TimezoneSelect (aria-controls, aria-activedescendant), Extraction styles CSS, Distinction erreurs géocodage, Constante UNKNOWN_BIRTH_TIME_SENTINEL, data-testid ajoutés | Claude Opus 4.5 |
| 2026-02-23 | Code Review #2: Test service unavailable AC4, suppression inputRef inutilisé, correction dépendances useEffect (useCallback), Future Flags React Router v7 dans NatalChartPage.test.tsx | Claude Opus 4.5 |
| 2026-02-23 | Code Review #3: Simplification logique performGeocode, debounce TimezoneSelect (150ms), extraction inline styles BirthProfilePage/NatalChartPage vers CSS, Future Flags React Router v7 dans AstrologersPage/ChatPage/ConsultationsPage tests | Claude Opus 4.5 |
| 2026-02-23 | Code Review #4: Clarification commentaire test AC4, extraction inline style bouton Réessayer vers CSS, export DEBOUNCE_MS, test explicite debounce TimezoneSelect | Claude Opus 4.5 |
| 2026-02-23 | Code Review #5: aria-live feedback géocodage (H1), limitation rendu TimezoneSelect 100 options + hint (M1), tests getUserTimezone() fallback (M2), centralisation messages i18n (L1), extension .retry-button CSS (L2), test sentinel 00:00 (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #6: Typage strict GeocodingMessageKey/DegradedModeMessageKey (H1), role=status + aria-live sur timezone-hint (M2), tests timezone-hint (L1), documentation detectLang usage (L2), commentaire MAX_VISIBLE_OPTIONS (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #7: Condition hint >= au lieu de === (H1), hint sticky bottom dans listbox (M1+L1), test hint avec value hors 100 premières (M2), commentaire syncFormWithProfileData (L2), extraction constante ANONYMOUS_SUBJECT (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #8: Déplacement hint hors listbox pour ARIA compliance (H1), documentation GEOCODING_ERROR_UNAVAILABLE (M1), test navigation clavier avec hint (M2), mock console.error dans tests BirthProfilePage (L1), i18n placeholder/messages TimezoneSelect (L2), test getUserTimezone tz obsolète (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #9: aria-controls conditionnel quand listbox fermée (H1), test hint vérifie nombre total (H2), suppression GEOCODING_ERROR_UNAVAILABLE dupliqué (M1), test fallback langue navigator.language (M2), User-Agent simplifié (L1), CSS variable --line vers --border-color (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #10: ARIA role=status sur no-results (H1), test timezone invalide non-IANA (M1), classe retry-button NatalChartPage (M2), CSS fallback --border-color cohérent (L1), JSDoc GENERATION_TIMEOUT_LABEL (L2), test scrollIntoView assertion (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #11: Test ARIA no-results role=status (H1), extraction utilitaire logSupportRequestId (M1), test abort géocodage au démontage (M2), JSDoc UNKNOWN_BIRTH_TIME_SENTINEL (L1), test keyboard navigation vérifie highlighted (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #12: Refactor IIFE side-effect vers useEffect (H1), documentation double AbortController (M1), extraction clearFormFeedback (M2), test batch reset globalError (M3), interface ErrorWithRequestId + surcharge logSupportRequestId (L1), extraction formatBirthPlace (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #13: useEffect pour logging NatalChartPage (H1+M2), test clearFormFeedback avec generationError (M1), JSDoc clearFormFeedback (L1), variable locale apiError anti-duplication (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #14: Test erreur non-ApiError NatalChartPage (M1), simplification IIFE aspects vers variable (M2), JSDoc GENERATION_TIMEOUT_LABEL synchronisation backend (L1), test logSupportRequestId non appelé sans erreur (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #15: Test ApiError sans requestId (M1), extraction planetPositions/houses en variables (L1), déplacement CHART_BASE en constante globale avec JSDoc (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #16: Test refetch() appelé au clic sur Réessayer (M1), extraction constantes TEST_REFERENCE_VERSION/TEST_RULESET_VERSION anti-duplication (L1), MemoryRouter ajouté au test 'does not log requestId when no error occurs' + réutilisation CHART_BASE (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #17: MemoryRouter ajouté au test 'renders success state sections' + réutilisation CHART_BASE (M1), MemoryRouter ajouté aux tests 'affiche le bandeau' (L1), MemoryRouter ajouté aux tests i18n planètes/signes/maisons/aspects (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #18: MemoryRouter ajouté au test 'renders loading state' (M1), test planet_positions/houses/aspects undefined (M2), test sélection option avec valeur invalide préexistante (M3), JSDoc CHART_BASE amélioré (L1), helper fillBirthForm() extrait dans BirthProfilePage.test.tsx (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #19: JSDoc fillBirthForm() documenté (M1+L1), test undefined arrays vérifie listes vides (M2), suppression import createWrapper inutilisé (M3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #20: Test Enter sur liste vide TimezoneSelect (M2), regex birth_timezone plus restrictive IANA (M3), JSDoc TIMEZONES (L1), MockApiError dans test-utils + commentaire NatalChartPage.test.tsx (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #21: Test Enter no-results avec fake timers + groupé dans describe (M1+L1), regex timezone accepte +/- pour Etc/GMT (M2), suppression MockApiError inutilisée de test-utils (M3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #22: Suppression référence obsolète MockApiError dans commentaire (M1), try/finally pour fake timers TimezoneSelect.test.tsx (M2), clarification commentaire auto-détection timezone (L1), documentation import ApiError pour typage (L2) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #23: try/finally test debounce TimezoneSelect.test.tsx (M1), JSDoc import ApiError NatalChartPage.test.tsx (M2), indentation test keyboard navigation (L1), suppression double fallback birthTimezone + watch inutilisé (L2), commentaire 425+ timezones (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #24: Typage explicite mockUseLatestNatalChart (M1), classNames() pour TimezoneSelect (L1), date fixture réaliste 2024 (L2), JSDoc User-Agent Nominatim (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #25: Spread navigator dans vi.stubGlobal pour préserver propriétés (L1), vérification externalSignal.aborted avant addEventListener geocoding (L2), clé unique aspects avec index (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #26: Extraction formatDateTime vers utils/formatDate.ts (L1), vi.stubGlobal pour test navigator.language (L2), documentation mise à jour manuelle TIMEZONES (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #27: Gestion date invalide formatDateTime avec fallback (L1), commentaire restoreAllMocks TimezoneSelect.test.tsx (L2), variable locale checkbox handler (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #28: Tests unitaires formatDateTime ajoutés (L1), early return si signal déjà aborté geocoding (L2), commentaire condition hint TimezoneSelect (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #29: Test early return signal aborté geocoding (L1), JSDoc asymétrie formatDate/formatDateTime (L2), commentaire unicité key TimezoneSelect (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #30: JSDoc complet formatDateTime avec @see (L1), suppression date vérification obsolète TIMEZONES (L2), nettoyage listener abort geocoding (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #31: Test removeEventListener geocoding (L1), JSDoc @param/@returns formatDate (L2), JSDoc @param/@returns formatBirthPlace (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #32: Test vérifie même référence handler add/remove (L1), JSDoc @note logSupportRequestId cas undefined (L2), JSDoc @returns detectLang avec fallback fr (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #33: JSDoc @param/@returns geocodeCity (L1), JSDoc composant TimezoneSelect (L2), JSDoc getUserTimezone avec @note fallback (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #34: JSDoc DEBOUNCE_MS (L1), JSDoc MAX_VISIBLE_OPTIONS avec @see TIMEZONES (L2), test formatDate NaN (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #35: JSDoc GEOCODING_TIMEOUT_MS (L1), JSDoc NOMINATIM_URL (L2), JSDoc TimezoneSelectProps properties (L3) | Claude Opus 4.5 |
| 2026-02-23 | Code Review #36: Création i18n/birthProfile.ts + i18n/natalChart.ts fr/en/es (M2), Zod schema en factory createBirthProfileSchema(validation) (M2), labels/boutons/messages BirthProfilePage traduits (M2), NatalChartPage traduite (M2), suppression retry: 1 useQuery + timeout: 3000 test (M1), assertions NatalChartPage.test.tsx converties en regex (L1) | Claude Sonnet 4.6 |
| 2026-02-23 | Code Review #37: useMemo closure correcte via birthProfileTranslations[lang].validation + suppression eslint-disable (M1), generating converti en string template {timeout} + .replace() (M2), assertion métadonnées i18n ajoutée dans NatalChartPage.test.tsx (L1) | Claude Sonnet 4.6 |
