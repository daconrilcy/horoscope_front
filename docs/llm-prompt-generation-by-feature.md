# Génération des Prompts LLM par Feature

Ce document décrit, à partir du code backend, comment les prompts sont générés par famille de features dans l'application.

Objectif :

- montrer les points d'entrée métier ;
- distinguer les couches de composition (template, context, persona, plan) ;
- servir de référence pour l'implémentation de nouvelles features.

## Doctrine d'abonnement (Story 66.9)

La plateforme applique désormais une doctrine canonique pour gérer la variabilité liée à l'abonnement dans la couche LLM. L'objectif est de réduire la prolifération de use_cases dupliqués (`_free`/`_full`) quand seule la longueur ou la profondeur du prompt varie.

### Règle de décision (Waterfall)

1. **Entitlements (Amont)** : Contrôle d'accès et quotas. Si l'utilisateur n'a pas accès à la feature, l'appel est bloqué avant d'entrer dans le gateway LLM.
2. **Plan Assembly (Composition)** : Si la feature est identique mais que l'abonnement change la profondeur, la longueur ou la richesse des instructions (ex: "sois concis" vs "analyse approfondie"), on utilise une configuration assembly unique avec des `plan_rules`.
3. **Use Case Distinct (Contrat)** : Réservé exclusivement aux cas où le **contrat de sortie change structurellement** (schéma JSON différent, structure métier différente).

### Classification des use_cases existants

| Use Case | Plan | Migrable ? | Destination Cible | Raison |
|---|---|---|---|---|
| `horoscope_daily_free` | Free | **Oui** | Feature `horoscope_daily` (plan: free) | Même tâche que `full`, seule la longueur change. |
| `horoscope_daily_full` | Premium | **Oui** | Feature `horoscope_daily` (plan: premium) | Base de référence pour la feature horoscope. |
| `natal_long_free` | Free | **Non** | `natal_long_free` (Maintenu) | Contrat de sortie spécifique (`title`, `summary`, `accordion_titles`) sans équivalent "full" identique. |
| `natal_psy_profile` | Premium | **Non** | N/A | Feature spécialisée, pas un doublon de plan. |

### Conclusion explicite

Le niveau d'abonnement doit être géré en priorité par assembly (`plan_rules`) pour toutes les features partageant le même contrat de sortie.

---

## Les 7 Couches de Composition (Pipeline Story 66.4+)

La composition d'un appel LLM n'est pas monolithique. Elle suit un ordre strict de couches qui s'empilent.

### 1. Template Métier (Base)

Responsabilité :

- intention métier (ex: "Analyse ce thème natal") ;
- structure de la réponse attendue ;
- contraintes fondamentales.

Source de vérité :

- table `llm_prompt_versions` (ou `USE_CASE_STUBS` pour le legacy).

Fichiers pivots :

- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/services/prompt_registry_v2.py`

### 2. Sous-feature (Variante)

Responsabilité :

- spécialisation optionnelle (ex: "Focus sur l'amour" pour une guidance).

Source de vérité :

- champ `subfeature_template_ref` dans l'assembly.

### 3. Persona (Style)

Responsabilité :

- tonalité ;
- style ;
- limites d'expression ;
- cadrage de voix.

#### Bornes stylistiques de la persona (Story 66.10)

La persona est une couche **purement stylistique**. Elle ne doit en aucun cas interférer avec la logique métier, les contrats de sortie ou la sécurité.

##### Dimensions autorisées (Style)

| Dimension | Description |
|---|---|
| `tone` | Registre de voix : chaleureux, professionnel, mystique, factuel... |
| `warmth` | Degré d'empathie et de proximité ressentie |
| `vocabulary` | Champ lexical privilégié : ésotérique, psychologique, poétique... |
| `symbolism_level` | Densité des références symboliques et mythologiques |
| `explanatory_density` | Niveau de détail explicatif par rapport à l'affirmation |
| `formulation_style` | Structure de la formulation (questions, affirmations, métaphores...) |

##### Dimensions interdites (Structure & Logique)

| Dimension | Raison |
|---|---|
| `hard_policy` | Immuable — les garde-fous de sécurité ne sont pas négociables |
| `feature_intent` | Objectif métier défini dans le template de la feature |
| `output_contract` | Le schéma JSON est imposé par le contrat technique |
| `plan_rules` | Les limites liées à l'abonnement sont gérées par la couche Plan |
| `model_choice` | Le choix du modèle LLM relève du profil d'exécution |
| `placeholders` | Les variables techniques sont gérées par le moteur de rendu |

Un lint automatique (Story 66.10) analyse le contenu des personas et émet des avertissements si des mots-clés interdits (ex: "JSON", "ignore instructions", "GPT-4") sont détectés.

Source de vérité :
- persona active ou ciblée en base de données ;
- composition via le service de persona.

### 4. Profils d'exécution (Story 66.11)

Responsabilité :

- choix technique du moteur (provider, modèle) ;
- paramètres de raisonnement (reasoning effort) ;
- paramètres de verbosité et de format (JSON, outils).

#### Abstractions stables

Afin de découpler les instructions métier des spécificités techniques des providers, la plateforme utilise des profils stables. Le `ProviderParameterMapper` traduit ces profils en paramètres spécifiques (OpenAI, Anthropic).

| Profil | Valeurs possibles | Impact |
|---|---|---|
| `reasoning_profile` | `off`, `light`, `medium`, `deep` | `reasoning_effort` (OpenAI), `thinking` (Anthropic) |
| `verbosity_profile` | `concise`, `balanced`, `detailed` | Instruction textuelle + `max_tokens` par défaut |
| `output_mode` | `free_text`, `structured_json` | `response_format` |
| `tool_mode` | `none`, `optional`, `required` | `tool_choice` |

#### Règle de priorité max_output_tokens

Le nombre maximum de tokens en sortie suit une priorité stricte :
1. `LengthBudget.global_max_tokens` (Surchage admin par feature/plan)
2. `ExecutionProfile.max_output_tokens` (Réglage technique du profil)
3. `verbosity_profile` (Valeur par défaut recommandée par le profil de verbosité)

#### Résolution par cascade (Waterfall)

Le profil d'exécution est résolu selon la priorité suivante :
1. Référence explicite dans la configuration assembly (`execution_profile_ref`).
2. Cascade automatique : `feature + subfeature + plan` -> `feature + subfeature` -> `feature`.
3. Résolution par défaut via `resolve_model` (legacy).

Source de vérité :
- table `llm_execution_profiles` en base de données.

### 5. Budgets de longueur (Story 66.12)

Afin de garantir une expérience utilisateur homogène et de contrôler les coûts, la plateforme permet de définir des budgets de longueur à trois niveaux dans la configuration assembly :

1. **Global Max Tokens** : Limite technique dure envoyée au provider (ex: `max_tokens=1500`).
2. **Cible de réponse (Editorial)** : Instruction textuelle globale (ex: "Sois concis, maximum 100 mots").
3. **Cibles par section** : Instructions spécifiques par champ du schéma de sortie (ex: "Section 'summary' : 2-3 phrases").

Ces budgets sont injectés automatiquement à la fin du prompt developer sous la balise `[CONSIGNE DE LONGUEUR]`.

Source de vérité :
- champ `length_budget` (JSON) dans `llm_assembly_configs`.

### 6. Gestion des placeholders (Story 66.13)

La plateforme applique une politique stricte de résolution des variables `{{placeholder}}`. Aucun placeholder non résolu ne doit être envoyé au LLM.

#### Classification

Chaque variable autorisée pour une feature est classifiée :

| Classification | Comportement si absent | Impact exécution |
|---|---|---|
| `required` | Exception ou Log Error | Bloquant pour features sensibles |
| `optional` | Remplacement par chaîne vide | Log Warning |
| `optional_with_fallback` | Remplacement par valeur par défaut | Log Info |

#### Features bloquantes (blocking_features)

Pour certaines features critiques (ex: `natal`, `guidance_contextual`), l'absence d'une variable `required` lève une `PromptRenderError` et interrompt l'appel.

Source de vérité :
- `PLACEHOLDER_ALLOWLIST` dans `assembly_resolver.py`.
- `PLACEHOLDER_POLICY` dans `placeholder_policy.py`.

### 7. Adaptation à la qualité de contexte (Story 66.14)

La rédaction s'adapte dynamiquement au niveau de contexte disponible (`full`, `partial`, `minimal`).

#### Blocs conditionnels
Les templates peuvent utiliser la syntaxe `{{#context_quality:VALUE}}...{{/context_quality}}` pour personnaliser le contenu selon le niveau.

#### Instructions de compensation
Si le template ne gère pas explicitement le niveau, le `ContextQualityInjector` ajoute automatiquement une instruction de compensation (ex: "[CONTEXTE LIMITÉ]...") en fin de prompt.

---

## Axe orthogonal : qualité de contexte

Le `CommonContextBuilder` ne sert pas seulement d'enrichissement secondaire. Il influence directement la qualité du prompt résolu, donc la stabilité et la cohérence de la sortie LLM.

Il peut produire :

- `full` : toutes les données nécessaires sont présentes et valides.
- `partial` : données de base présentes mais compléments manquants (ex: heure de naissance inconnue).
- `minimal` : quasiment aucune donnée fiable, le système doit rester évasif ou pédagogique.

Risque :

- fuite de placeholders bruts dans la couche `developer` ;
- dégradation de qualité silencieuse ;
- sorties moins cohérentes ou moins robustes sans erreur bloquante immédiate.
