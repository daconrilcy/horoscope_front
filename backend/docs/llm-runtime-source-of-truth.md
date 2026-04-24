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

## Legacy supprime

Les champs legacy d assembly, de prompt version, de use case config et de call
log ne doivent plus etre consultes par le runtime nominal.

Le runtime ne lit plus ses parametres d execution que depuis :

- `llm_execution_profiles` ;
- le snapshot de release actif ;
- les objets canoniques explicitement references par l assembly.

Tout payload legacy doit echouer explicitement ou passer par une migration
ponctuelle hors runtime nominal.
