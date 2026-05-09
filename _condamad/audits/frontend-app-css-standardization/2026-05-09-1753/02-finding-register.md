<!-- Registre des constats du re-audit App.css apres mise en oeuvre CS-121 a CS-124. -->

# Finding Register - frontend-app-css-standardization

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | frontend-app-css-standardization | E-003, E-008, E-013 | La convergence a cree et consomme des primitives, mais `App.css` conserve 442 variables `--app-*`, dont des prefixes massifs `person`, `activity`, `summary`, `flow`, `premium`, `precision`, `evidence`; le domaine n'est donc pas encore ferme selon le stop condition de l'audit precedent. | Classer chaque prefix `--app-*` restant en owner canonique, semantic-extension, page-scope a extraire, ou suppression; migrer les owners non generiques hors `App.css` ou vers primitives generiques documentees. | yes |
| F-002 | Medium | High | missing-guard | frontend-app-css-standardization | E-006, E-007, E-012, E-014 | La garde CS-124 protege les cinq mots explicitement scans, mais n'interdit pas les familles visuelles `precision-*` et `evidence-*` pourtant incluses dans la selection SC-003; ces familles restent actives dans `App.css` et dans des consommateurs TSX. | Etendre la garde App aux prefixes residuels classes, ou migrer `precision/evidence` vers primitives/owners dedies avant d'ajouter un scan zero-hit exact. | yes |

## Finding Details

### F-001 - Taxonomie `--app-*` encore non fermee

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-app-css-standardization
- Evidence: E-003, E-008, E-013.
- Expected rule: apres CS-121 a CS-124, `App.css` doit exposer des primitives generiques et des owners `--app-*` justifies; les noms page/service/component restants doivent etre documentes ou extraits.
- Actual state: l'inventaire actuel compte toujours 442 variables `--app-*`; les prefixes `person=124`, `activity=59`, `summary=26`, `flow=17`, `premium=15`, `precision=14`, `evidence=13`, `people=13`, `chat=11`, `usage=9` restent dans `#root`.
- Impact: La convergence a cree et consomme des primitives, mais `App.css` conserve 442 variables `--app-*`, dont des prefixes massifs `person`, `activity`, `summary`, `flow`, `premium`, `precision`, `evidence`; le domaine n'est donc pas encore ferme selon le stop condition de l'audit precedent.
- Recommended action: Classer chaque prefix `--app-*` restant en owner canonique, semantic-extension, page-scope a extraire, ou suppression; migrer les owners non generiques hors `App.css` ou vers primitives generiques documentees.
- Story candidate: yes
- Suggested archetype: registry-catalog-refactor
- Closure status: phased-with-map, car la surface est finie par selection regex et doit etre traitee en un plan de fermeture complet.

### F-002 - Garde CS-124 partielle pour les familles visuelles residuelles

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-app-css-standardization
- Evidence: E-006, E-007, E-012, E-014.
- Expected rule: les familles visees par SC-003 doivent etre migrees ou bloquees par une garde exacte, sans ancien nom conserve comme alias.
- Actual state: `precision-badge` et `evidence-pill/evidence-tags` restent styles dans `App.css`; `ConsultationSummaryStep`, `DataCollectionStep` et `NatalInterpretationEvidence` les consomment; `isAppSpecificName` ne couvre pas `precision` ni `evidence`.
- Impact: La garde CS-124 protege les cinq mots explicitement scans, mais n'interdit pas les familles visuelles `precision-*` et `evidence-*` pourtant incluses dans la selection SC-003; ces familles restent actives dans `App.css` et dans des consommateurs TSX.
- Recommended action: Etendre la garde App aux prefixes residuels classes, ou migrer `precision/evidence` vers primitives/owners dedies avant d'ajouter un scan zero-hit exact.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
- Closure status: closure-ready si traite avec F-001; bloque seulement si le produit veut conserver `precision/evidence` comme contrat public de classe.
