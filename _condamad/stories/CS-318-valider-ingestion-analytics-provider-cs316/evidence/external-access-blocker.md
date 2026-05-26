<!-- Commentaire global: ce blocage CS-318 decrit pourquoi la validation provider ne peut pas etre executee localement. -->

# External Access Blocker

Statut: `blocked_external_access`

Date: `2026-05-26`

Provider attendu: Plausible ou Matomo

Environnement attendu: staging ou production observable

Blocage:

- Le runtime local documente par CS-316 utilise `provider: "noop"`.
- Aucun acces dashboard, export ou confirmation de proprietaire d'environnement
  n'est disponible dans cette execution.
- Aucune variable locale ne designe un provider observable pour `/natal`.

Condition de deblocage:

Un responsable environnement doit fournir un acces d'observation ou un extrait
redige confirmant l'ingestion des sept evenements dans le provider configure.

Limite de preuve:

Cette execution ne remplace pas la preuve provider. Elle borne l'absence
d'environnement et conserve un ledger exploitable pour la validation externe.
