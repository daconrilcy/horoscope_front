# Story Candidates - scripts-ops

## SC-001

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Retirer le validateur story-specifique de la racine scripts
- Suggested archetype: dead-code-removal
- Primary domain: scripts-ops
- Required contracts: No Legacy / DRY
- Draft objective: supprimer ou relocaliser `scripts/validate_route_removal_audit.py` afin que la racine `scripts/` ne porte plus un outil ponctuel de story historique.
- Must include: scan de references avant/apres, mise a jour des artefacts story si un chemin executable est encore cite, absence de changement runtime.
- Validation hints: `rg -n "validate_route_removal_audit.py" .`; validation du dossier story si le chemin est modifie.
- Blockers: confirmer si l'audit historique doit rester executable.

## SC-003

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Formaliser l'ownership du dossier scripts
- Suggested archetype: namespace-convergence
- Primary domain: scripts-ops
- Required contracts: No Legacy / DRY, RG-015
- Draft objective: creer un index ou une topologie stable pour les scripts ops/dev afin de clarifier proprietaire, usage, test et statut legacy.
- Must include: classification de chaque script, chemins stables ou plan de migration, update docs.
- Validation hints: inventaire `rg --files scripts`, scan docs/tests pour chemins references.
- Blockers: choisir entre reorganisation physique en sous-dossiers ou index d'ownership conservant les chemins actuels.

## SC-004

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Durcir le script de demarrage dev local
- Suggested archetype: test-guard-hardening
- Primary domain: scripts-ops
- Required contracts: scripts dev Windows/PowerShell
- Draft objective: rendre Stripe optionnel dans `start-dev-stack.ps1`, ajouter une doc et une garde de syntaxe/comportement.
- Must include: parametre explicite, erreur claire si Stripe est demande mais absent, test ou scan de structure PowerShell.
- Validation hints: test PowerShell mocke, execution `-SkipStripe` sans Stripe CLI.
- Blockers: aucun.

## SC-005

- Candidate ID: SC-005
- Source finding: F-005
- Suggested story title: Clarifier les scenarios de charge critiques
- Suggested archetype: ownership-routing-refactor
- Primary domain: scripts-ops
- Required contracts: No Legacy / DRY
- Draft objective: separer les scenarios legacy/smoke, LLM, B2B et privacy destructif pour rendre le load-test previsible.
- Must include: manifest de scenarios ou fonctions dediees, choix explicite pour `privacy_delete_request`, conservation du rapport JSON/Markdown.
- Validation hints: dry-run ou tests mockes sur endpoints attendus; scan zero-hit des marqueurs `Story 66.35` et `Legacy critical scenarios`.
- Blockers: definir si le delete privacy reste dans le smoke par defaut.

## SC-006

- Candidate ID: SC-006
- Source finding: F-006
- Suggested story title: Rendre la readiness release LLM portable
- Suggested archetype: runtime-contract-preservation
- Primary domain: scripts-ops
- Required contracts: scripts release LLM
- Draft objective: supprimer le chemin absolu local du cache pytest dans `llm-release-readiness.ps1`.
- Must include: chemin derive du repo root, option de surcharge, pas de regression des fichiers de preuve generes.
- Validation hints: scan zero-hit `C:\dev\horoscope_front` dans le script; test manuel ou mock.
- Blockers: aucun.

## SC-007

- Candidate ID: SC-007
- Source finding: F-007
- Suggested story title: Classer le rapport natal cross-tool comme outil dev backend
- Suggested archetype: namespace-convergence
- Primary domain: scripts-ops
- Required contracts: No Legacy / DRY, frontiere test/dev
- Draft objective: clarifier l'emplacement et le contrat dev-only de `natal-cross-tool-report-dev.py`.
- Must include: doc d'usage avec venv, controle CI refusal deja existant, decision sur l'import de fixtures de test.
- Validation hints: `CI=true` refuse l'execution; execution dev limitee dans venv; scan imports.
- Blockers: aucun.
