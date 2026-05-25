<!-- Commentaire global: ce document fixe le contrat canonique structured_facts_v1 sans creer d'implementation runtime ni de surface publique. -->

# Contrat `structured_facts_v1`

## Role

`structured_facts_v1` est la projection factuelle stable, hashable et non narrative qui sert de base commune aux futures projections client, admin/expert, entree LLM, audit et `evidence_refs`.

Ce contrat documente une forme cible partagee. Il ne cree pas de builder, de route API, de schema OpenAPI, de table, de migration, de client frontend ou de serializer runtime.

Le registre produit existant conserve le primitif `structured_facts`; `structured_facts_v1` en precise la version contractuelle stable pour les usages futurs controles.

## Projection

| Champ | Regle |
|---|---|
| `projection_id` | Valeur exacte: `structured_facts_v1`. |
| `role` | Base factuelle stable pour projection produit, audit, entree LLM controlee et references d'evidence. |
| `consumer_policy` | Les consommateurs futurs sont optionnels et explicites: client, admin/expert, LLM input, audit et product projection. Le B2C n'est pas un consommateur direct obligatoire. |
| `source_of_truth` | Les faits restent derives du runtime canonique de calcul astrologique, pas d'un prompt, d'une prose finale ou d'une reponse LLM. |

## Familles de faits autorisees

`structured_facts_v1` peut contenir uniquement les familles de faits suivantes:

- `positions`: positions astrologiques normalisees, avec identifiants stables, signes, degres, maisons associees et unites explicites.
- `houses`: cuspides, axes, systeme de maisons et metadonnees de reference necessaires a la lecture structurelle.
- `major aspects`: aspects majeurs calcules avec objets source/cible, type d'aspect, orbe et precision stable.
- `dominants`: dominantes calculees et classements derives du runtime, avec methode et version source.
- `source metadata`: versions de catalogues, moteur de calcul, regles de precision, horodatage de generation contractuel et identifiants de provenance.

Aucune autre famille ne devient autorisee par implication. Toute extension requiert une story separee qui met a jour ce contrat et ses validations.

## Regles de stabilite

La projection impose une stable ordering pour rendre les comparaisons, signatures et audits reproductibles:

- les collections sont triees par identifiant metier stable, puis par role astrologique si necessaire;
- les objets sans identifiant public stable ne peuvent pas etre serialises tels quels;
- les nombres utilisent une precision stable documentee par famille;
- les unites sont explicites et constantes entre executions;
- l'ordre runtime, l'ordre d'insertion, les adresses memoire, les labels de debug et les traces temporaires sont exclus.

## Regles de hachage

Le hachage sert l'AI audit, la comparaison de projections et la detection de derive de faits, pas l'authentification ni le stockage de secrets.

La deterministic serialization du hash input boundary inclut uniquement:

- `projection_id`;
- les familles autorisees dans leur ordre canonique;
- les versions de sources et catalogues;
- les regles de precision appliquees;
- les identifiants de provenance strictement necessaires a l'audit.

Le hash input boundary exclut toute donnee narrative, tout prompt, tout texte rendu, toute reponse LLM, toute trace brute et tout payload interne. La forme de serialization doit etre canonique: noms de champs stables, tri deterministe, normalisation des nombres et absence de champs optionnels vides non significatifs.

## Lien avec `AINarrativeInputContract`

`AINarrativeInputContract` peut consommer `structured_facts_v1` comme entree downstream ou le referencer comme base de faits stabilisee.

Cette relation ne transfere pas la calculation truth vers le contrat IA. La verite de calcul reste dans les proprietaires runtime et dans les projections typifiees en amont. `AINarrativeInputContract` assemble un contexte de scoring ou de narration; il ne devient pas proprietaire des faits astrologiques.

Tout champ derive pour la narration doit rester en aval de `structured_facts_v1` et ne peut pas modifier le contenu hashable de la projection factuelle.

## Contraintes non narratives

`structured_facts_v1` est non narrative. Les contenus suivants sont interdits dans la projection:

- prompt text;
- rendered prose;
- advice;
- LLM output;
- interpretation finale;
- titres ou paragraphes rediges pour l'utilisateur;
- champs dont le sens depend d'un style editorial ou d'un fournisseur LLM.

Ces contenus peuvent exister dans des projections ou contrats aval separes, mais pas dans le hash factuel ni dans la projection `structured_facts_v1`.

## Surfaces exclues

Les surfaces brutes suivantes restent internes et ne sont pas des payloads publics de `structured_facts_v1`:

- `ChartObjectRuntimeData`;
- raw `chart_objects`;
- debug raw traces;
- runtime traces;
- internal payloads;
- graphes de calcul complets;
- objets Pydantic internes marques comme runtime-only.

Ces noms peuvent etre cites comme proprietaires ou sources internes, mais ils ne deviennent pas des champs publics ni des schemas clients.

## Frontieres applicatives

Cette story ne publie pas `structured_facts_v1` dans une route, un schema OpenAPI ou un client frontend. Toute exposition publique future doit definir:

- le consommateur exact;
- la selection de champs;
- la politique de redaction;
- la compatibilite avec le hash input boundary;
- les validations de non-regression API et frontend.
