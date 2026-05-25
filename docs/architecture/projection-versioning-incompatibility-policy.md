<!-- Commentaire global: ce document fixe la politique canonique de version et d'incompatibilite des projections publiques ou persistables. -->

# Projection Versioning And Incompatibility Policy

## Statut et proprietaire

Ce document est la politique canonique de versioning des projections. Il complete
la gouvernance des primitives publiques de
`docs/architecture/official-product-primitives-public-projections.md`, le contrat
de commande de projection CS-263 et la persistance CS-264 sans creer une seconde
registry et sans modifier de route, de builder, de modele DB ou de payload
existant.

Chaque contrat de projection doit porter une identite explicite. Le champ
`projection_version` est mandatory et required pour chaque contrat de projection,
pour chaque requete de projection qui cible un contrat versionne, et pour chaque
projection persistee avec `projection_hash` et `source_versions`.

## Identite de version

Une version de projection identifie la forme du payload, ses semantiques produit,
les regles de masquage, l'ordre contractuel des listes visibles, les sources
autorisees et les droits d'acces necessaires. Une projection `v1` ne peut pas
recevoir silencieusement une semantique breaking: toute rupture cree une nouvelle
identite de contrat `v2`.

Les changements suivants forcent un contrat `v2`:

- suppression, renommage ou changement de type d'un champ public ou persistable;
- changement de signification metier d'un champ conserve;
- ajout d'une obligation nouvelle pour construire ou consommer le payload;
- modification des regles de masking, de filtrage, de profondeur par plan ou
  d'exposition de champs internes;
- changement d'ordre contractuel quand l'ordre porte du sens produit;
- changement incompatible de source canonique, de runtime, de reference data ou
  de doctrine qui rend les anciennes `source_versions` non comparables;
- changement d'acces qui rend une projection disponible a une audience differente
  ou retire une audience deja autorisee.

Les corrections non breaking peuvent rester dans la version courante seulement si
elles conservent la forme, la semantique, le masking, l'ordre contractuel, les
sources compatibles et les acces attendus.

## Versions inconnues ou depreciees

Une `projection_version` unknown ou inconnue est un resultat blocking. L'implementation
future ne doit pas appliquer de fallback vers la version courante, ne doit pas
servir une projection approximative et doit produire un `admin_log` ou admin log
avec le type de projection, la version demandee, l'acteur ou le contexte
disponible et la raison du blocage.

Une `projection_version` deprecated ou explicitement `dépréciée` est aussi un
resultat blocking tant qu'une story separee n'a pas defini une fenetre de
transition publique. Le blocage doit produire un `admin_log` indiquant la version
depreciee, la version cible quand elle existe, la surface appelee et la decision
de refus. Une version depreciee ne devient jamais un alias silencieux ou silent
vers `v2`.

## Incompatibilite des sources

Le champ `source_versions` decrit les contrats, runtime, references, policies,
preuves ou versions de doctrine consommes par une projection. Une projection dont
les `source_versions` sont incompatibles avec le contrat demande est blocking.
L'implementation future doit refuser l'usage du payload existant et emettre un
`admin_log` qui nomme la source incompatible, la version attendue, la version
trouvee et le contrat de projection concerne.

Le recalculation ou `recalcul` n'est authorized que si le contrat de projection
nomme explicitement les sources canoniques approuvees pour reconstruire le
payload. Sans cette autorisation explicite, une incompatibilite de
`source_versions` bloque la lecture, la reutilisation et la persistence derivee.

Quand un recalcul est autorise, la nouvelle projection doit produire sa propre
identite `projection_version`, ses propres `source_versions` et son propre
`projection_hash`; elle ne reecrit pas silencieusement l'ancien payload.

## Compatibilite publique

Le produit ne promet pas de strong backward compatibility tant que l'API produit
n'est pas une stable public API et tant qu'aucun engagement public B2B n'a ete
accepte. Cette absence de promesse forte ne permet pas de mutation silencieuse:
elle signifie qu'un changement breaking est livre sous une nouvelle identite
`v2`, avec blocage et logs pour les versions inconnues, depreciees ou
incompatibles.

Les contrats publics futurs peuvent ajouter une politique de transition plus
stricte, mais ils doivent le faire dans leur propre story API ou B2B. Ce document
reste la regle minimale: version explicite, rupture en nouvelle version, refus
des versions inconnues ou depreciees, refus des sources incompatibles sans
recalcul autorise.
