# Story 66.16 : Créer une matrice d'évaluation systématique

Status: ready-for-dev

## Story

En tant qu'**architecte qualité / responsable plateforme LLM**,
je veux **une infrastructure de tests d'évaluation paramétrés couvrant la matrice feature × plan × astrologue × context_quality**,
afin de **pouvoir détecter toute régression sur le contrat de sortie, la longueur, les placeholders résolus et l'influence stylistique, dès qu'une modification est apportée au système de composition**.

## Intent

Dès que le système permet des variations sur plusieurs axes (feature, plan, astrologue, moteur, context_quality), la probabilité d'introduire une régression silencieuse augmente. Sans matrice de tests, une modification d'un plan_rules peut casser un contrat de sortie sur une autre combinaison sans qu'on le sache.

La matrice minimale recommandée :
- **4 features :** `chat`, `guidance`, `natal`, `horoscope_daily`
- **3 plans :** `free`, `basic`, `premium`
- **2 profils astrologue :** un profil "synthétique" et un profil "ample" (profils contrastés)
- **3 niveaux context_quality :** `full`, `partial`, `minimal`

Chaque cellule de la matrice vérifie :
1. **Contrat de sortie :** la réponse respecte le schéma attendu (si output_contract défini)
2. **Longueur :** la réponse respecte le budget de longueur (si `LengthBudget` défini)
3. **Placeholders résolus :** aucun `{{...}}` dans le prompt final envoyé
4. **Influence stylistique :** la persona détectée influence le ton (vérification heuristique)
5. **Différence plan sans dérive logique métier :** free vs premium diffèrent sur la longueur/profondeur, pas sur la structure métier

Cette story ne vise pas à lancer des appels LLM réels en CI par défaut. L'évaluation porte sur :
- La **résolution du prompt** (prompt renderer + assembly) — testable sans LLM.
- L'**output post-LLM** — testable via fixtures de réponses LLM préenregistrées.

## Décisions d'architecture

**D1 — L'infrastructure d'évaluation est séparée des tests unitaires.** Elle vit dans `backend/tests/evaluation/` et est taggée `@pytest.mark.evaluation` pour être exécutée optionnellement (pas par défaut dans le pipeline CI standard).

**D2 — Les fixtures LLM sont des réponses préenregistrées.** Pour les tests de contrat de sortie et d'influence stylistique, les réponses LLM sont mockes avec des fixtures JSON réalistes. Les tests ne font pas de vrais appels au provider en CI.

**D3 — La matrice est définie dans un fichier de configuration `evaluation_matrix.yaml`.** Chaque ligne de la matrice est une combinaison testée avec ses attendus (schéma attendu, budget de longueur attendu, etc.).

**D4 — Un rapport d'évaluation est généré** sous forme de tableau markdown ou JSON après exécution, montrant le statut de chaque cellule de la matrice.

**D5 — Les tests de résolution de prompt ne nécessitent pas de LLM.** `PromptRenderer.render()` est appelé directement avec les fixtures de contexte. C'est la partie la plus critique à couvrir.

## Acceptance Criteria

1. **Given** que la matrice d'évaluation est configurée dans `backend/tests/evaluation/evaluation_matrix.yaml`
   **When** les tests d'évaluation sont exécutés (`pytest -m evaluation`)
   **Then** chaque combinaison (feature × plan × astrologue × context_quality) dans la matrice produit un résultat pass/fail pour les 5 dimensions vérifiées

2. **Given** un test de résolution de prompt pour `feature=natal, plan=premium, context_quality=full, astrologue=synthétique`
   **When** le test est exécuté
   **Then** le prompt résolu ne contient aucun `{{...}}`, respecte le budget de longueur défini, et la version `premium` est plus longue/riche que la version `free`

3. **Given** un test de contrat de sortie avec fixture LLM préenregistrée
   **When** la réponse fixture est validée contre le `output_contract` de la feature
   **Then** la validation Pydantic passe — si elle échoue, le test échoue avec un message clair indiquant quel champ ne respecte pas le contrat

4. **Given** deux profils astrologue contrastés (synthétique vs ample)
   **When** les prompts résolus pour les deux profils sont comparés sur la même combinaison feature/plan/context_quality
   **Then** le test détecte une différence dans le bloc persona injecté — si les blocs sont identiques, le test échoue (signalant que les personas ne sont pas suffisamment contrastées)
   **Note :** ce test valide une **différenciation structurelle de l'entrée** (les blocs persona sont différents), pas la qualité stylistique de la sortie LLM. Il ne garantit pas que l'astrologue A est réellement plus synthétique que B dans la réponse générée — cette validation sémantique n'est pas possible sans appel LLM réel et est hors scope des tests CI automatiques.

5. **Given** que `context_quality=minimal` est simulé
   **When** le test vérifie le developer_prompt résolu
   **Then** l'instruction de compensation `context_quality` est présente dans le prompt (story 66.14 — si implémentée)

6. **Given** qu'un rapport d'évaluation est généré après exécution
   **When** le développeur consulte le rapport
   **Then** il voit un tableau avec colonnes : `feature | plan | astrologue | context_quality | contrat_sortie | longueur | placeholders | persona_influence | differentiation_plan` et le statut (✅/❌/⚠️) pour chaque cellule

7. **Given** qu'une modification est apportée à un `plan_rules` ou à un template feature
   **When** les tests d'évaluation sont relancés
   **Then** toute régression sur une cellule précédemment passante est détectée et rapportée avec le contexte de la combinaison affectée

## Tasks / Subtasks

- [ ] Créer l'infrastructure d'évaluation (AC: 1, 6)
  - [ ] Créer `backend/tests/evaluation/` avec `__init__.py`
  - [ ] Créer `backend/tests/evaluation/evaluation_matrix.yaml` : liste des combinaisons à tester, attendus par dimension
  - [ ] Créer `backend/tests/evaluation/conftest.py` : fixtures de contexte par niveau (full/partial/minimal), fixtures de profils astrologue
  - [ ] Créer `backend/tests/evaluation/fixtures/` : réponses LLM préenregistrées par feature (JSON)
  - [ ] Configurer le marker pytest `@pytest.mark.evaluation` dans `backend/pyproject.toml`

- [ ] Implémenter les tests de résolution de prompt (AC: 2, 5)
  - [ ] Créer `backend/tests/evaluation/test_prompt_resolution.py`
  - [ ] Test paramétré sur la matrice : pour chaque combinaison, appeler `assembly_resolver.resolve_assembly()` + `PromptRenderer.render()` et vérifier :
    - Absence de `{{...}}` dans le prompt résolu
    - Présence de l'instruction context_quality si applicable
    - Longueur estimée (compte de tokens approximatif) dans les bornes du `LengthBudget`

- [ ] Implémenter les tests de contrat de sortie (AC: 3)
  - [ ] Créer `backend/tests/evaluation/test_output_contract.py`
  - [ ] Pour chaque feature avec `output_contract`, charger la fixture de réponse LLM et valider avec le schéma Pydantic correspondant

- [ ] Implémenter les tests de différenciation plan et persona (AC: 2, 4)
  - [ ] Créer `backend/tests/evaluation/test_differentiation.py`
  - [ ] Test : comparer `rendered_developer_prompt` pour `plan=free` vs `plan=premium` — asserter que la version premium est plus longue ou contient le bloc plan_rules premium
  - [ ] Test : comparer le bloc persona injecté pour astrologue synthétique vs ample — asserter que les blocs diffèrent

- [ ] Implémenter le générateur de rapport (AC: 6)
  - [ ] Créer `backend/tests/evaluation/report_generator.py` : parcourt les résultats pytest et génère un tableau markdown
  - [ ] Ajouter un hook pytest ou un script `generate_eval_report.py` à exécuter après les tests

- [ ] Créer les fixtures de profils astrologue de test (AC: 4)
  - [ ] Créer deux personas de test contrastées dans `backend/tests/evaluation/fixtures/personas/` : `synthétique.json` et `ample.json`
  - [ ] Ces personas doivent être utilisées dans la matrice d'évaluation sans polluer les personas de production

- [ ] Tests de la matrice sur les familles prioritaires (AC: 1, 7)
  - [ ] Implémenter la couverture pour les familles `guidance`, `natal`, `chat` (migrées en story 66.15)
  - [ ] Implémenter une couverture partielle pour `horoscope_daily` (chemin use_case-first — résolution de prompt uniquement)

## Dev Notes

- **Structure de répertoires :**
  ```
  backend/tests/evaluation/
  ├── __init__.py
  ├── conftest.py
  ├── evaluation_matrix.yaml
  ├── report_generator.py
  ├── test_prompt_resolution.py
  ├── test_output_contract.py
  ├── test_differentiation.py
  └── fixtures/
      ├── personas/
      │   ├── synthetique.json
      │   └── ample.json
      └── llm_responses/
          ├── natal_premium_full.json
          └── ...
  ```

- **Pas de vrais appels LLM en CI.** Les tests de résolution de prompt sont purement locaux. Les tests de contrat de sortie utilisent des fixtures JSON préenregistrées. Un mode `--live` optionnel peut être ajouté pour les tests manuels avec vrais appels.

- **Dépendances :** Cette story est la plus efficace après 66.13 (placeholders), 66.12 (budgets), 66.14 (context_quality), 66.15 (migration assembly). Elle peut néanmoins être démarrée partiellement avant.

- **Résolution d'ambiguïté :** "influence stylistique correcte de l'astrologue" est vérifiée de façon structurelle (blocs persona différents), pas sémantique (pas de LLM judge en CI par défaut).

### References

- [Source: docs/llm-prompt-generation-by-feature.md]
- [Source: backend/app/llm_orchestration/services/assembly_resolver.py]
- [Source: backend/app/prompts/prompt_renderer.py]
- [Source: backend/pyproject.toml — configuration pytest]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
