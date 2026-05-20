<!-- Brief d'execution CONDAMAD pour CS-204. -->

# CS-204 Execution Brief

## Objectif

Exposer `hayz` et `rejoicing` comme contrats explicites dans le resultat natal,
le JSON public et le panneau expert, sans changer la doctrine, les scores, les
routes, les migrations ou les seeds.

## Contraintes

- Le normalizer domaine est l'unique proprietaire du bloc
  `traditional_conditions`.
- `json_builder.py` serialize uniquement le contrat deja calcule.
- Le frontend affiche uniquement les champs fournis par le backend.
- Aucun mapping local de planetes, maisons de joie, horizons ou genres de
  signes n'est autorise.
- Les modes no-time ne doivent pas fabriquer de contrat house-dependent.

## Done

- AC1 a AC12 couverts par tests, scans et evidence persistante.
- `RG-131` ajoute au registre.
- Revue finale `CLEAN`.
- Aucun commit/push automatique.
