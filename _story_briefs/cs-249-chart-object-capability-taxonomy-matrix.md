# CS-249 — Define Chart Object Capability And Object Taxonomy Matrix

## Résumé

Formaliser la matrice de capacités et la taxonomie des objets astrologiques pour éviter les branches ad hoc par `object_type`.

Cette story remappe `SC-ARCH-004`.

## Contexte

CS-217 à CS-224 ont fait converger le runtime vers `ChartObjectRuntimeData`. Les audits CS-237 et CS-239 montrent cependant que certaines familles d'objets restent ambiguës : angles, noeuds, lots, astéroïdes, Chiron, midpoints et étoiles fixes.

## Objectif

Créer une matrice canonique décrivant, pour chaque famille d'objet, les capacités autorisées :

- positionnel ;
- aspectable ;
- interprétable ;
- scorable ;
- dignité-éligible ;
- dominance-éligible ;
- motion/visibility ;
- house/rulership ;
- fixed-star-contact ;
- projection publique.

## Périmètre inclus

1. Définir la matrice de capacités.
2. Couvrir Soleil, Lune, planètes classiques, planètes modernes, ASC/MC/angles, noeuds lunaires, Lilith, apsides, lots, astéroïdes, Chiron, midpoints et étoiles fixes.
3. Marquer explicitement les décisions `needs-user-decision`.
4. Ajouter une garde ou un test empêchant la croissance de branches ad hoc non gouvernées.
5. Préserver le comportement existant tant qu'une décision produit/doctrine n'autorise pas de changement.

## Hors périmètre

- Implémenter les lots, astéroïdes, Chiron ou midpoints comme nouveaux calculateurs.
- Changer les orbes d'aspects.
- Modifier la projection publique.
- Ajouter une migration DB.

## Contrat attendu

La matrice doit être exploitable par le code ou par une garde testable. Un simple document non vérifié ne suffit pas si le code continue à diverger.

Colonnes minimales :

```text
object_family
canonical_type
source_kind
positionable
aspectable
interpretable
scorable
dignity_eligible
dominance_eligible
public_projection
decision_status
```

## Critères d'acceptation

1. Tous les objets obligatoires de CS-245 sont couverts.
2. Les capacités existantes sont préservées.
3. Les décisions inconnues sont explicites et bloquantes.
4. Les tests détectent une nouvelle famille non classée.
5. Les branches ad hoc par `object_type` sont interdites ou inventoriées avec justification.
6. Aucun calculateur de nouvelle famille n'est introduit sans décision.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter une commande ciblée pour la matrice et les guards architecture.

## Dépendances

- CS-246 pour le registre de familles runtime.
- CS-251 consommera cette matrice pour la roadmap des projections publiques.

## Risques

Le risque principal est de transformer une matrice de gouvernance en changement métier implicite. Toute modification de comportement doit être nommée et testée séparément.
