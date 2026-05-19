# Implementation Plan CS-191

1. Etendre le runtime immutable avec `PlanetDignityReferenceSet`.
2. Charger les regles, poids et conditions de dignites depuis les repositories infra.
3. Creer les contrats et calculateurs purs sous `domain/astrology/dignities`.
4. Integrer le scoring dans `build_natal_result` et projeter `dignities` dans `json_builder`.
5. Ajouter tests unitaires et garde d'architecture RG-118.
6. Capturer evidence payload avant/apres et runtime.
7. Executer tests cibles, Ruff et scans zero-hit.
