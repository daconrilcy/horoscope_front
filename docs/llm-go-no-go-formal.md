# CR Go / No-Go Formelle

## Objet

Décision formelle pour la promotion du runtime `LLM prompt generation`.

## Périmètre évalué

- snapshot : `e2e7191a-b403-42b9-911a-43c6f442420e`
- version : `release-candidate-ready`
- manifest cible : `natal:interpretation:premium:fr-FR`

## Preuves retenues

- qualification corrélée : `go-with-constraints`
- golden corrélée : `pass`
- chaos report 66.43 : vert
- doc ↔ code : vert
- smoke corrélé : `pass`
- activation préprod : `active`

## Point de vigilance

La qualification corrélée passe avec contrainte de performance :

- `p95 latency > 8000 ms`

Ce point n'invalide pas la chaîne de preuve, mais impose une validation opérationnelle explicite avant production.

## Décision

### Préproduction

- **GO préprod confirmé**

Le snapshot `release-candidate-ready` a été activé avec succès en préproduction.

### Production

- **GO prod prudent**

La promotion production est autorisable si l'équipe d'exploitation accepte explicitement le risque de latence observé et maintient les seuils de surveillance et de rollback associés.

## Phrase formelle

> Nous activons le snapshot `e2e7191a-b403-42b9-911a-43c6f442420e` (`release-candidate-ready`), validé par une qualification corrélée `go-with-constraints`, une golden corrélée `pass`, un chaos report 66.43 vert, un smoke corrélé `pass`, avec seuils de release health actifs et procédure de rollback disponible.

## Conditions de maintien du GO

- conserver la corrélation snapshot / qualification / golden / smoke ;
- surveiller la latence `p95` après activation ;
- déclencher rollback si les seuils `release_health` sont franchis ;
- ne pas réutiliser ce CR pour un autre snapshot.

