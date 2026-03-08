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

## Stratégie de Transition

### Phase 1 : Introduction et Parallélisme (Terminé)
- Création du ruleset `2.0.0` identique au `1.0.0`.
- Les deux rulesets sont rattachés à la référence `2.0.0`.
- Le script de seed `seed_31_prediction_reference_v2.py` crée les deux.

### Phase 2 : Bascule par défaut (Terminé)
- `Settings.active_ruleset_version` pointe vers `2.0.0`.
- Les tests d'intégration et les jobs de calibration utilisent `2.0.0`.
- `.env.example` est mis à jour.

### Phase 3 : Monitoring et Migration (En cours)
- Un log de `DEPRECATION` est émis si le ruleset `1.0.0` est utilisé explicitement.
- Identification des appels restants via l'observabilité (champ `ruleset_version` dans les logs).

### Phase 4 : Dépréciation explicite (Planifié)
- Date cible : À déterminer après analyse de l'usage en production.
- Action : Le service lèvera un warning plus agressif (ex: retour dans les métadonnées API).
- Les données historiques ne seront **pas supprimées**, mais les nouveaux calculs en `1.0.0` pourraient être bloqués.

## Runbook de Transition (Développeur)

Si vous voyez des warnings `DEPRECATION: Legacy ruleset '1.0.0' is being used` :

1. Vérifiez vos variables d'environnement (`RULESET_VERSION`).
2. Assurez-vous que votre base de données locale est à jour :
   ```bash
   python -m scripts.seed_31_prediction_reference_v2
   ```
3. Si vous testez des flux historiques, vous pouvez ignorer le warning.
