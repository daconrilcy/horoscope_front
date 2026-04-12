# Architecture de Composition LLM (Canonique)

Ce document définit les responsabilités de chaque entité du pipeline de composition LLM. Il sert de source de vérité officielle pour tout développeur intervenant sur l'IA.

## 1. Doctrine de responsabilité exclusive

Chaque couche a une responsabilité unique. Ne mélangez pas les préoccupations.

| Entité | Responsabilité exclusive | Source de vérité |
|---|---|---|
| **PromptAssemblyConfig** | **Sélection et Composition** : détermine quelle config s'applique, quels blocs sont actifs et dans quel ordre. | Table `llm_assembly_configs` |
| **LlmPromptVersionModel** | **Contenu des Blocs** : le texte brut des templates métier, sous-features et règles de plan. | Table `llm_prompt_versions` |
| **LlmPersonaModel** | **Style et Voix** : ton, vocabulaire, empathie, densité stylistique. | Table `llm_personas` |
| **ExecutionProfile** | **Paramètres techniques** : choix du moteur (provider, modèle), raisonnement, verbosité technique. | Table `llm_execution_profiles` |
| **ResolvedExecutionPlan** | **Vérité finale immuable** : l'agrégation de toutes les couches à l'instant T de l'exécution. | Objet Python (frozen) |
| **ProviderRuntimeManager** | **Robustesse Opérationnelle** : gestion des retries, circuit breaking et rate limits. | Code applicatif |

## 2. Règles de décision : "Où mettre mon instruction ?"

- **C'est une règle métier immuable ?** -> Template de feature (`LlmPromptVersionModel`).
- **C'est une variation liée à l'abonnement ?** -> `plan_rules` dans l'assembly.
- **C'est une variation de style d'astrologue ?** -> Persona (`LlmPersonaModel`).
- **C'est une instruction de format (JSON) ?** -> Schéma de sortie (`output_contract_ref`).
- **C'est un choix de modèle (ex: o1 vs gpt-4o) ?** -> Profil d'exécution (`ExecutionProfile`).

## 3. Violations fréquentes (détectées par lint)

| Violation | Exemple à éviter | Action corrective |
|---|---|---|
| **Execution in Template** | "Réponds en utilisant le modèle gpt-4." | Supprimer du texte, configurer l'ExecutionProfile. |
| **Contract in Persona** | "Ta réponse doit être un JSON valide." | Supprimer de la persona, utiliser `output_contract_ref`. |
| **Feature Logic in Plan** | "Si premium, analyse aussi les transits." | Utiliser deux templates distincts ou des blocs conditionnels. |

## 4. Ordre de résolution (Gateway)

La transformation du prompt suit un ordre séquentiel strict. Les étapes 2 et 3 sont des mutations textuelles opérées par le Gateway avant l'appel final au moteur de rendu.

1. **Qualification du contexte** (`CommonContextBuilder`)
2. **Résolution de l'Assembly** (Sélection des IDs et activation des flags)
3. **Résolution du Profil d'Exécution** (Choix du moteur et paramètres techniques) :
   - Pour les familles supportées (`chat`, `guidance`, `natal`, `horoscope_daily`) en **production nominale**, la résolution d'un `ExecutionProfile` est **obligatoire**.
   - Tout échec de résolution (profil manquant, provider non supporté, mapping impossible) doit lever une `GatewayConfigError`.
   - Le fallback historique `resolve_model()` est strictement interdit sur ce périmètre nominal. Il reste toléré pour les familles hors support ou en mode test local.
4. **Assemblage et Mutations du Prompt Developer** (Opérées par le Gateway) :
   - a. Injection des instructions de compensation `context_quality` (via `ContextQualityInjector`)
   - b. Injection des instructions de verbosité (via `verbosity_profile`)
5. **Rendu et Validation** (Opérés par `PromptRenderer.render()`) :
   - a. Résolution des blocs conditionnels `{{#context_quality:VALUE}}...{{/context_quality}}`
   - b. Rendu des placeholders `{{variable}}`
   - c. Nettoyage final des résidus `{{...}}`
6. **Résolution de la Persona**
7. **Résolution du Schéma de sortie**
8. **Gel du plan** -> `ResolvedExecutionPlan` est créé et devient immuable.
9. **Appel Provider résilient** (`ProviderRuntimeManager`) :
   - Gestion des retries applicatifs
   - Circuit Breaker par famille
   - Gestion des Rate Limits (Retry-After)
