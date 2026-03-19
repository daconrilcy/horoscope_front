# Migration du Contrat API : V3 → V4 (Epic 60)

## Contexte
Dans le cadre de la Refonte V4 de la page "Horoscope du jour", le payload de l'API a été enrichi pour supporter une nouvelle narration centrée sur l'utilisateur.

## Changements du Payload

### Nouveaux champs ajoutés (V4)
Tous ces champs sont optionnels pour assurer la compatibilité ascendante.

| Champ | Type | Description |
|-------|------|-------------|
| `meta.payload_version` | `str` | Indique la version du schéma (`"v3"` ou `"v4"`). |
| `day_climate` | `object` | Résumé global du climat de la journée (label, tone, intensity, top_domains...). |
| `domain_ranking` | `list` | Les 5 domaines publics avec score sur 10 et niveau lisible. |
| `time_windows` | `list` | Fenêtres temporelles narratives (regime, label, action_hint). |
| `turning_point` | `object` | Le point de bascule principal de la journée (si significatif). |
| `best_window` | `object` | La meilleure opportunité temporelle de la journée. |
| `astro_foundation` | `object` | Détails techniques/astrologiques (mouvements, maisons, aspects). |
| `categories_internal` | `list` | Copie des 12 catégories internes (pour debug/rétrocompat). |

### Champs conservés (Rétrocompatibilité)
Ces champs restent présents pour ne pas casser les clients V3.

- `summary`
- `categories` (contient toujours les 12 domaines internes)
- `timeline`
- `turning_points` (liste complète technique)
- `decision_windows`
- `micro_trends`

## Stratégie de Déploiement

1. **Backend First** : Déployer le backend V4. Les clients V3 existants ignoreront les nouveaux champs JSON.
2. **Frontend** : Déployer le frontend V4. Il détectera `payload_version: "v4"` et affichera les nouveaux composants. En cas d'absence du flag, il retombera sur l'affichage V3.
3. **Cleanup** : Une fois la migration validée, les anciens composants et champs pourront être supprimés (prévu en Story 60.12).

## Validation
- Les tests d'intégration dans `backend/tests/integration/test_v4_migration.py` valident la présence des anciens champs dans un payload V4.
- Le frontend utilise des mappers avec fallback pour garantir un affichage même sur des données incomplètes.
