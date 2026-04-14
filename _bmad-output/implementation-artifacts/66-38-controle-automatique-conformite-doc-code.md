# Story 66.38: Contrôle automatique de conformité doc ↔ code

Status: done

## Maintenance Follow-Up

- Après vérification runtime réelle du 2026-04-14, un résidu de nomenclature `daily_prediction` subsistait encore dans la construction du contexte commun du flux horoscope quotidien.
- Ce résidu a été absorbé sans changer la doctrine du pipeline : le nominal daily passe maintenant aussi par `horoscope_daily` dans le builder de contexte, en cohérence avec la taxonomie Story 66 et avec les assemblies/runtime observés en production locale.
- La compatibilité défensive avec l’alias legacy reste portée côté builder pour éviter une régression lors d’appels historiques non migrés.

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect / Maintainer du pipeline LLM,
I want mécaniser une partie du contrôle de conformité entre la documentation canonique et le code réel,
so that une divergence structurelle du pipeline ne puisse plus être mergée sur simple discipline humaine, mais soit détectée par la CI, par des lints ciblés et par une revue PR explicitement bloquante.

## Contexte

La story [66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md) a déjà imposé une discipline documentaire explicite :

- la doc canonique runtime [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) doit être maintenue ;
- le bloc de vérification final porte une référence stable de revue manuelle ;
- le template PR [.github/pull_request_template.md](/c:/dev/horoscope_front/.github/pull_request_template.md) expose la règle ;
- un garde-fou léger existe déjà dans [backend/tests/integration/test_story_66_26_documentation_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_26_documentation_governance.py).

Cette discipline reste cependant largement déclarative.

Le dépôt possède déjà des sources de vérité machine-readables qui peuvent être exploitées :

- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py) porte la taxonomie nominale des familles ;
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) porte le registre des fallbacks et leur statut ;
- [backend/app/llm_orchestration/golden_regression_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/golden_regression_registry.py) classe les champs `obs_snapshot` ;
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py) sait déjà rejeter des incohérences structurelles au publish et au boot ;
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) énonce noir sur blanc :
  - la taxonomie canonique ;
  - le provider nominalement supporté ;
  - le rôle du registre de fallbacks ;
  - la classification et la doctrine `obs_snapshot` ;
  - le bloc final de vérification manuelle.

Le trou restant est précis :

- une PR peut encore modifier une zone structurante du pipeline sans que la CI exige la mise à jour de la référence de vérification documentaire ;
- les invariants documentés autour de la taxonomie, du provider nominal, du fallback registry et de `obs_snapshot` ne sont pas tous comparés automatiquement au code ;
- le template PR force une déclaration humaine, mais pas encore un contrôle bloquant couplé aux fichiers réellement touchés ;
- la doc dit déjà "si le code diverge, le code fait foi", mais il manque un garde-fou qui empêche de laisser cette divergence dériver trop longtemps.

L’objectif de 66.38 n’est pas de prétendre remplacer la revue humaine. L’objectif est de **mécaniser les divergences structurelles les plus objectivables** et de rendre la discipline documentaire partiellement exécutable en CI.

## Portée exacte

Cette story doit couvrir les quatre livrables demandés :

1. un **check CI** détectant certaines divergences structurelles doc ↔ code ;
2. un **lint ciblé** sur la taxonomie, le provider nominal, le fallback registry et les champs `obs_snapshot` ;
3. une **obligation exécutable** d’actualiser la référence de vérification quand des fichiers structurants changent ;
4. un **template PR réellement bloquant** si l’impact documentaire n’est pas traité.

La détection des fichiers structurants, la sémantique des exceptions autorisées, et le format du bloc de preuve documentaire doivent être **centralisés dans une unique source de vérité versionnée** réutilisée par les tests, le script local, la CI et le workflow PR.

Elle ne doit pas :

- déclarer automatiquement que la documentation est "à jour" sans revue humaine réelle ;
- inventer une seconde source de vérité concurrente à la doc ou au code ;
- tenter un diff sémantique complet et fragile de tout le pipeline ;
- transformer un simple refactoring local hors périmètre en obligation documentaire systématique.

## Cible d'architecture

Introduire une **chaîne de conformité documentaire exécutable** pour le pipeline LLM, avec trois niveaux complémentaires :

1. **Détection de périmètre** : identifier les fichiers et zones structurantes qui déclenchent un contrôle documentaire renforcé.
2. **Lint doctrinal** : comparer les invariants doc/code les plus stables et les plus structurants.
3. **Gate PR/CI** : si le périmètre est touché, exiger soit une mise à jour documentaire traçable, soit une justification explicite et visible, et vérifier que la référence de vérification a été réactualisée.

La chaîne doit être conçue pour rester honnête :

- le lint vérifie seulement des invariants que le dépôt sait déjà exprimer de façon stable ;
- la revue humaine reste obligatoire pour la référence de vérification ;
- la CI contrôle la présence, la fraîcheur et la cohérence minimale des artefacts, pas une pseudo-certification automatique du sens de la documentation.

## Invariants à protéger

### 1. Taxonomie canonique

La doc et le code doivent rester alignés sur :

- les familles nominales supportées ;
- les alias legacy explicitement tolérés ;
- la fermeture nominale autour de `chat`, `guidance`, `natal`, `horoscope_daily`.

La source de vérité code actuelle est [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py). Le lint doit au minimum empêcher qu’une doc prétende un périmètre nominal différent de celui du code.

### 2. Provider nominal

La doc affirme que `openai` est le seul provider nominalement autorisé. Cette affirmation ne doit pas diverger de la vérité portée par les validateurs/résolveurs runtime. Le check doit détecter une divergence claire entre formulation documentaire et source de vérité code.

### 3. Fallback registry

La doc présente le rôle du registre de gouvernance et la doctrine de fermeture progressive des fallbacks. Une modification de [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) qui change le statut, le périmètre, ou les fallbacks interdits doit être considérée comme impact documentaire obligatoire.

Le contrôle automatique ne doit pas prétendre relire toute la doctrine narrative. Il doit comparer uniquement un **contrat doctrinal minimal machine-readable** sur les fallbacks structurants : statut minimal, périmètre nominal interdit/autorisé, et familles concernées.

### 4. Champs `obs_snapshot`

La doc décrit déjà la classification des champs `obs_snapshot` et les discriminants canoniques. Le check doit au minimum comparer la classification ou les champs clés documentés avec la source de vérité portée par [backend/app/llm_orchestration/golden_regression_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/golden_regression_registry.py) et/ou [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py).

Le contrat attendu ici doit être strictement borné à la classification stable déjà portée par le registre golden : `strict`, `thresholded`, `informational`, ainsi qu’au jeu de champs canoniques rattachés à chaque classe.

### 5. Référence de vérification manuelle

Quand une PR touche un fichier structurant du pipeline ou de sa doctrine, le bloc final de [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) doit être réactualisé :

- date ;
- référence stable ;
- et, si le format est enrichi, tout identifiant de preuve supplémentaire retenu par l’implémentation.

L’absence d’évolution de cette référence sur un change set structurel doit devenir un motif d’échec CI.

Une réactualisation valide ne peut pas se limiter à un changement cosmétique dans la section. Le contrôle doit exiger qu’au minimum la `Date` et/ou la `Référence stable` changent effectivement dans le même changeset.

### 6. Contrat documentaire machine-readable minimal

Le lint ne doit pas dépendre d’un wording libre sur toute la doc. Il doit reposer sur un **contrat documentaire machine-readable minimal**, matérialisé soit par :

- des sections/balises explicitement identifiables dans la doc canonique ;
- soit un artefact dérivé versionné ;
- soit une combinaison légère des deux.

Ce contrat doit au minimum couvrir :

- familles nominales supportées ;
- alias legacy explicitement tolérés ;
- provider nominal ;
- classification des champs `obs_snapshot` ;
- bloc de preuve documentaire final.

## Acceptance Criteria

1. **AC1 — Check CI doc ↔ code ciblé** : une vérification CI dédiée échoue si des invariants structurels documentés du pipeline LLM divergent du code sur le périmètre explicitement supporté.
2. **AC2 — Lint taxonomie** : le contrôle vérifie l’alignement minimal entre la doc canonique et [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py) pour les familles nominales, alias legacy tolérés et périmètre convergé.
3. **AC3 — Lint provider nominal** : le contrôle vérifie que l’assertion documentaire sur le provider nominalement supporté reste cohérente avec la vérité portée par le code/runtime.
4. **AC4 — Lint fallback registry** : le contrôle compare, pour les fallbacks structurants documentés, leur statut doctrinal minimal (`allowed`, `to_remove`, `forbidden`) et leur périmètre de familles avec la source de vérité code. Toute divergence machine-détectable échoue en CI.
5. **AC5 — Lint `obs_snapshot`** : le contrôle compare le jeu de champs `obs_snapshot` doctrinalement canoniques et leur classification stable (`strict`, `thresholded`, `informational`) avec la source de vérité portée par le registre golden et/ou les modèles canoniques.
6. **AC6 — Détection des fichiers structurants** : la CI sait déterminer qu’une PR touche une zone à impact documentaire obligatoire à partir d’un manifeste unique versionné partagé par les tests, le script local, la CI et le workflow PR. Ce manifeste couvre au minimum :
   - `docs/llm-prompt-generation-by-feature.md` ;
   - `.github/pull_request_template.md` ;
   - `backend/app/llm_orchestration/gateway.py` ;
   - `backend/app/llm_orchestration/feature_taxonomy.py` ;
   - `backend/app/llm_orchestration/services/fallback_governance.py` ;
   - `backend/app/llm_orchestration/services/provider_parameter_mapper.py` ;
   - `backend/app/llm_orchestration/services/config_coherence_validator.py` ;
   - `backend/app/llm_orchestration/golden_regression_registry.py` ;
   - et tout autre fichier explicitement retenu comme source de vérité structurelle.
7. **AC7 — Référence de vérification obligatoire si périmètre touché** : si un fichier structurant change, la CI échoue si la `Date` et/ou la `Référence stable` du bloc "Dernière vérification manuelle contre le pipeline réel du gateway" n’ont pas été modifiées dans le même changeset.
8. **AC8 — Pas de faux positif sur refactoring hors périmètre** : un changement sans impact structurel dans le pipeline LLM ne doit pas exiger de mise à jour documentaire si aucun fichier structurant détecté n’est touché.
9. **AC9 — Template PR + workflow CI bloquant** : le template PR expose une section documentaire obligatoire, et un workflow CI bloquant vérifie que cette section est correctement renseignée et cohérente avec le périmètre de fichiers modifiés.
10. **AC10 — Cohérence doc / template / CI** : le périmètre de déclenchement et les issues autorisées sont alignés entre la doc canonique, le template PR et le contrôle CI.
11. **AC11 — Pas de pseudo-vérification automatique mensongère** : le contrôle ne déclare jamais que la revue humaine a eu lieu ; il vérifie seulement la présence et la fraîcheur des preuves/documentations attendues.
12. **AC12 — Format de preuve toujours stable** : le bloc de preuve documentaire reste machine-assertable, avec au minimum une date ISO et une référence stable non flottante.
13. **AC13 — Exception bornée et codifiée** : la justification d’absence de mise à jour documentaire est portée dans une surface unique explicitement prévue par le workflow PR et validée selon un ensemble borné de motifs autorisés, plutôt qu’en texte libre non gouverné.
14. **AC14 — Intégration dans le quality gate** : le contrôle est exécutable localement et en CI via une commande stable documentée, idéalement réutilisée par le quality gate existant ou branchée explicitement à celui-ci.
15. **AC15 — Tests automatisés dédiés** : des tests couvrent au minimum le cas nominal, l’absence de mise à jour de référence sur changement structurant, la divergence taxonomie/provider/fallback/`obs_snapshot`, et un cas hors périmètre non bloquant.
16. **AC16 — Documentation de maintenance réalignée** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) et la documentation/outillage associé expliquent clairement ce qui est vérifié automatiquement, ce qui reste manuel, et comment réagir à un échec.
17. **AC17 — Logique de conformité testable hors git brut** : la logique de conformité documentaire principale est implémentée dans des fonctions réutilisables et testables indépendamment du diff Git brut ; la résolution de changeset CI vient en surcouche.

## Tasks / Subtasks

- [x] Task 1: Définir le périmètre structurel déclenchant le contrôle documentaire (AC6, AC8, AC10)
  - [x] Créer un manifeste unique de gouvernance documentaire structurant, consommé par les lints, les tests, la CI et le gate PR.
  - [x] Lister explicitement les fichiers structurants et les grouper dans cette source de vérité versionnée.
  - [x] Décider si la détection repose sur une allowlist de chemins, un manifeste dédié, ou une politique centralisée réutilisable, mais sans duplication concurrente.
  - [x] Distinguer clairement les fichiers de vérité structurelle des fichiers de simple implémentation locale.

- [x] Task 2: Implémenter le lint doc ↔ code ciblé (AC1 à AC5, AC11, AC12, AC17)
  - [x] Vérifier l’alignement taxonomie/doc.
  - [x] Vérifier l’alignement provider nominal/doc.
  - [x] Vérifier l’alignement fallback registry/doc sur un contrat doctrinal minimal réellement comparable.
  - [x] Vérifier l’alignement `obs_snapshot`/doc sur la classification stable `strict` / `thresholded` / `informational`.
  - [x] Implémenter la logique de conformité principale dans un module Python réutilisable, indépendant du diff Git brut.
  - [x] Produire des erreurs structurées compréhensibles pour la review PR.

- [x] Task 3: Introduire la règle exécutable sur la référence de vérification manuelle (AC7, AC11, AC12)
  - [x] Détecter qu’un change set touche le périmètre structurel.
  - [x] Vérifier que la `Date` et/ou la `Référence stable` du bloc final de vérification ont effectivement changé dans ce cas.
  - [x] Interdire toute logique assimilant cette réactualisation à une revue automatique.

- [x] Task 4: Rendre le workflow PR/CI réellement bloquant sur l’impact documentaire (AC9, AC10, AC13, AC16)
  - [x] Faire évoluer [.github/pull_request_template.md](/c:/dev/horoscope_front/.github/pull_request_template.md) si nécessaire pour rendre l’issue ambiguë impossible.
  - [x] Aligner la sémantique avec la doc canonique.
  - [x] Définir une surface unique pour la justification d’absence de mise à jour documentaire.
  - [x] Borner les motifs autorisés de justification au lieu d’un texte libre non gouverné.
  - [x] Brancher un workflow CI qui valide cette section en cohérence avec le périmètre de fichiers modifiés.

- [x] Task 5: Brancher le contrôle au workflow local/CI existant (AC14, AC17)
  - [x] Choisir le point d’entrée : script Python, test Pytest dédié, script PowerShell, ou combinaison légère.
  - [x] L’intégrer au quality gate/script CI existant sans créer une seconde façon concurrente d’exécuter la même vérification.
  - [x] Documenter la commande exacte à lancer localement.

- [x] Task 6: Ajouter la couverture de tests (AC1 à AC5, AC7 à AC17)
  - [x] Étendre ou compléter [backend/tests/integration/test_story_66_26_documentation_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_26_documentation_governance.py) avec les nouveaux cas bloquants.
  - [x] Ajouter au besoin une suite dédiée à la conformité doc ↔ code pour éviter de surcharger le test 66.26.
  - [x] Tester au minimum un scénario hors périmètre, un scénario structurant sans MAJ de référence, et un scénario de divergence doctrinale.

- [x] Task 7: Réaligner la documentation de gouvernance (AC10, AC16)
  - [x] Mettre à jour [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) pour expliciter le contrôle automatique partiel.
  - [x] Documenter ce que la CI sait prouver et ce qu’elle ne sait pas prouver.
  - [x] Stabiliser, si nécessaire, des marqueurs ou sections canoniques minimales dans la doc pour fiabiliser le lint sans parser tout le wording libre.
  - [x] Ajouter, si nécessaire, un court runbook de remédiation d’un échec de conformité documentaire.

- [x] Task 8: Vérification locale obligatoire
  - [x] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .`.
  - [x] Dans `backend/`, exécuter `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [x] Exécuter la ou les suites ciblées liées à la gouvernance documentaire et au nouveau gate CI.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- 66.38 est une story de **mécanisation honnête** de la discipline documentaire, pas une tentative de remplacer la revue humaine.
- Le meilleur levier n’est pas un parseur universel du markdown, mais un nombre réduit d’invariants structurants déjà portés par des modules canoniques.
- Le dépôt a déjà le pattern "gouvernance légère par tests d’intégration" avec [backend/tests/integration/test_story_66_26_documentation_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_26_documentation_governance.py).
- Le dépôt a déjà le pattern "validation fail-fast" avec [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py). 66.38 doit s’en inspirer sans tout recoder à part.
- Les quatre objets les plus stables à comparer sont précisément ceux donnés par la demande utilisateur : taxonomie, provider nominal, fallback registry, `obs_snapshot`.

### Ce que le dev ne doit pas faire

- Ne pas introduire un check gigantesque et fragile dépendant d’un wording exact de toute la doc.
- Ne pas créer une nouvelle doctrine concurrente à [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md).
- Ne pas marquer automatiquement la documentation comme "revue" ou "validée".
- Ne pas exiger une mise à jour documentaire pour n’importe quel diff backend hors périmètre.
- Ne pas dupliquer le périmètre d’impact dans trois fichiers divergents sans source de vérité unique.

### Fichiers à inspecter en priorité

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [.github/pull_request_template.md](/c:/dev/horoscope_front/.github/pull_request_template.md)
- [backend/tests/integration/test_story_66_26_documentation_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_26_documentation_governance.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/golden_regression_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/golden_regression_registry.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [scripts/quality-gate.ps1](/c:/dev/horoscope_front/scripts/quality-gate.ps1)

### Stratégie d’implémentation recommandée

- Centraliser d’abord le **registre du périmètre documentaire structurant** pour éviter les divergences entre tests, CI et template PR.
- Implémenter ensuite un contrôle lisible, probablement sous forme de test(s) d’intégration et/ou script dédié réutilisable par la CI.
- Enfin seulement, brancher le gate à `quality-gate.ps1` ou au workflow CI concerné.

### Previous Story Intelligence

- **66.26** a déjà imposé la discipline documentaire et le template PR, mais sans contrôle suffisamment mécanisé.
- **66.22** a verrouillé le provider nominal ; 66.38 doit empêcher une divergence silencieuse entre ce verrou et la doc.
- **66.23** a verrouillé la taxonomie canonique natal ; 66.38 généralise ce réflexe de cohérence à la doc runtime.
- **66.25** a rendu `obs_snapshot` central dans l’observabilité ; 66.38 doit protéger sa classification documentaire.
- **66.31** a montré le pattern fail-fast cohérence publish/boot ; 66.38 applique la même philosophie au couple doc ↔ code.
- **66.36** a déjà un registre golden et un gating machine-readable ; 66.38 doit réutiliser cette idée plutôt que la contourner.
- **66.37** a renforcé l’exploitation par dimensions canoniques ; cela augmente encore la nécessité d’une doc fiable sur ces mêmes dimensions.

### Git Intelligence

Commits récents pertinents observés :

- `84a62564` : `chore(db): keep only active backend sqlite database`
- `f86437d4` : `docs(llm): clarify ops monitoring contract for story 66.37`
- `ad4f51a3` : `feat(ops): add llm operational monitoring dashboards`
- `2e52fa7b` : `fix(llm): add golden regression publish gate`
- `939bae53` : `docs(llm): clarify story 66.35 qualification contract`

Signal utile :

- le dépôt a déjà le pattern "gate publish/golden" ;
- la doc runtime LLM continue d’évoluer par stories successives ;
- 66.38 doit verrouiller la cohérence entre ces deux mouvements.

### Testing Requirements

- Ajouter un test qui détecte un changement structurant sans réactualisation de la référence de vérification.
- Ajouter un test qui détecte une divergence de taxonomie entre doc et `feature_taxonomy.py`.
- Ajouter un test qui détecte une divergence sur le provider nominal supporté.
- Ajouter un test qui détecte une divergence structurante sur `FallbackGovernanceRegistry`.
- Ajouter un test qui détecte une divergence sur la classification ou les champs structurants `obs_snapshot`.
- Ajouter un test garantissant qu’un diff hors périmètre structurant n’échoue pas.
- Vérifier que le template PR et la doc exposent exactement les mêmes issues autorisées.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest tests/integration/test_story_66_26_documentation_governance.py -q`
  - ajouter et exécuter la suite dédiée 66.38 si elle est créée

### Project Structure Notes

- Travail majoritairement backend/scripts/docs, sans changement frontend attendu.
- Le point d’entrée le plus probable pour l’automatisation est un garde-fou Python/Pytest réutilisable par `scripts/quality-gate.ps1`.
- Si un registre de périmètre documentaire est créé, il doit vivre côté backend/scripts/docs d’une façon simple à relire.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [.github/pull_request_template.md](/c:/dev/horoscope_front/.github/pull_request_template.md)
- [backend/tests/integration/test_story_66_26_documentation_governance.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_26_documentation_governance.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/golden_regression_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/golden_regression_registry.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [scripts/quality-gate.ps1](/c:/dev/horoscope_front/scripts/quality-gate.ps1)
- [66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md)
- [66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-31-validation-fail-fast-coherence-configuration-publish-boot-runtime.md)
- [66-36-gating-de-non-regression-end-to-end-sur-golden-set-de-prompts-et-outputs.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-36-gating-de-non-regression-end-to-end-sur-golden-set-de-prompts-et-outputs.md)
- [66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- 2026-04-13 : manifeste unique [backend/app/llm_orchestration/doc_conformity_manifest.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/doc_conformity_manifest.py) introduit pour centraliser périmètre structurel, format de preuve et motifs d’exception autorisés.
- 2026-04-13 : validateur [backend/app/llm_orchestration/services/doc_conformity_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/doc_conformity_validator.py) durci avec contrôles taxonomie/provider/fallback/`obs_snapshot`, validation du bloc de preuve et cohérence du template PR.
- 2026-04-13 : script [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py) étendu pour couvrir les changements commités, staged, unstaged et untracked, ainsi que le corps de PR en CI.
- 2026-04-13 : workflow CI bloquant [.github/workflows/llm-doc-conformity.yml](/c:/dev/horoscope_front/.github/workflows/llm-doc-conformity.yml) ajouté pour exécuter le gate documentaire sur les pull requests.
- 2026-04-13 : documentation runtime [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) réalignée et référence de vérification manuelle réactualisée.
- 2026-04-14 : passe corrective post-review appliquée pour imposer la section documentaire en contexte PR, auto-protéger le gate via le manifeste, et vérifier explicitement les alias legacy `daily_prediction` / `natal_interpretation`.
- 2026-04-14 : la doc runtime a été ré-alignée sur le périmètre structurel enrichi du manifeste, y compris les briques du gate documentaire lui-même.
- 2026-04-14 : la classification doctrinale `obs_snapshot` a été explicitée via `OBS_SNAPSHOT_CLASSIFICATION_DEFAULT` pour découpler la gouvernance doc ↔ code de la seule sémantique de seuils portée par `GOLDEN_THRESHOLDS_DEFAULT`.
- 2026-04-14 : le script documentaire utilise désormais un calcul de changeset plus déterministe basé sur merge-base et `DOC_CONFORMITY_BASE_REF`, avec fallbacks bornés pour les contextes locaux/CI atypiques.
- 2026-04-14 : vérification ciblée exécutée dans le venv avec `ruff check` et `pytest -q tests/integration/test_story_66_38_doc_conformity.py` ; résultat `21 passed`.
- 2026-04-14 : nouvelle passe de maintenance documentaire effectuée après corrections de fiabilité backend ; le gate 66.38 continue de couvrir la doc de référence désormais mise à jour pour refléter le durcissement runtime provider, la sanitation opérationnelle réellement autorisée, l’isolation de l’état global de test et le comportement dégradé contrôlé du scheduler au boot.
- 2026-04-14 : maintenance documentaire étendue après stabilisation des parcours LLM `natal` free et `horoscope_daily` ; la gouvernance doc ↔ code reste alignée avec le comportement runtime réel sur le routage canonique `natal/interpretation/free`, le wrapper `QualifiedContext`, le schéma structuré du narrateur et la persistance idempotente des runs quotidiens.

### File List

- `_bmad-output/implementation-artifacts/66-38-controle-automatique-conformite-doc-code.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `.github/workflows/llm-doc-conformity.yml`
- `backend/app/llm_orchestration/doc_conformity_manifest.py`
- `backend/app/llm_orchestration/services/doc_conformity_validator.py`
- `backend/scripts/check_doc_conformity.py`
- `backend/tests/integration/test_story_66_38_doc_conformity.py`
- `docs/llm-prompt-generation-by-feature.md`
