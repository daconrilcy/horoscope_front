# CS-252 — Define Astrology Doctrine And School Governance Model

## Résumé

Définir le modèle de gouvernance des doctrines et écoles astrologiques pour éviter les seuils, poids et règles silencieuses.

Cette story remappe `SC-ARCH-007`.

## Contexte

CS-240 montre que les sources de règles astrologiques sont mixtes : DB, Python, tests, documentation et décisions implicites. CS-245 recommande de classer ces règles avant d'étendre la plateforme à de nouvelles techniques.

## Objectif

Créer un modèle de gouvernance qui classe chaque famille de règle :

- DB-owned ;
- Python-owned ;
- mixed ;
- documentation-only ;
- test-only ;
- needs-user-decision.

Le modèle doit aussi décider si le produit supporte une seule doctrine canonique ou plusieurs écoles astrologiques versionnées.

## Périmètre inclus

1. Inventorier les familles de règles auditées.
2. Classer les propriétaires de source.
3. Définir les statuts et transitions autorisés.
4. Ajouter une garde empêchant les nouveaux seuils/poids/profils non classés.
5. Documenter les décisions utilisateur restantes.
6. Préparer la compatibilité avec les futures techniques traditionnelles, modernes ou prévisionnelles.

## Hors périmètre

- Changer des poids ou seuils sans décision.
- Ajouter une nouvelle école complète.
- Migrer massivement les référentiels.
- Modifier la narration.

## Critères d'acceptation

1. Les familles de règles CS-240 sont classées.
2. Les règles liées à CS-241 F-003 ont un owner ou un blocker explicite.
3. Les décisions doctrine vs architecture sont distinguées.
4. Les tests détectent l'ajout de seuils, poids ou profils non gouvernés.
5. Les valeurs `needs-user-decision` ne sont pas remplacées par des choix implicites.
6. Le modèle peut être cité par les stories temporelles futures.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter les scans/guards de gouvernance ciblés.

## Dépendances

- CS-246 pour relier familles runtime et owners.
- CS-249 pour relier capacités d'objets et doctrine.

## Risques

Le risque principal est de confondre gouvernance et refonte métier. Cette story doit classifier et verrouiller, pas réécrire l'astrologie du produit.
