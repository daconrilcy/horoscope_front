<!-- Plan d'implementation CS-119 centre sur une suppression test-only sans compatibilite. -->

# Implementation Plan - CS-119

1. Capturer l'inventaire avant avec tous les fichiers composants et les preuves
   d'imports pour les cibles de suppression.
2. Supprimer uniquement les composants confirmes `test-only`, leurs CSS orphelins
   et leurs tests focalises.
3. Adapter les guards transverses et supprimer les exceptions allowlist stale.
4. Remplacer le type interne `MiniInsightCardType` dans `useDailyInsights.ts`
   sans importer de composant supprime.
5. Ajouter ou renforcer le guard anti-reintroduction des chemins/symboles CS-119.
6. Executer les validations ciblees, les scans negatifs et les validations de
   story avec venv active.
7. Mettre a jour les preuves finales, lancer la revue, corriger les findings et
   synchroniser le statut.

## No Legacy Stance

Aucun wrapper, alias, fallback, re-export, barrel de compatibilite ou exception
large n'est autorise pour conserver les surfaces supprimees.
