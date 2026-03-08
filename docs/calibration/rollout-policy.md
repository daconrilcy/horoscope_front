# Politique de Rollout de Calibration

Ce document décrit la politique de gestion, de versionnage et de déploiement des calibrations du moteur de prédiction.

## États de Calibration

Une calibration peut se trouver dans l'un des états suivants, identifié par son `calibration_label` :

1.  **provisional** : État initial après le calcul automatique des percentiles. Cet état signifie que les données sont statistiquement calculées mais n'ont pas encore subi de validation métier approfondie.
2.  **v1, v2, ...** : État "promu". Une calibration passe à ce stade après validation métier (story 37-4) et décision explicite documentée dans `review-decision.md`.
3.  **mixed** : État transitoire anormal où plusieurs labels coexistent sur les catégories actives d'un même ruleset. Le moteur l'expose explicitement pour éviter d'annoncer à tort une version stable unique.

## Règle d'Immuabilité

**Les runs historiques ne sont jamais recalculés silencieusement lors d'un changement de calibration.**

- Les scores (`note_20`, `raw_score`) persistés dans `daily_prediction_runs` et ses entités filles sont définitifs pour un `input_hash` donné.
- Un changement de calibration n'affecte que les **nouveaux** calculs.
- La traçabilité est assurée par la présence de `calibration_label` dans les métadonnées de chaque run.
- Si une calibration active est encore `provisional` ou si plusieurs labels coexistent, `meta.is_provisional_calibration` reste vrai ou `meta.calibration_label` vaut `mixed` afin que le payload API ne présente jamais une stabilité fictive.

## Procédure de Promotion

Pour promouvoir une calibration de `provisional` vers une version stable (`vN`) :

1.  **Calcul** : Le job de calcul des percentiles (story 37-3) injecte les données avec le label `provisional`.
2.  **Revue** : Une grille de revue est générée et validée par les experts métier (story 37-4).
3.  **Décision** : La décision de promotion est actée dans `docs/calibration/review-decision.md`.
4.  **Action Technique** : Le `calibration_label` est mis à jour en base de données dans la table `category_calibrations` pour les entrées concernées.
5.  **Vérification** : Les nouveaux runs doivent désormais porter le nouveau label dans leur `meta.calibration_label`.
6.  **Cohérence** : Toutes les catégories actives d'un même ruleset doivent partager le même label promu avant ouverture du rollout. La présence de `mixed` doit être traitée comme un incident de rollout.

## Procédure de Rollback

En cas d'anomalie détectée après une promotion :

1.  Identifier la version de calibration précédente stable.
2.  Mettre à jour la table `category_calibrations` pour restaurer les percentiles précédents ou changer le label actif.
3.  Les runs effectués sous la version défaillante restent en historique avec leur label ; les nouveaux calculs reprendront la version stable restaurée.
4.  Si un rollback partiel laisse coexister plusieurs labels, le moteur exposera `mixed` tant que l'état homogène n'est pas rétabli.
