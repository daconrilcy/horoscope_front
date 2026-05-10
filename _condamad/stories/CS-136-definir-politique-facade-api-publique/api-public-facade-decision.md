<!-- Decision d'architecture sur la facade publique API frontend pour CS-136. -->

# CS-136 - Decision facade publique API

## Decision

La politique retenue est: conserver `frontend/src/api/index.ts` comme facade
publique globale stable pour les consommateurs existants, tout en autorisant les
entrypoints par domaine `@api/<module>` et les imports relatifs directs depuis
les tests ou les features deja en place.

Le domaine `frontend/src/api/**` ne doit jamais importer le barrel public
`@api`; les imports internes passent par des chemins relatifs vers l'owner local
ou le helper canonique.

## Consequences

- CS-131 peut modifier les modules API sans modifier la facade publique.
- CS-132 peut exporter les helpers/types canoniques depuis `client.ts` ou un
  sous-module core, puis les rendre accessibles par la facade globale si besoin.
- CS-133 peut scinder `adminPrompts` et `natalChart` en sous-modules, mais les
  fichiers racine doivent rester l'entrypoint public unique de ces domaines.
- CS-134 doit garder une regle zero exception: aucun import `@api` sous
  `frontend/src/api`.
- CS-135 peut supprimer l'exposition ops persona depuis `support.ts` sans
  changer la politique globale, car l'owner canonique reste exporte via
  `opsPersona.ts`.

## Regles futures

1. Ajouter un export a `index.ts` exige une classification d'owner.
2. Un module sans consommateur runtime peut rester public seulement s'il est
   classe `public-export-retained` ou `external-unknown`.
3. Les sous-modules de domaine ne doivent pas creer de facade parallele non
   documentee.
4. Les stories d'application doivent ajouter ou etendre les guards executables
   quand elles changent cette politique.

## Verification

La decision ne change aucun fichier runtime par elle-meme. Les changements de
code necessaires sont portes par CS-131 a CS-135.
