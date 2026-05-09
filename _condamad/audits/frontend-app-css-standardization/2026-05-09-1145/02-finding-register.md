<!-- Registre des constats pour la standardisation des classes dans App.css. -->

# Finding Register - frontend-app-css-standardization

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | frontend-app-css-standardization | E-006, E-007, E-009 | `App.css` centralise des styles specifiques au lieu de fournir des primitives reutilisables; la coherence d'effet reste dependante de 482 classes et 442 variables locales. | Definir une taxonomie finie de primitives CSS generiques App et les owners de tokens acceptes avant toute migration. | yes |
| F-002 | High | High | dry-violation | frontend-app-css-standardization | E-006, E-008, E-009 | Les patterns layout, etat et action sont recopies sous des noms differents; les arrondis de spacing/radius/typographie ne sont pas exploites pour converger. | Migrer les layouts, etats, boutons/actions et typographies de page vers les primitives generiques. | yes |
| F-003 | Medium | High | duplicate-responsibility | frontend-app-css-standardization | E-006, E-007, E-009 | Les cartes, listes, badges, modales et avatars conservent des noms de domaine qui empechent la reutilisation transversale. | Migrer les familles cartes/listes/badges/modales vers variantes generiques et supprimer les classes/variables specifiques devenues inutiles. | yes |
| F-004 | Medium | High | missing-guard | frontend-app-css-standardization | E-003, E-010, E-011, E-012 | Les guards existants protegent les literals et tokens, mais ne bloquent pas la reintroduction de selecteurs ou variables `--app-*` page-specific. | Ajouter une garde anti-drift qui interdit les nouveaux selecteurs/variables specifiques dans `App.css` hors allowlist exacte et temporaire. | yes |

## Finding Details

### F-001 - Centralisation sans primitives generiques

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-app-css-standardization
- Evidence: E-006, E-007, E-009.
- Expected rule: `App.css` doit exposer des classes generiques reutilisables pour produire les memes effets sur les pages, layouts et composants.
- Actual state: `App.css` contient 482 classes uniques et 442 variables `--app-*`; 290 variables portent un mot de domaine/page et 439 variables sont utilisees une seule fois.
- Impact: `App.css` centralise des styles specifiques au lieu de fournir des primitives reutilisables; la coherence d'effet reste dependante de 482 classes et 442 variables locales.
- Recommended action: Definir une taxonomie finie de primitives CSS generiques App et les owners de tokens acceptes avant toute migration.
- Story candidate: yes
- Suggested archetype: registry-catalog-refactor

### F-002 - Duplication structurelle malgre les tokens

- Severity: High
- Confidence: High
- Category: dry-violation
- Domain: frontend-app-css-standardization
- Evidence: E-006, E-008, E-009.
- Expected rule: les patterns repetes de flex/grid/gap/etat/action doivent etre portes par des classes generiques et des roles standardises.
- Actual state: `display:flex`, `flex-direction:column`, `align-items:center`, `gap`, `text-align:center`, margins et containers sont repetes dans des blocs nominatifs.
- Impact: Les patterns layout, etat et action sont recopies sous des noms differents; les arrondis de spacing/radius/typographie ne sont pas exploites pour converger.
- Recommended action: Migrer les layouts, etats, boutons/actions et typographies de page vers les primitives generiques.
- Story candidate: yes
- Suggested archetype: batch-migration

### F-003 - Composants visuels transverses nommes par domaine

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-app-css-standardization
- Evidence: E-006, E-007, E-009.
- Expected rule: une carte, une liste, un badge, une modale ou un avatar partage doit porter un nom generique et des variantes reutilisables.
- Actual state: les gros groupes `astrologer-card`, `consultation-card`, `dashboard-summary`, `precision-badge`, `settings-tab`, `modal` restent des owners visuels locaux dans `App.css`.
- Impact: Les cartes, listes, badges, modales et avatars conservent des noms de domaine qui empechent la reutilisation transversale.
- Recommended action: Migrer les familles cartes/listes/badges/modales vers variantes generiques et supprimer les classes/variables specifiques devenues inutiles.
- Story candidate: yes
- Suggested archetype: batch-migration

### F-004 - Absence de garde anti-retour sur la specificite App

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-app-css-standardization
- Evidence: E-003, E-010, E-011, E-012.
- Expected rule: apres convergence, un test doit echouer si `App.css` recree une classe ou variable nommee par page/service.
- Actual state: la garde existante bloque les literals et fallbacks, mais pas les noms comme `--app-astrologer-card-display-name-font-size`.
- Impact: Les guards existants protegent les literals et tokens, mais ne bloquent pas la reintroduction de selecteurs ou variables `--app-*` page-specific.
- Recommended action: Ajouter une garde anti-drift qui interdit les nouveaux selecteurs/variables specifiques dans `App.css` hors allowlist exacte et temporaire.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
