# Stratégie de Transition et Dépréciation du Versionning de Prédiction

## Contexte

Historiquement, la pile de prédiction quotidienne utilisait une paire de versions asymétrique :
- `reference_version="2.0.0"` (modèle sémantique : planètes, maisons, poids).
- `ruleset_version="1.0.0"` (paramètres de calcul : orbes, types d'événements).

Cette asymétrie créait de la confusion et de la dette technique dans les scripts de seed, les tests et la configuration runtime.

## Vision Cible

Aligner le ruleset sur la version de référence active pour une cohérence "métier" complète :
- `ACTIVE_REFERENCE_VERSION="2.0.0"`
- `ACTIVE_RULESET_VERSION="2.0.0"`

## Relation entre les versions

| Version | Rôle | Statut | Commentaire |
| :--- | :--- | :--- | :--- |
| **Référence 2.0.0** | Modèle de données astro | **Actif** | Source de vérité pour les entités et poids. |
| **Ruleset 2.0.0** | Paramètres de calcul | **Canonique** | Aligné sur la référence 2.0.0. À utiliser par défaut. |
| **Ruleset 1.0.0** | Paramètres de calcul | **Déprécié** | Conservé pour compatibilité avec l'historique. |

## Impact par surface

### Backend runtime

- `ACTIVE_REFERENCE_VERSION=2.0.0` et `RULESET_VERSION=2.0.0` sont la paire attendue pour l'exécution locale, QA et non-prod.
- Le service `DailyPredictionService` journalise `ruleset_version` sur chaque log `prediction.run`.
- Toute demande explicite en `ruleset=1.0.0` produit un warning `DEPRECATION` mais reste tolérée pour les lectures historiques.

### Calibration

- Les jobs de calibration doivent viser le ruleset canonique `2.0.0` afin de rester cohérents avec la référence active `2.0.0`.
- Un job ou script qui force encore `1.0.0` doit être traité comme un flux legacy à migrer, pas comme la configuration standard.
- Les seeds de référence conservent `1.0.0` uniquement pour compatibilité et audit historique.
- Une `ACTIVE_REFERENCE_VERSION` ou une référence demandée invalide provoque désormais un échec immédiat du job: aucun fallback silencieux vers la référence liée au ruleset n'est autorisé.

### QA et tests

- Les fixtures et suites QA doivent semer et consommer la paire canonique `2.0.0` / `2.0.0`.
- Les scénarios en `ruleset=1.0.0` doivent être nommés explicitement comme tests legacy ou backward compatibility.
- Le signal opérationnel à surveiller est le champ structuré `ruleset_version` dans `prediction.run`, pas seulement le texte libre du warning.

## Stratégie de Transition

### Phase 1 : Introduction et Parallélisme (Terminé)
- Création du ruleset `2.0.0` identique au `1.0.0`.
- Les deux rulesets sont rattachés à la référence `2.0.0`.
- Le script de seed `seed_31_prediction_reference_v2.py` crée les deux.

### Phase 2 : Bascule par défaut (Terminé)
- `Settings.active_ruleset_version` pointe vers `2.0.0`.
- Les tests d'intégration et les jobs de calibration utilisent `2.0.0`.
- `backend/.env.example` et `backend/.env` sont alignés sur `RULESET_VERSION=2.0.0`.

### Phase 3 : Monitoring et Migration (En cours)
- Un log de `DEPRECATION` est émis si le ruleset `1.0.0` est utilisé explicitement.
- Identification des appels restants via l'observabilité (champ `ruleset_version` dans les logs).

### Phase 4 : Dépréciation explicite (Planifié)
- Date cible : À déterminer après analyse de l'usage en production.
- Action : Le service lèvera un warning plus agressif (ex: retour dans les métadonnées API).
- Les données historiques ne seront **pas supprimées**, mais les nouveaux calculs en `1.0.0` pourraient être bloqués.

## Runbook de Transition (Développeur)

Si vous voyez des warnings `DEPRECATION: Legacy ruleset '1.0.0' is being used` :

1. Vérifiez vos variables d'environnement (`RULESET_VERSION`) et réalignez `backend/.env` sur `2.0.0` en local si nécessaire.
2. Assurez-vous que votre base de données locale est à jour :
   ```bash
   python -m scripts.seed_31_prediction_reference_v2
   ```
3. Inspectez les logs `prediction.run` et filtrez `ruleset_version="1.0.0"` pour identifier le code ou le test qui force encore le legacy.
4. Si vous testez des flux historiques, vous pouvez ignorer le warning, mais le scénario doit rester explicitement marqué legacy.
