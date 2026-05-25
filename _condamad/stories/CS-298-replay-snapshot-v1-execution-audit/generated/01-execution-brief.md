# Execution brief - CS-298

Implementer l'orchestration d'audit `replay_snapshot_v1` cote backend uniquement.

Scope:
- audit obligatoire des lectures metadata, tentatives de replay et purges;
- details bornes sans prompt brut, donnees naissance, secrets, email, payload chiffre ou payload provider;
- refus avant execution provider pour snapshot expire, purge, introuvable ou incomplet;
- API strictement interne sous `/v1/admin/audit`;
- documentation des limites de reproductibilite.

Non-goals:
- pas de frontend;
- pas de migration DB;
- pas de nouvelle route publique/support/B2B;
- pas de changement de prompt ou de provider executor.
