# Finding Register - scripts-ops

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | legacy-surface | scripts-ops | E-003, E-014 | La racine `scripts/` conserve un validateur story-specifique dont l'usage durable est termine. | Supprimer `scripts/validate_route_removal_audit.py` apres confirmation que la story historique n'a plus besoin d'une commande executable depuis la racine, ou le deplacer sous le dossier de story. | yes |
| F-002 | Medium | High | legacy-surface | scripts-ops | E-007, E-010 | `stripe-listen-webhook.sh` duplique le script PowerShell alors que l'OS cible dev est Windows/PowerShell; docs/tests le rendent encore actif. | Decision utilisateur: supprimer le `.sh` et adapter docs/tests, ou le declarer explicitement support cross-platform. | needs-user-decision |
| F-003 | Medium | High | missing-canonical-owner | scripts-ops | E-001, E-002 | La racine melange quality gate, DB ops, securite, perf, LLM release, dev local et validateurs story; l'ownership est difficile a lire et favorise le legacy. | Organiser par familles (`quality`, `security`, `db`, `perf`, `llm`, `dev`, `story-tools`) ou documenter un index canonique avant de deplacer. | yes |
| F-004 | Medium | Medium | missing-test-coverage | scripts-ops | E-003, E-008 | `start-dev-stack.ps1` est utile pour le dev local mais non documente/teste; il rend Stripe obligatoire pour demarrer backend+frontend. | Ajouter une garde/test minimal et rendre Stripe optionnel via parametre, puis documenter le script dans le guide dev. | yes |
| F-005 | Medium | High | duplicate-responsibility | scripts-ops | E-009 | `load-test-critical.ps1` porte plusieurs vagues stories et des scenarios "Legacy critical"; le scope perf melange billing, privacy, chat, LLM, B2B et monitoring. | Factoriser les definitions de scenarios et separer smoke critique, matrice LLM et tests destructifs privacy. | yes |
| F-006 | Low | High | runtime-contract-drift | scripts-ops | E-011 | `llm-release-readiness.ps1` encode un chemin absolu local, ce qui casse la portabilite hors `C:\dev\horoscope_front`. | Remplacer le cache pytest par un chemin derive du repo root ou un parametre. | yes |
| F-007 | Low | Medium | boundary-violation | scripts-ops | E-012 | `natal-cross-tool-report-dev.py` est utile mais depend de fixtures de test backend et d'un module `backend/scripts`, depuis la racine `scripts/`. | Deplacer/classer comme outil dev backend, ou introduire un contrat explicite dev-only et une doc d'execution avec venv. | yes |
| F-008 | Info | High | observability-gap | scripts-ops | E-005, E-006, E-013, E-015, E-016 | Plusieurs scripts sont actifs, documentes et testes; ils doivent rester dans le perimetre supporte. | Conserver ces scripts et les proteger dans un index/ownership registry. | no |

## Details

### F-001

- Severity: High
- Confidence: High
- Category: legacy-surface
- Domain: scripts-ops
- Evidence: E-003, E-014.
- Expected rule: la racine `scripts/` contient des outils operationnels ou dev durables, pas des validateurs ponctuels de story terminee.
- Actual state: `validate_route_removal_audit.py` est reference par `_condamad/stories/remove-historical-facade-routes/**` et pas par les runbooks applicatifs.
- Impact: La racine `scripts/` conserve un validateur story-specifique dont l'usage durable est termine.
- Recommended action: Supprimer `scripts/validate_route_removal_audit.py` apres confirmation que la story historique n'a plus besoin d'une commande executable depuis la racine, ou le deplacer sous le dossier de story.
- Story candidate: yes
- Suggested archetype: dead-code-removal

### F-002

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: scripts-ops
- Evidence: E-007, E-010.
- Expected rule: la cible dev Windows/PowerShell evite les doubles implementations shell non necessaires.
- Actual state: `.ps1` et `.sh` contiennent la meme logique Stripe; le `.sh` est garde par docs/tests.
- Impact: `stripe-listen-webhook.sh` duplique le script PowerShell alors que l'OS cible dev est Windows/PowerShell; docs/tests le rendent encore actif.
- Recommended action: Decision utilisateur: supprimer le `.sh` et adapter docs/tests, ou le declarer explicitement support cross-platform.
- Story candidate: needs-user-decision
- Suggested archetype: legacy-facade-removal

### F-003

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: scripts-ops
- Evidence: E-001, E-002.
- Expected rule: un domaine scripts doit exposer des proprietaires lisibles et une topologie DRY.
- Actual state: tous les scripts cohabitent dans un dossier plat.
- Impact: La racine melange quality gate, DB ops, securite, perf, LLM release, dev local et validateurs story; l'ownership est difficile a lire et favorise le legacy.
- Recommended action: Organiser par familles (`quality`, `security`, `db`, `perf`, `llm`, `dev`, `story-tools`) ou documenter un index canonique avant de deplacer.
- Story candidate: yes
- Suggested archetype: namespace-convergence

### F-004

- Severity: Medium
- Confidence: Medium
- Category: missing-test-coverage
- Domain: scripts-ops
- Evidence: E-003, E-008.
- Expected rule: un script de demarrage local doit etre documente, testable, et ne pas imposer Stripe quand le besoin est backend/frontend.
- Actual state: Stripe CLI est requis et l'onglet Stripe est toujours cree.
- Impact: `start-dev-stack.ps1` est utile pour le dev local mais non documente/teste; il rend Stripe obligatoire pour demarrer backend+frontend.
- Recommended action: Ajouter une garde/test minimal et rendre Stripe optionnel via parametre, puis documenter le script dans le guide dev.
- Story candidate: yes
- Suggested archetype: test-guard-hardening

### F-005

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: scripts-ops
- Evidence: E-009.
- Expected rule: les scripts de charge doivent avoir des scenarios explicites, non destructifs par defaut, et sans marqueurs story/legacy actifs.
- Actual state: scenario `privacy_delete_request` actif et commentaires story/legacy dans le script principal.
- Impact: `load-test-critical.ps1` porte plusieurs vagues stories et des scenarios "Legacy critical"; le scope perf melange billing, privacy, chat, LLM, B2B et monitoring.
- Recommended action: Factoriser les definitions de scenarios et separer smoke critique, matrice LLM et tests destructifs privacy.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor

### F-006

- Severity: Low
- Confidence: High
- Category: runtime-contract-drift
- Domain: scripts-ops
- Evidence: E-011.
- Expected rule: un script release doit etre portable entre clones du repo.
- Actual state: chemin cache pytest absolu vers le poste local.
- Impact: `llm-release-readiness.ps1` encode un chemin absolu local, ce qui casse la portabilite hors `C:\dev\horoscope_front`.
- Recommended action: Remplacer le cache pytest par un chemin derive du repo root ou un parametre.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-007

- Severity: Low
- Confidence: Medium
- Category: boundary-violation
- Domain: scripts-ops
- Evidence: E-012.
- Expected rule: les scripts dev-only backend ne doivent pas brouiller les frontieres test/runtime/dev.
- Actual state: import direct de fixtures `app.tests.golden` et helper `scripts.cross_tool_report`.
- Impact: `natal-cross-tool-report-dev.py` est utile mais depend de fixtures de test backend et d'un module `backend/scripts`, depuis la racine `scripts/`.
- Recommended action: Deplacer/classer comme outil dev backend, ou introduire un contrat explicite dev-only et une doc d'execution avec venv.
- Story candidate: yes
- Suggested archetype: namespace-convergence

### F-008

- Severity: Info
- Confidence: High
- Category: observability-gap
- Domain: scripts-ops
- Evidence: E-005, E-006, E-013, E-015, E-016.
- Expected rule: scripts actifs et gardes restent supportes.
- Actual state: quality/security/DB/predeploy ont tests et docs.
- Impact: Plusieurs scripts sont actifs, documentes et testes; ils doivent rester dans le perimetre supporte.
- Recommended action: Conserver ces scripts et les proteger dans un index/ownership registry.
- Story candidate: no
- Suggested archetype: none
