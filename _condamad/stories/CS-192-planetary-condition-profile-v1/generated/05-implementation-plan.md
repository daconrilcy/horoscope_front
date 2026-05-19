<!-- Plan d'implementation CS-192 maintenu pendant le developpement. -->

# CS-192 Implementation Plan

1. Etendre les colonnes de poids de dignites avec axes conditionnels neutres.
2. Transporter les axes dans `DignityScoreWeightReferenceData` via repository et mapper.
3. Ajouter les contrats et le service pur `PlanetConditionProfileService`.
4. Integrer les profils au calcul natal et au serialiseur JSON public.
5. Ajouter les tests unitaires, integration migration et garde RG-119.
6. Produire les snapshots et rapports evidence.
7. Executer tests, scans et lint sous venv, puis lancer la revue CONDAMAD.

## No Legacy

Aucune compatibilite, alias, fallback silencieux, mapping local de poids
conditionnels ou table dediee n'est autorise.
