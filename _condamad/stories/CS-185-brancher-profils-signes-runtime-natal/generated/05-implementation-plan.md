# Implementation Plan - CS-185

## Architecture retenue

`ReferenceRepository` conserve le payload public historique. Le repository
runtime `AstrologyRuntimeReferenceRepository` enrichit seulement le flux natal
avec les profils de signes et leurs taxonomies avant que
`AstrologyRuntimeReferenceMapper` ne construise les dataclasses domaines.

## Etapes

1. Capturer le snapshot runtime avant.
2. Ajouter la jointure stricte des profils de signes dans `ReferenceRepository`.
3. Rendre les champs `element`, `modality`, `polarity` obligatoires dans les
   contrats runtime.
4. Faire echouer le chargement runtime sur profil manquant ou incomplet.
5. Aligner le seed de `ReferenceDataService.seed_reference_version()` pour les
   DB de test et runtime.
6. Ajouter les tests et scans de non-retour.
7. Produire les preuves finales et lancer la revue.

## No Legacy

Aucun mapping local signe -> element/modalite/polarite n'est ajoute dans
`domain/astrology` ou `services/natal`. Les fixtures de tests reutilisent la
source seed existante pour eviter un referentiel concurrent.
