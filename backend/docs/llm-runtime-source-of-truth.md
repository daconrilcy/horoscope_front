# Source de verite runtime LLM

Ce document fixe la responsabilite de chaque objet DB LLM dans le runtime
canonique. Il evite que les anciens champs de compatibilite redeviennent des
sources nominales apres le regroupement sous `app.infra.db.models.llm`.

## Resolution runtime nominale

`llm_assembly_configs` est le point d entree nominal. Une assembly publiee
identifie la cible runtime par `feature`, `subfeature`, `plan` et `locale`, puis
reference les composants necessaires a l execution.

Les responsabilites sont separees ainsi :

- `llm_assembly_configs` choisit la cible fonctionnelle, les references de
  template, persona, profil d execution et contrat de sortie.
- `llm_prompt_versions` porte le texte de prompt versionne et publie. Ses champs
  historiques de modele ou de fallback ne doivent pas redevenir source nominale
  de provider, modele ou routage.
- `llm_execution_profiles` porte les choix d execution : provider, modele,
  timeout, limite de sortie, raisonnement, verbosite, mode d outil et fallback de
  profil.
- `llm_output_schemas` porte le contrat de sortie structuree. La resolution doit
  utiliser une reference explicite depuis l assembly ou le snapshot de release.
- `llm_release_snapshots` fige un manifeste versionne des assemblies et de leurs
  dependances resolues.
- `llm_active_releases` est le pointeur singleton qui indique quel snapshot est
  actif en runtime.

## Priorite entre tables

Quand une release active existe, le runtime doit considerer le snapshot actif
comme la version figee de la configuration. Les tables sources restent les
surfaces d administration et de preparation des prochaines releases.

Quand aucun snapshot actif n est disponible en environnement local ou en mode de
bootstrap, le runtime peut lire les tables sources publiees dans cet ordre :

1. assembly publiee pour `feature/subfeature/plan/locale` ;
2. templates et persona references par cette assembly ;
3. execution profile explicite ou resolu par waterfall canonique ;
4. output schema reference par l assembly.

## Compatibilite legacy

Dans `llm_assembly_configs`, les champs `execution_config`, `interaction_mode`,
`user_question_policy`, `input_schema`, `output_contract_ref` et
`fallback_use_case` sont des champs de compatibilite ou de reference bornee, pas
des sources libres d execution runtime.

Quand `execution_profile_ref` est present, `execution_config` peut seulement
rester comme miroir historique compatible. La validation de coherence refuse a
la publication les valeurs qui contredisent le profil reference pour `model`,
`provider`, `timeout_seconds`, `max_output_tokens` ou `temperature`.

Les champs `use_case`, `fallback_use_case`, `fallback_use_case_key`, `model`,
`temperature`, `reasoning_effort`, `verbosity` et `max_output_tokens` presents
sur d autres anciens objets ne doivent pas reprendre une autorite runtime
nominale si une source canonique existe.

Ces champs restent toleres uniquement pour :

- lire l historique admin ;
- reclasser des lignes d observabilite anciennes ;
- executer un fallback explicitement documente ;
- permettre un rollback encadre par une migration ou un runbook.

Tout nouveau consommateur nominal doit donc partir de l assembly canonique ou du
snapshot actif, puis descendre vers les composants references.
