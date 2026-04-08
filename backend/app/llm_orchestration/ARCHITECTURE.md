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

1. **Qualification du contexte** (`CommonContextBuilder`)
2. **Résolution de l'Assembly** (Sélection des IDs et activation des flags)
3. **Résolution du Profil d'Exécution** (Choix du moteur et paramètres techniques)
4. **Assemblage du Prompt Developer** :
   - Blocs conditionnels `context_quality`
   - Instructions de compensation `context_quality`
   - Instructions de verbosité
   - Rendu des placeholders `{{variable}}`
5. **Résolution de la Persona**
6. **Résolution du Schéma de sortie**
7. **Gel du plan** -> `ResolvedExecutionPlan` est créé et devient immuable.
8. **Appel Provider**
