# Executive Summary

## Domain audited

`backend/app/api`, post-refactor audit, archetype `api-adapter-boundary-audit`.

## Overall assessment

Le refactor a corrigé les deux écarts structurels principaux du précédent audit: le routeur admin LLM observability est désormais propriétaire runtime unique, et les routes hors registre v1 sont gouvernées par `API_ROUTE_MOUNT_EXCEPTIONS`. Les gardes d'architecture sont nettement plus fortes.

## Top risks

1. La dette SQL directe dans l'API reste élevée: 848 entrées allowlistées.
2. `/api/email/unsubscribe` reste une URL historique active hors `/v1`, même si elle est maintenant explicitement gouvernée. Son exposition publique est normale pour un lien de désabonnement, mais le token en query string demande des garde-fous HTTP et logging explicites.

## Recommended actions

Prioriser une story de réduction SQL par lot borné, puis décider le statut cible de l'URL publique historique de désabonnement en incluant les durcissements de sécurité: réponse non énumérante, `Cache-Control: no-store`, logs sans token/query string, et décision sur `GET` direct versus confirmation `GET` + action `POST`.

## Story candidates to create first

Créer d'abord `SC-001`. `SC-002` nécessite une décision produit/architecture avant implémentation.
