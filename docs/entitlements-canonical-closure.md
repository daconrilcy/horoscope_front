# Clôture du chantier entitlements canoniques — Objectif atteint

## Objectif du sous-chantier

Migrer le système de droits produit d'un modèle couplé au legacy billing vers une
plateforme canonique d'entitlements gouvernée, observable et validée de bout en bout.
(Stories 61.7 à 61.50 de l'epic 61.)

## État atteint

| Phase | Stories | Livraison |
|---|---|---|
| Fondations canoniques | 61.7–61.10 | Modèle canonique, backfill, EntitlementService, moteur de quotas |
| Migration B2C | 61.11–61.17 | Gates B2C migrées, endpoint `GET /v1/entitlements/me`, décommission quota legacy |
| Migration B2B | 61.18–61.26 | Runtime B2B canonique, compteurs entreprise natifs, nettoyage admin_user_id |
| Garde-fous | 61.27–61.30 | Registre de scope, validation statique, enforcement CI, validation DB |
| Gouvernance écritures | 61.31–61.38 | Écriture centralisée, audit trail, review queue, SLA ops |
| Alerting ops | 61.39–61.46 | Alerting persistant, retry, triage, règles de suppression durables |
| Unification runtime | 61.47–61.50 | Resolver effectif, gates rebranchées, contrat frontend, validation e2e |

## Travaux post-clôture prévus

1. **Suivi production** : surveillance des alertes ops en conditions réelles,
   ajustements SLA si nécessaire.
2. **Corrections mineures isolées** : bugs ponctuels identifiés en production,
   traités au cas par cas sans rouvrir de chantier.
3. **Dette technique ciblée** : les reliquats legacy inventoriés dans
   `docs/entitlements-legacy-remnants.md` sont la liste de référence.
   Chaque suppression sera effectuée en story courte indépendante,
   uniquement si la régression est exclue par grep et tests existants.

## Ce qui n'est pas prévu

Aucune nouvelle étape structurante du chantier entitlements n'est planifiée dans
l'epic 61. Les prochaines stories de l'epic 61 porteront sur d'autres sujets produit.
