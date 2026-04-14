# Story 66.39: Durcissement de fiabilité multi-contexte du gate de conformité documentaire

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect / Maintainer du pipeline LLM,
I want rendre le gate documentaire 66.38 fiable et explicable sur tous les contextes Git/CI réels,
so that un contrôle désormais bloquant ne devienne ni flaky en local/CI, ni contournable sur des cas limites de changeset, de PR body ou de clone shallow.

## Contexte

La story [66-38-controle-automatique-conformite-doc-code.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-38-controle-automatique-conformite-doc-code.md) a déjà livré la gouvernance exécutable de base :

- manifeste unique [backend/app/llm_orchestration/doc_conformity_manifest.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/doc_conformity_manifest.py) ;
- validateur [backend/app/llm_orchestration/services/doc_conformity_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/doc_conformity_validator.py) ;
- CLI local/CI [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py) ;
- workflow PR bloquant [.github/workflows/llm-doc-conformity.yml](/c:/dev/horoscope_front/.github/workflows/llm-doc-conformity.yml) ;
- branchement au quality gate [scripts/quality-gate.ps1](/c:/dev/horoscope_front/scripts/quality-gate.ps1) ;
- couverture d’intégration [backend/tests/integration/test_story_66_38_doc_conformity.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_38_doc_conformity.py).

La doctrine documentaire est désormais claire :

- source de vérité unique pour le périmètre structurel ;
- obligation de mise à jour du bloc de preuve documentaire ;
- section PR bornée par motifs autorisés ;
- lints ciblés sur taxonomie, provider nominal, fallbacks et `obs_snapshot`.

Le risque principal a changé. Ce n’est plus un risque d’architecture, mais un risque de **fiabilité opérationnelle du garde-fou lui-même** :

- le calcul de changeset combine `merge-base`, diff de branche, staged, unstaged et untracked ;
- le workflow PR dépend du body PR et du contexte `github.base_ref` ;
- le gate doit rester prédictible sur poste Windows, branche locale atypique, CI GitHub et historiques partiels ;
- un parser trop permissif ou une erreur peu lisible transformeraient un garde-fou utile en source de friction ou de faux positifs.

66.39 ne doit donc **pas** changer la doctrine de 66.38. Elle doit la rendre **opérationnellement irréprochable**.

## Portée exacte

Cette story couvre cinq axes et rien de plus :

1. **matrice de tests multi-contexte** du détecteur de changeset ;
2. **durcissement du parser PR** avec erreurs stables et strictes ;
3. **mode diagnostic lisible** expliquant pourquoi un changeset est structurel ;
4. **tests de non-régression machine-vérifiables** pour les motifs autorisés ;
5. **sortie machine-readable** du contrôle documentaire pour réusage CI/outillage.

Elle ne doit pas :

- réécrire la doctrine documentaire ou le manifeste 66.38 sans nécessité ;
- élargir le périmètre doctrinal comparé doc ↔ code ;
- introduire une seconde commande concurrente au CLI documentaire existant ;
- dégrader la simplicité du quality gate local pour un besoin purement théorique.

## Diagnostic précis à traiter

Les dix vérifications prioritaires issues de la revue 66.38 doivent être traitées comme le cadrage de 66.39 :

1. unicité réelle de la source de vérité ;
2. robustesse du calcul de changeset en conditions Git réelles ;
3. caractère vraiment bloquant du bloc de preuve documentaire ;
4. strictesse du parser de template PR ;
5. cohérence sémantique exécutable des motifs autorisés ;
6. lisibilité du lint taxonomie ;
7. caractère binaire du lint provider nominal ;
8. solidité du lint fallback registry ;
9. fidélité du lint `obs_snapshot` sur la classification doctrinale ;
10. intégration réelle au quality gate standard.

La priorité d’implémentation est toutefois la suivante :

- d’abord les contextes Git/CI réellement fragiles ;
- ensuite la qualité des messages d’erreur et du diagnostic ;
- enfin l’export machine-readable et la couverture anti-régression.

## Cible d'architecture

Conserver le triptyque actuel :

1. **manifeste** = périmètre, format de preuve et motifs autorisés ;
2. **validateur réutilisable** = logique doctrinale pure et parser PR ;
3. **CLI unique** = résolution du contexte Git/CI, rendu humain et code de sortie.

La cible 66.39 est de renforcer ce triptyque avec deux propriétés supplémentaires :

- **déterminisme multi-contexte** : un même état logique produit la même décision quel que soit le contexte d’exécution supporté ;
- **explicabilité opérationnelle** : tout échec doit dire clairement quel fichier, quelle règle et quel contexte ont déclenché le gate.

Le point d’entrée unique doit rester [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py), y compris quand une sortie JSON ou un mode diagnostic est ajouté.

## Latest Technical Specifics

- `git merge-base` repose sur le meilleur ancêtre commun entre deux commits ; cela confirme que la fiabilité du gate dépend directement de la disponibilité réelle de l’historique nécessaire, et pas seulement du nom de branche. Source primaire : [git-merge-base documentation](https://git-scm.com/docs/git-merge-base).
- `actions/checkout` ne récupère qu’un seul commit par défaut ; `fetch-depth: 0` est explicitement requis pour obtenir tout l’historique. Le workflow 66.38 le fait déjà, mais 66.39 doit protéger les cas où ce prérequis ne serait pas respecté ou serait perdu par régression. Source primaire : [actions/checkout README](https://github.com/actions/checkout).

Inférences à imposer :

- le détecteur de changeset doit signaler explicitement quand il fonctionne en mode dégradé faute d’historique exploitable ;
- la stratégie de fallback Git doit être testée comme un contrat produit, pas comme un détail d’implémentation ;
- le workflow ne doit pas dépendre d’un comportement implicite de checkout ou de l’état du clone local.

## Acceptance Criteria

1. **AC1 — Source de vérité réellement unique** : `STRUCTURAL_FILES`, `DOC_PATH`, `VERIFICATION_MARKER` et `AUTHORIZED_PR_REASONS` sont définis uniquement dans [backend/app/llm_orchestration/doc_conformity_manifest.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/doc_conformity_manifest.py). Les autres composants du gate, des tests et du workflow consomment ces valeurs par import ou par lecture indirecte du manifeste, sans reconstruire localement de listes, tuples, enums ou constantes homologues.
2. **AC2 — Matrice changeset locale complète** : le détecteur de changeset couvre au minimum les cas `unstaged`, `staged`, `untracked`, branche locale sans upstream valide, `HEAD~1` indisponible et historique partiel. La décision de changeset est matérialisée par un résultat structuré de résolution de contexte Git exposant au minimum le mode retenu, la base utilisée si résolue, et les fichiers agrégés.
3. **AC3 — Matrice changeset CI complète** : la couverture teste explicitement un cas PR GitHub nominal avec `DOC_CONFORMITY_BASE_REF`, un cas clone shallow/dépouillé, et un cas fallback sans base exploitable. Si aucun `merge-base` exploitable n’est disponible, le CLI doit exposer explicitement un mode dégradé (taxonomie : `merge_base`, `head_prev`, `diff_tree`, `no_history`) ; cette décision ne doit jamais être silencieuse.
4. **AC4 — Bloc de preuve réellement bloquant** : les scénarios suivants sont testés et stables : changement structurel sans MAJ du bloc, changement cosmétique dans la section, changement de date seule, changement de référence stable seule. La validation porte sur les champs structurés du bloc final (`Date`, `Référence stable`) identifiés depuis le marqueur canonique, et non sur un diff textuel libre de la section complète.
5. **AC5 — Parser PR strict et prédictible** : le parser rejette de manière stable un body vide, une section non renseignée, plusieurs motifs cochés, un motif inconnu, un usage contradictoire de `OUI` et d’un motif, ou une justification incohérente avec l’état réel de la doc. Les erreurs sont déterministes et normalisées par règle violée.
6. **AC6 — Motifs autorisés exécutables** : chaque motif autorisé (`REF_ONLY`, `FIX_TYPO`, `TEST_ONLY`, `DOC_ONLY`, `NON_LLM`) possède une règle machine-vérifiable ou explicitement bornée :
   - `DOC_ONLY` : la doc a effectivement changé ; aucun fichier structurant hors doc/template/workflow n'est touché.
   - `NON_LLM` : des fichiers structurants ont été touchés (sinon le gate ne se déclenche pas), mais le changement est purement technique/infrastructurel (ex: refactor de script ou de workflow) sans modifier la doctrine LLM ni le périmètre métier documenté.
   - `TEST_ONLY` : seuls des fichiers dans des dossiers `tests/` ou nommés `test_*.py` (y compris s'ils sont dans `STRUCTURAL_FILES`) sont touchés.
   - `FIX_TYPO` : le diff est borné à des fichiers non-exécutables (markdown, templates PR) ou des commentaires sans effet sur la logique du gateway.
   - `REF_ONLY` : la mise à jour porte exclusivement sur la référence documentaire (Date/SHA) sans changement doctrinal.
   Aucun motif ne reste purement narratif.
7. **AC7 — Diagnostics de changeset lisibles** : un mode diagnostic ou une sortie explicite indique au minimum les fichiers considérés structurels, la base Git retenue, le mode de fallback utilisé et la raison de l’échec.
8. **AC8 — Lint taxonomie orienté review** : les erreurs sur familles nominales et alias legacy `daily_prediction -> horoscope_daily` et `natal_interpretation -> natal` sont compréhensibles sans lecture du code source.
9. **AC9 — Lint provider nominal binaire** : le contrôle explicite clairement l’attendu nominal `openai`, le constat documentaire et le constat code, sans ambiguïté.
10. **AC10 — Lint fallback registry borné** : la comparaison des fallbacks `USE_CASE_FIRST` et `RESOLVE_MODEL` reste limitée au noyau doctrinal documenté (statut et périmètre familles) et ne dérive pas vers du parsing narratif fragile.
11. **AC11 — Lint `obs_snapshot` fidèle** : la comparaison utilise bien la classification doctrinale `strict` / `thresholded` / `informational` et pas uniquement des seuils numériques indirects.
12. **AC12 — Sortie machine-readable** : le CLI peut produire une sortie structurée exploitable par d’autres workflows. Le contrat minimal expose au moins :
   - `status`
   - `git_context.mode`
   - `git_context.base_ref`
   - `git_context.base_commit` si résolu
   - `structural_files_detected`
   - `doc_changed`
   - `verification_block_updated`
   - `pr_section_status`
   - `errors[]` avec au minimum `code`, `message`, `rule` et `file` optionnel
   Le JSON ne doit pas être seulement valide syntaxiquement ; il doit être suffisant pour un réusage CI secondaire sans reparser la sortie texte.
13. **AC13 — Intégration quality gate inchangée côté appelant** : [scripts/quality-gate.ps1](/c:/dev/horoscope_front/scripts/quality-gate.ps1) continue d’appeler une seule commande stable ; en cas d’échec documentaire, le gate global échoue sans voie concurrente.
14. **AC14 — Windows + PowerShell supportés** : le comportement nominal du contrôle reste compatible avec le workflow local Windows/PowerShell déjà imposé par le dépôt.
15. **AC15 — Documentation de maintenance réalignée** : la documentation de maintenance du gate est mise à jour dans la doc runtime, ou dans un runbook explicitement référencé depuis elle. Elle décrit les nouveaux modes diagnostic, les scénarios Git supportés et la lecture des erreurs machine/humaines.
16. **AC16 — Preuve d’implémentation réelle des sorties critiques** : l’implémentation et la couverture automatisée prouvent explicitement trois points dans le code réel du gate :
   - l’option `--json` retourne bien la structure minimale attendue ;
   - `git_context.mode` expose la taxonomie bornée documentée sur au moins un cas nominal et un cas dégradé ;
   - la validation sémantique des motifs PR (`DOC_ONLY`, `NON_LLM`, `TEST_ONLY`, `FIX_TYPO`, `REF_ONLY`) est testée sur des cas réels positifs et négatifs.

## Tasks / Subtasks

- [ ] Task 1: Verrouiller l’unicité réelle de la source de vérité (AC1)
  - [ ] Auditer les constantes de périmètre, de doc path, de marqueur et de motifs autorisés.
  - [ ] Supprimer toute duplication résiduelle si elle existe et faire consommer ces valeurs par import depuis le manifeste.
  - [ ] Ajouter une protection de test qui échoue si une seconde source de vérité réapparaît ou si une liste homologue est reconstruite localement.

- [ ] Task 2: Durcir le calcul de changeset multi-contexte (AC2, AC3, AC7, AC14)
  - [ ] Introduire un résultat structuré de résolution de contexte Git (`GitContextResolutionResult` ou équivalent) séparant décision, provenance et fichiers détectés.
  - [ ] Couvrir les cas locaux `unstaged`, `staged`, `untracked`.
  - [ ] Couvrir les cas sans upstream propre, sans merge-base exploitable, avec historique partiel et avec fallback `HEAD~1` / `diff-tree`.
  - [ ] Définir une taxonomie bornée des modes Git retenus, y compris les modes dégradés, et la rendre explicite dans la sortie.

- [ ] Task 3: Rendre la vérification du bloc de preuve irréprochable (AC4)
  - [ ] Ajouter les scénarios sans changement, cosmétique seul, date seule, référence stable seule.
  - [ ] Vérifier que l’implémentation compare les champs structurés du bloc canonique et non un diff textuel libre de la section.
  - [ ] Vérifier que les messages d’échec distinguent clairement “doc non modifiée”, “bloc non réactualisé” et “base impossible à relire”.

- [ ] Task 4: Durcir le parser du corps PR et la sémantique des motifs autorisés (AC5, AC6)
  - [ ] Ajouter les cas body vide, section incomplète, plusieurs motifs, motif inconnu, contradictions `OUI` / motif.
  - [ ] Spécifier exécutablement les attentes minimales de `DOC_ONLY`, `NON_LLM`, `TEST_ONLY`, `FIX_TYPO`, `REF_ONLY`.
  - [ ] Produire des erreurs stables, orientées review et sans ambiguïté.

- [ ] Task 5: Améliorer les diagnostics humains et machine-readable (AC7, AC12, AC15)
  - [ ] Introduire une sortie structurée optionnelle (`json` ou équivalent) sur le CLI existant.
  - [ ] Inclure dans cette sortie le contrat minimal `status`, `git_context`, `structural_files_detected`, `doc_changed`, `verification_block_updated`, `pr_section_status` et `errors[]`.
  - [ ] Ajouter un mode diagnostic lisible pour expliquer la décision du gate.
  - [ ] Documenter le contrat de cette sortie et son usage CI/local.

- [ ] Task 6: Renforcer les messages des lints doctrinaux (AC8, AC9, AC10, AC11)
  - [ ] Vérifier la lisibilité des erreurs taxonomie, provider, fallback et `obs_snapshot`.
  - [ ] Garder les comparaisons bornées au contrat doctrinal machine-readable existant.
  - [ ] Empêcher tout élargissement fragile vers du markdown libre.

- [ ] Task 7: Maintenir un point d’entrée unique dans le quality gate (AC13, AC14)
  - [ ] Vérifier que `scripts/quality-gate.ps1` reste le point d’appel local standard.
  - [ ] Vérifier que le workflow PR appelle toujours le même CLI, sans seconde implémentation concurrente.
  - [ ] Ajouter la couverture de non-régression associée si nécessaire.

- [ ] Task 8: Prouver l’implémentation effective des sorties et règles critiques (AC16)
  - [ ] Ajouter des tests qui appellent réellement le CLI en mode `--json` et valident la présence des champs minimaux attendus.
  - [ ] Ajouter des tests dédiés sur `git_context.mode` couvrant au minimum un mode nominal et un mode dégradé documenté.
  - [ ] Ajouter des tests positifs et négatifs pour chaque motif PR autorisé afin de prouver la validation sémantique réelle dans le code.
  - [ ] Vérifier que la doc runtime ne décrit aucun comportement `66.39` non couvert par un test ciblé correspondant.

- [ ] Task 9: Validation locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .`.
  - [ ] Dans `backend/`, exécuter `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum la suite ciblée 66.38/66.39 et toute suite quality-gate impactée.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- 66.39 est une story de **hardening de fiabilité**, pas une nouvelle doctrine.
- Le danger principal est le comportement flaky entre local, CI, historique complet et historique partiel.
- Le point d’entrée doit rester unique : [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py).
- Le manifeste doit rester la seule vérité versionnée pour le périmètre et les motifs autorisés.
- La meilleure amélioration n’est pas “plus de règles”, mais des règles mieux testées, mieux diagnostiquées et mieux expliquées.

### Ce que le dev ne doit pas faire

- Ne pas créer une seconde CLI “debug” concurrente au script existant.
- Ne pas déplacer la doctrine dans le workflow GitHub ou dans les tests.
- Ne pas parser toute la doc ou tout le template PR avec des heuristiques narratives larges.
- Ne pas traiter un clone shallow ou un merge-base introuvable comme un cas silencieux.
- Ne pas utiliser `TEST_ONLY` ou `FIX_TYPO` comme échappatoire non gouvernée.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/doc_conformity_manifest.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/doc_conformity_manifest.py)
- [backend/app/llm_orchestration/services/doc_conformity_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/doc_conformity_validator.py)
- [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py)
- [backend/tests/integration/test_story_66_38_doc_conformity.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_38_doc_conformity.py)
- [.github/workflows/llm-doc-conformity.yml](/c:/dev/horoscope_front/.github/workflows/llm-doc-conformity.yml)
- [.github/pull_request_template.md](/c:/dev/horoscope_front/.github/pull_request_template.md)
- [scripts/quality-gate.ps1](/c:/dev/horoscope_front/scripts/quality-gate.ps1)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **66.26** a imposé la discipline documentaire et la référence de vérification manuelle.
- **66.31** a confirmé le pattern fail-fast sur des cohérences structurelles de runtime.
- **66.36** a déjà introduit un gate machine-readable dans le pipeline LLM.
- **66.38** a fermé la gouvernance doc ↔ code, mais en rendant le CLI et le calcul de changeset critiques pour la fiabilité quotidienne.
- Les commits récents sur 66.38 montrent déjà un cycle “feat puis hardening”, ce qui confirme que le prochain incrément logique est bien la robustesse multi-contexte et non une nouvelle extension doctrinale.

### Git Intelligence

Commits récents pertinents observés :

- `aa0d024b` : `fix(llm): harden story 66.38 diff and obs classification`
- `e61910fa` : `fix(llm): harden story 66.38 doc conformity gate`
- `deb8cc6f` : `feat(llm): add doc conformity gate for story 66.38`
- `a9b47518` : `refactor(llm): expand structural files manifest for doc conformity`
- `4a603c0a` : `refactor(llm): strengthen doc-to-code conformity and local quality gate (story 66.38)`

Signal utile :

- la zone 66.38 a déjà nécessité plusieurs passes correctives ;
- la dette résiduelle la plus probable est donc dans les cas limites Git/CI et les diagnostics ;
- 66.39 doit privilégier les tests opérationnels et la lisibilité de sortie plutôt qu’un nouveau refactor large.

### Testing Requirements

- Ajouter une matrice de tests du changeset couvrant au minimum :
  - structurant `unstaged`
  - structurant `staged`
  - structurant `untracked`
  - branche locale sans upstream valide
  - CI avec `DOC_CONFORMITY_BASE_REF`
  - clone shallow / historique insuffisant
- Ajouter les scénarios de bloc de preuve :
  - changement structurel sans modification du bloc
  - changement cosmétique seul
  - changement de date seule
  - changement de SHA seul
- Ajouter les scénarios PR :
  - body vide
  - section non renseignée
  - deux motifs cochés
  - motif inconnu
  - contradiction `OUI` / doc non modifiée
  - justification fournie alors que la doc a été mise à jour
- Ajouter des tests CLI `--json` qui valident le contrat minimal de sortie sans reparser la sortie texte.
- Ajouter des tests explicites sur `git_context.mode` pour au moins un cas nominal et un cas dégradé documenté.
- Ajouter des tests positifs et négatifs pour chaque motif PR autorisé, pas seulement des exemples représentatifs.
- Ajouter des tests lisibilité/normalisation des erreurs pour taxonomie, provider, fallback et `obs_snapshot`.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest -q tests/integration/test_story_66_38_doc_conformity.py`
  - ajouter et exécuter la suite dédiée 66.39 si elle est créée

### Project Structure Notes

- Travail concentré sur `backend/app/llm_orchestration/`, `backend/scripts/`, `backend/tests/integration/`, `.github/` et `docs/`.
- Éviter de déplacer la logique métier du validateur dans le workflow GitHub ; le workflow doit rester un simple appelant.
- Si une sortie JSON est ajoutée, la porter dans le script existant plutôt que dans un nouveau wrapper.

### References

- [66-38-controle-automatique-conformite-doc-code.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-38-controle-automatique-conformite-doc-code.md)
- [66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md)
- [66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md)
- [66-36-gating-de-non-regression-end-to-end-sur-golden-set-de-prompts-et-outputs.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-36-gating-de-non-regression-end-to-end-sur-golden-set-de-prompts-et-outputs.md)
- [backend/app/llm_orchestration/doc_conformity_manifest.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/doc_conformity_manifest.py)
- [backend/app/llm_orchestration/services/doc_conformity_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/doc_conformity_validator.py)
- [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py)
- [backend/tests/integration/test_story_66_38_doc_conformity.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_38_doc_conformity.py)
- [.github/workflows/llm-doc-conformity.yml](/c:/dev/horoscope_front/.github/workflows/llm-doc-conformity.yml)
- [.github/pull_request_template.md](/c:/dev/horoscope_front/.github/pull_request_template.md)
- [scripts/quality-gate.ps1](/c:/dev/horoscope_front/scripts/quality-gate.ps1)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [git-merge-base documentation](https://git-scm.com/docs/git-merge-base)
- [actions/checkout README](https://github.com/actions/checkout)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- 2026-04-14 : `check_doc_conformity.py` durci avec une résolution Git structurée, une sortie `--json`, et une exigence explicite de section PR sur changement structurel.
- 2026-04-14 : `DocConformityValidator` renforcé sur les messages doctrinaux et la sémantique des motifs PR autorisés.
- 2026-04-14 : nouvelle suite [backend/tests/integration/test_story_66_39_doc_conformity_hardening.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_39_doc_conformity_hardening.py) ajoutée pour couvrir unicité de la source de vérité, robustesse du bloc de preuve, `git_context.mode`, JSON machine-readable et validation sémantique des motifs.
- 2026-04-14 : [backend/tests/integration/test_story_66_38_doc_conformity.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_38_doc_conformity.py) et [backend/app/tests/integration/test_pipeline_scripts.py](/c:/dev/horoscope_front/backend/app/tests/integration/test_pipeline_scripts.py) réalignés sur le comportement effectif du gate documentaire.
- 2026-04-14 : validation ciblée exécutée dans le venv avec `ruff check` sur les fichiers du gate, `pytest -q tests/integration/test_story_66_38_doc_conformity.py tests/integration/test_story_66_39_doc_conformity_hardening.py` et `pytest -q app/tests/integration/test_pipeline_scripts.py -k "quality_gate_success_executes_all_steps_in_order or quality_gate_skips_canonical_db_cli_when_db_not_marked_ready"` ; résultats verts.
- 2026-04-14 : exécution réelle de `python backend/scripts/check_doc_conformity.py --json` confirmée ; la sortie JSON est conforme, et l’échec observé sur le worktree local provient bien de l’absence de body PR alors que des fichiers structurels sont modifiés.
- 2026-04-14 : passe documentaire complémentaire appliquée après durcissement runtime/tests du backend ; la doc de référence LLM a été réalignée sur la compatibilité `ProviderRuntimeManager` / `ResponsesClient`, l’isolation des états globaux de test (`circuit breakers`, caches registry), la clarification pratique de `OPERATIONAL_FIELDS` et le fallback no-op du scheduler FastAPI quand `apscheduler` n’est pas importable.

### File List

- `_bmad-output/implementation-artifacts/66-39-durcissement-fiabilite-multi-contexte-gate-conformite-documentaire.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/llm_orchestration/services/doc_conformity_validator.py`
- `backend/app/tests/integration/test_pipeline_scripts.py`
- `backend/scripts/check_doc_conformity.py`
- `backend/tests/integration/test_story_66_38_doc_conformity.py`
- `backend/tests/integration/test_story_66_39_doc_conformity_hardening.py`
- `docs/llm-prompt-generation-by-feature.md`
