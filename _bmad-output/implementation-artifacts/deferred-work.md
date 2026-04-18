# Travail différé

## Deferred from: code review of 67-1-clarifier-modes-preview-et-statuts-placeholders.md (2026-04-17)

- **Placeholders sans définition registry (`unknown`)** — En `assembly_preview`, ils restent en statut `unknown` plutôt qu’`expected_missing_in_preview`. Comportement acceptable pour placeholders non gouvernés ; homogénéisation éventuelle si le produit veut une seule grille de statuts partout.

## Deferred from: code review of 67-2-exposer-construction-logique-graphe-inspectable.md (2026-04-17)

- **Résilience limitée si payload `resolved` partiel** — La robustesse aux payloads incomplets n'est pas spécifique à ce diff (la vue détail déréférence déjà plusieurs sous-objets du payload), amélioration à traiter de façon transverse sur la surface d'inspection admin.

## Deferred from: code review of 68-3-gerer-sample-payloads-depuis-surface-admin.md (2026-04-17)

- **Double chargement catalogue sur l’onglet samples** — `AdminSamplePayloadsAdmin` refait un `useAdminLlmCatalog` pour les facettes alors que la page parent charge déjà le catalogue sur l’onglet catalogue ; regrouper ou mutualiser les facettes pour réduire les appels réseau.

## Deferred from: code review of 69-2-afficher-retour-llm-brut-structure-metadonnees-execution.md (2026-04-18)

- **`anonymize_text` sans garde-fou dans le helper de payload manuel** — Même pattern que sur d’autres chemins ; traiter transversalement si besoin de tolérance aux pannes de config salt.

## Deferred from: code review of 69-3-securiser-surface-execution-manuelle-et-qa.md (2026-04-18)

- **Mutation `useMutation` : `isSuccess` sans `data`** — La zone d’aide « Retour LLM » dépend de `!manualExecuteMutation.isSuccess`. Si un cas extrême produisait un succès sans payload, l’utilisateur ne verrait ni résultat ni invite ; à traiter seulement si observé en prod (contrat TanStack Query habituellement garantit `data` au succès).
