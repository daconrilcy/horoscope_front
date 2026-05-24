# CS-251 — Define Official Product Primitives And Public Projection Roadmap

## Résumé

Définir les primitives produit officielles et la roadmap de projection publique sans exposer les surfaces runtime brutes.

Cette story remappe `SC-ARCH-005` et passe après CS-250 dans l'ordre opérationnel demandé.

## Contexte

Les audits CS-238 et CS-244 montrent que le produit a besoin de projections débutant, expert, astrologue et export, mais que `chart_objects` et `ChartObjectRuntimeData` doivent rester internes.

## Objectif

Décider quelles projections deviennent des primitives produit :

- facts structurés ;
- résumé débutant ;
- projection technique expert ;
- fixed-star contacts publics ou gated ;
- données astrologue/debug ;
- input LLM non public.

## Périmètre inclus

1. Inventorier les surfaces runtime et projections existantes.
2. Définir les primitives publiques autorisées.
3. Définir les surfaces qui restent internes.
4. Définir les projections nécessaires pour débutant, expert, astrologue et export PDF.
5. Ajouter ou préparer les guards empêchant l'exposition brute.
6. Produire une roadmap de stories si certaines projections nécessitent une implémentation séparée.

## Hors périmètre

- Exposer directement `chart_objects`.
- Exposer `ChartObjectRuntimeData`.
- Modifier le frontend sans contrat API validé.
- Créer une narration LLM.
- Implémenter une technique temporelle.

## Critères d'acceptation

1. Chaque besoin CS-244 a une projection nommée ou un rejet produit explicite.
2. Les surfaces internes sont clairement interdites en public.
3. La politique fixed-star public/gated est décidée ou marquée `needs-user-decision`.
4. Les tests ou scans empêchent l'exposition brute des surfaces internes.
5. La roadmap sépare contrat API, client frontend et composants UI.
6. Les projections publiques restent compatibles avec OpenAPI.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Si des contrats frontend sont modifiés, exécuter aussi les tests frontend pertinents selon la story d'implémentation.

## Dépendances

- CS-249 pour la matrice objet/capacité.
- CS-250 pour ne pas promouvoir de temporalité publique sans preuve astronomique.

## Risques

Le risque principal est de créer une API miroir du runtime interne. Les projections doivent être des contrats produit, pas des dumps techniques.
