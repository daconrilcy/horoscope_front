# CS-390 — Audit architecture lecture natale publique `/natal`

Date: 2026-05-30. Périmètre: page `NatalChartPage` après CS-386 à CS-389.

## 1. Inventaire des blocs visibles

| Bloc | Composant | États couverts |
|---|---|---|
| En-tête page | `natal-page-header` | normal, titre short/complete |
| Alertes dégradées | `natal-page__degraded-warning` | `no_location`, `no_time`, `no_location_no_time` |
| Hero | `NatalProfileHero` | chart chargé |
| Synthèse IA | `NatalThemeSynthesis` → `NatalInterpretationSection` | loading, empty, error, quota, free lock, complete |
| ADN astrologique | `NatalAstrologicalDna` | fallback `explanation_facts` |
| Domaines de vie | `NatalLifeDomains` | liste fixe + placements |
| Forces | `NatalStrengths` | dominantes + texte moteur |
| Défis | `NatalChallenges` | placements fallback |
| Aspects majeurs | `NatalMajorAspects` | `dominant_aspects` |
| Signature karmique | `NatalKarmicSignature` | nœuds / Saturne / Pluton |
| Talents cachés | `NatalHiddenTalents` | placements |
| Potentiel relationnel | `NatalRelationshipPotential` | placements |
| Potentiel professionnel | `NatalCareerPotential` | placements |
| Mode astrologue | `NatalAstrologerMode` | entitlement premium, replié par défaut |
| Détails techniques | `NatalTechnicalDetails` | sous mode astrologue |
| Panneau expert | `NatalExpertPanel` | sous mode astrologue |
| Guide | `NatalChartGuide` | `missingBirthTime` |

Dans `NatalInterpretationContent`: résumé, highlights, accordéon sections V1/V2/V3, conseils, `EvidenceTags`, panneau projections B2C (`AstrologyProjectionsPanel`).

## 2. Matrice lecteur / information / owner / décision

| Information | Lecteur actuel | Owner actuel | Owner cible | Décision |
|---|---|---|---|---|
| Soleil / Lune / Ascendant lisibles | Débutant | `NatalProfileHero` | `NatalProfileHero` | **Conserver** (sans codes moteur en traits) |
| `dominant_topics`, `dominant_axes`, `narrative_priorities` | Fuite → débutant | `interpretation_adapter` via hero | — | **Retirer** de la vue publique |
| Synthèse LLM (titre, résumé, sections) | Débutant / passionné | `NatalInterpretation` | `NatalNarrativeReading` | **Migrer** vers 5 chapitres narratifs |
| `explanation_facts` concaténés | Passionné confus | `NatalAstrologicalDna` | — | **Retirer** de la vue principale |
| Cartes domaines / forces / défis / karmique / talents / relation / carrière | Passionné sans fil | composants sprint 2–3 | — | **Retirer** de la composition principale |
| Projections `beginner_summary_v1` / `client_interpretation_projection_v1` | Observabilité produit | `InterpretationContent` | backend-only | **Retirer** de la lecture publique |
| `EvidenceTags` (IDs `SUN_TAURUS_H10`) | Passionné curieux | `NatalInterpretationEvidence` | `NatalReadingSources` | **Remplacer** par justification vulgarisée |
| Scores, signaux, `audit_input`, JSON expert | Astrologue | `NatalExpertPanel` | `NatalAstrologerMode` | **Conserver** derrière toggle premium |
| Positions / maisons / aspects bruts | Astrologue | `NatalTechnicalDetails` | mode astrologue | **Conserver** |

## 3. Fuites techniques publiques (liste finie)

1. Codes adapter (`visibility_expression`, `dominant_topics`, `dominant_axes`, `narrative_priorities`) dans le hero.
2. `explanation_facts` et signaux calculatoires dans `NatalAstrologicalDna`.
3. Fallback placements (`planet_code`, `house_number`) quand le texte interprété manque (Challenges, Relationship, Career, etc.).
4. `EvidenceTags` exposant des identifiants evidence bruts en `title` DOM.
5. Panneau projections B2C (`projection_version`, `support_elements`, `interpretive_signal_ids`, `audit_input`) mélangé à la narration.
6. Métadonnées techniques dans l'en-tête (`reference_version`) — acceptable produit ; pas une fuite moteur.

## 4. Architecture cible (3 couches)

```text
Couche 1 — Lecture narrative (vue principale)
  Hero court → 5 chapitres (personnalité, monde émotionnel, relations, vocation, chemin d'évolution)

Couche 2 — Justification (fin de lecture, repliée)
  « Ce que nous avons utilisé » ← used_astrological_elements (contrat narrative_natal_reading_v1)

Couche 3 — Mode astrologue (premium, replié, fin de page)
  NatalTechnicalDetails + NatalExpertPanel
```

Politique éditoriale: ~80 % interprétation / ~20 % justification vulgarisée ; aucun score ni trace LLM en couche 1–2.

## 5. Carte de dépendances CS-391 → CS-395

| Story | Livrable | Dépend de |
|---|---|---|
| CS-391 | Contrat `narrative_natal_reading_v1` + exemples JSON | CS-390 |
| CS-392 | Schéma Pydantic, validation denylist, persistance | CS-391 |
| CS-393 | `NatalNarrativeReading`, refonte `NatalChartPage` | CS-390, CS-392 |
| CS-394 | `NatalReadingSources` | CS-392, CS-393 |
| CS-395 | Gardes + rapport non-régression + RG-152/153 | CS-390–394 |

## 6. Captures navigateur

Preuve visuelle complémentaire (2026-05-30, post CS-395) :

- **Automatisée** : gardes DOM Vitest (`natalPublicDomGuard`, `NatalChartPage` CS-395) prouvent l'absence de fuites techniques dans la lecture publique narrative.
- **Manuelle recommandée** : captures desktop/mobile annotées sur `/natal` avec l'utilisateur test après déploiement (non bloquante si les gardes RG-154 passent).
- Baseline structurelle sprint antérieur : `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/evidence/`, `_condamad/stories/CS-387-refonte-natal-sprint2-interpretation-approfondie/evidence/`.

## Invariants consultés

RG-071, RG-073, RG-129, RG-150, RG-151 — aucun assouplissement prévu.
