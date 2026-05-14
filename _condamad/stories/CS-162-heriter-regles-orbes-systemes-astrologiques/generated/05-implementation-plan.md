<!-- Plan d'implementation vivant pour CS-162. -->

# Implementation Plan

1. Capturer le baseline avant: presence de `copy_rules_from`, comptages attendus actuels et comportement du resolver.
2. Ajouter la self-FK nullable `inherits_from_system_id` au modele et a Alembic, puis renseigner la carte d'heritage dans le seed.
3. Remplacer le depliage `copy_rules_from` par une lecture directe des groupes locaux et un guard anti-copie complete.
4. Exposer `astral_systems` dans le payload de reference et adapter `resolve_orb` pour calculer la chaine locale puis parente avec detection de cycle.
5. Mettre a jour les tests unitaires/integration et les compteurs de reference de `159` vers `79` quand applicable.
6. Mettre a jour les trois documents de recherche et les preuves persistantes avant/apres.
7. Executer les validations ciblees, lint/format, scans No Legacy, puis revue CONDAMAD.

## Rollback strategy

Revenir les fichiers de cette story uniquement si une validation bloque sans correctif local; ne pas toucher aux changements utilisateur hors scope.
