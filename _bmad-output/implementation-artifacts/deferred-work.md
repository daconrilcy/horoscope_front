# Travail différé

## Deferred from: code review of 67-1-clarifier-modes-preview-et-statuts-placeholders.md (2026-04-17)

- **Placeholders sans définition registry (`unknown`)** — En `assembly_preview`, ils restent en statut `unknown` plutôt qu’`expected_missing_in_preview`. Comportement acceptable pour placeholders non gouvernés ; homogénéisation éventuelle si le produit veut une seule grille de statuts partout.

## Deferred from: code review of 67-2-exposer-construction-logique-graphe-inspectable.md (2026-04-17)

- **Résilience limitée si payload `resolved` partiel** — La robustesse aux payloads incomplets n'est pas spécifique à ce diff (la vue détail déréférence déjà plusieurs sous-objets du payload), amélioration à traiter de façon transverse sur la surface d'inspection admin.
