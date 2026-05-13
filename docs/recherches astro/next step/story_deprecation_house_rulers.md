# Story — Dépréciation progressive de `house_rulers[]`

Status: planned

## 1. Objective

Supprimer progressivement le champ legacy :

```json
house_rulers[]
```

au profit de la source canonique runtime :

```json
houses[*].ruler
```

sans casser :

- les payloads publics existants,
- les snapshots historiques,
- les projections IA,
- les évidences astrologiques,
- les prompts LLM,
- les consommateurs frontend,
- les exports ou analytics.

Cette story intervient après la convergence runtime des maisons riches et vise à éliminer la duplication structurelle des maîtres de maisons.

---

# 2. Contexte

Depuis la Priorité 3 Runtime Maisons Riches :

```text
houses[*].ruler
```

est devenu :

- la source canonique runtime,
- la représentation structurée des maîtrises,
- la donnée utilisée pour l’interprétation avancée.

Le champ :

```text
house_rulers[]
```

est désormais uniquement :

- une projection legacy,
- générée depuis `houses[*].ruler`,
- maintenue pour compatibilité.

Le contrat actuel documenté est :

```text
Source canonique runtime = houses[*].ruler
Projection legacy = house_rulers[]
```

---

# 3. Pourquoi supprimer `house_rulers[]`

Le maintien permanent des deux structures crée plusieurs risques :

## Risque 1 — duplication publique

Deux représentations du même concept :

```json
houses[*].ruler
```

et :

```json
house_rulers[]
```

augmentent :

- la complexité du payload,
- la dette cognitive,
- le coût de maintenance.

---

## Risque 2 — divergence future

Même avec les guardrails actuels :

- un futur refactor,
- un nouveau serializer,
- un consumer partiel,
- un export spécifique,

pourrait recréer une divergence silencieuse.

---

## Risque 3 — ambiguïté produit

Pour les consommateurs :

```text
quelle structure faut-il utiliser ?
```

La coexistence permanente empêche une API claire.

---

## Risque 4 — payload inflation

Les thèmes astrologiques riches deviennent déjà volumineux :

- occupants,
- interceptions,
- strengths,
- metadata,
- activations futures,
- overlays prédictifs.

Supprimer les doublons devient important.

---

# 4. Objectif cible

Payload cible final :

```json
{
  "houses": [
    {
      "number": 7,
      "cusp_sign": "taurus",
      "ruler": {
        "planet": "venus",
        "sign": "leo",
        "house": 10
      }
    }
  ]
}
```

Le champ :

```json
house_rulers[]
```

doit disparaître complètement.

---

# 5. Contraintes critiques

## Ne PAS casser brutalement :

- les prompts LLM existants,
- les snapshots golden,
- les consumers frontend,
- les exports,
- les évidences runtime,
- les analytics historiques.

---

## La suppression doit être progressive

Approche obligatoire :

```text
deprecated
→ migration des consumers
→ warning
→ suppression
```

Jamais :

```text
suppression immédiate
```

---

# 6. Étapes recommandées

# Phase 1 — Audit complet des consumers

Créer :

```text
_condamad/audits/house-rulers-deprecation/
```

Identifier tous les usages de :

```text
house_rulers
```

dans :

- frontend,
- projections IA,
- prompts,
- snapshots,
- builders,
- exports,
- analytics,
- tests,
- evidences,
- scripts.

Livrable :

```text
consumer inventory
```

avec :

- consumer,
- criticité,
- migration requise,
- statut.

---

# Phase 2 — Migration des consumers

Tous les consumers doivent migrer vers :

```text
houses[*].ruler
```

Interdictions :

- nouveau code utilisant `house_rulers[]`,
- nouveaux prompts utilisant `house_rulers[]`,
- nouvelles projections basées dessus.

---

# Phase 3 — Ajout d’un statut deprecated

Dans la doc publique :

```text
house_rulers[] is deprecated
Use houses[*].ruler instead
```

Ajouter également :

- changelog,
- release note,
- warning développeur.

---

# Phase 4 — Guardrails anti-réintroduction

Créer :

```text
test_no_new_consumers_of_house_rulers.py
```

Le test doit :

- scanner le codebase,
- détecter les nouveaux usages,
- autoriser uniquement :
  - serializer legacy,
  - tests legacy explicitement whitelistés,
  - compatibilité transitoire.

---

# Phase 5 — Suppression finale

Supprimer :

- `house_rulers[]`
- serializers legacy
- projections de compatibilité
- tests legacy
- snapshots legacy

Puis :

- mise à jour OpenAPI,
- mise à jour docs,
- mise à jour golden snapshots.

---

# 7. Architecture cible finale

## Canonique unique

```text
houses[*]
```

devient :

- la structure astrologique centrale,
- la source des rulers,
- la source des occupants,
- la source des strengths,
- la source IA.

---

## Interdiction permanente

Ne jamais réintroduire :

```text
house_rulers[]
```

comme structure parallèle.

---

# 8. Acceptance Criteria

## AC1 — audit complet

Tous les consumers identifiés.

---

## AC2 — migration

Aucun nouveau consumer métier ne lit :

```text
house_rulers[]
```

---

## AC3 — guardrails

Test empêchant toute réintroduction.

---

## AC4 — suppression finale

Le payload final ne contient plus :

```json
house_rulers[]
```

---

## AC5 — compatibilité IA

Tous les prompts et projections utilisent :

```text
houses[*].ruler
```

---

# 9. Non-objectifs

Cette story ne doit PAS :

- modifier le calcul des maîtrises,
- modifier les dignités,
- modifier les houses runtime,
- modifier les cuspides,
- modifier le moteur daily,
- modifier les evidences astrologiques métier.

---

# 10. Risques identifiés

## Risque principal

Certains prompts IA ou snapshots peuvent dépendre implicitement de :

```text
house_rulers[]
```

sans que ce soit documenté.

Le scan initial est donc critique.

---

# 11. Recommandation importante

Ne PAS planifier cette suppression immédiatement.

Priorité avant suppression :

- stabiliser le runtime riche,
- stabiliser les projections IA,
- stabiliser les narratifs,
- stabiliser les payloads publics.

La suppression doit intervenir uniquement lorsque :

```text
houses[*]
```

sera devenu :

- la structure centrale unique,
- consommée partout.
