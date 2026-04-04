# Epic 63: Landing page et funnel de conversion vers des utilisateurs payants

Status: implemented

## Objectif

Créer une landing page publique crédible et maintenable, reliée à un funnel d'inscription et d'activation cohérent avec le produit réel, sans inventer de pricing, de preuves sociales ni de capacités backend non encore exposées.

## Décisions de cadrage

1. La route publique canonique est `/` et doit être rendue depuis `routes.tsx` sous `RootLayout`, sans redirection intermédiaire vers `/login`.
2. L'inscription visée par l'epic est une création de compte applicatif via `/register`, pas une simple capture d'email marketing.
3. Le modèle de plans à respecter pour cet epic est le modèle produit actuel : `free`, `trial`, `basic`, `premium`.
4. La landing ne dépend d'aucun endpoint billing authentifié pour afficher ses offres. Si un endpoint public existe plus tard, il pourra être branché sans casser le fallback de configuration.
5. L'email J0 est transactionnel et distinct de la séquence marketing J+1/J+7.
6. Le désabonnement concerne les emails marketing uniquement. Il ne doit jamais bloquer les emails transactionnels.
7. Les stories V2 ou dépendantes d'une infrastructure non stabilisée doivent être explicitement marquées comme telles.

## Ordre de livraison recommandé

### MVP

- `63.01` Hero + route `/`
- `63.02` Navbar
- `63.03` Preuves rapides
- `63.04` Problème / opportunité
- `63.05` Solution / comment ça marche
- `63.06` Témoignages / cas clients
- `63.07` Offre / tarifs alignés produit réel
- `63.08` FAQ + CTA final
- `63.09` Footer
- `63.10` SEO / performance
- `63.11` Inscription produit optimisée conversion
- `63.12` Email de bienvenue J0 transactionnel
- `63.13` Abstraction provider email + EmailLog
- `63.14` Désabonnement marketing tokenisé
- `63.16` Instrumentation analytics
- `63.17` Accessibilité transverse

### V2

- `63.15` Scheduler séquence emails J+1 à J+7

## Artefacts obsolètes ou remplacés

- `63-11-page-inscription-capture-lead.md` est remplacé par `63-11-page-inscription-produit-conversion.md`.
- `63-12-sequence-emails-bienvenue.md` est remplacé par le découpage `63.12` (J0 transactionnel), `63.13` (infra provider/logs), `63.14` (unsubscribe marketing) et `63.15` (scheduler J+1/J+7).

## Risques neutralisés par cette revue

- Doubles numéros de stories `63.11` et `63.12`.
- Contradiction entre le routing documenté et le routing réel React Router.
- Invention d'IDs de plans `premium_monthly` / `pro_annual` absents du produit.
- Dépendance erronée à `/v1/billing/plans`, endpoint authentifié et donc inutilisable par une landing publique.
- Mélange entre email transactionnel et désabonnement marketing.

## Mise en oeuvre réelle

1. La landing publique a été refondue en une narration plus éditoriale et démonstrative : `Navbar` compacte au scroll, `Hero` avec mockup produit crédible, bloc confiance enrichi, diptyque problème/transformation, 3 étapes d'usage, pricing rehiérarchisé, FAQ + CTA final plus direct, footer allégé.
2. La section `63.06` n'est plus exposée dans le parcours principal de la landing refondue. Le composant de témoignages reste disponible derrière feature flag pour usage futur, mais le funnel MVP actuel s'appuie sur un bloc confiance qualitatif et la FAQ.
3. L'instrumentation analytics est active via `useAnalytics()` avec support `noop | plausible | matomo`. Plausible est traité comme provider privacy-first sans dépendance à un cookie de consentement applicatif.
4. La séquence emails J+1/J+7 (`63.15`) reste en code mais n'est plus déclenchée par défaut : elle est désormais protégée par le flag backend `ENABLE_ONBOARDING_EMAIL_SEQUENCE=false` tant qu'elle n'est pas validée en production.
5. Les contenus fictifs non vérifiables ont été neutralisés dans le funnel principal : pas de métriques chiffrées ni de témoignages publiés par défaut.
