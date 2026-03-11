# Epic 42: Refonte du moteur daily v3 orienté signal continu

Status: draft-for-story-splitting

## Contexte

Le moteur daily actuel repose principalement sur une logique `event-driven` :

- détection d'événements discrets
- conversion de ces événements en contributions par catégorie
- agrégation journalière
- dérivation de pivots, fenêtres et textes

Cette architecture est saine techniquement, mais elle produit encore trop souvent :

- un signal trop sparse
- des notes écrasées autour du neutre
- des turning points trop faciles à produire
- des fenêtres publiques parfois plus riches que la force réelle du signal

L'objectif d'Epic 42 est de faire évoluer le daily vers un moteur `signal-driven` :

- calculer d'abord des courbes astro continues par thème et par pas de temps
- dériver ensuite orientation, intensité, confiance et rareté
- ne produire des pivots que lorsqu'il y a un vrai changement de régime
- exposer un `evidence pack` propre pour la projection publique et une future interprétation experte

## Objectif Produit

Construire un moteur daily v3 qui :

1. calcule un signal composite continu par thème
2. distingue clairement orientation, intensité, confiance et rareté
3. produit des blocs horaires et turning points crédibles, plus rares et plus utiles
4. garde les journées réellement plates plates, sans faux relief
5. prépare un futur flux d'interprétation expert/LLM à partir d'un `evidence pack`

## Non-objectifs

- ne pas casser immédiatement le contrat public actuel
- ne pas supprimer le moteur v2 tant que la bascule n'est pas validée
- ne pas introduire de LLM dans le calcul du signal
- ne pas maquiller une journée faible en journée vivante par simple tuning éditorial

## Principe de calcul cible

Pour chaque thème `c` et chaque pas de temps `t` :

`S(c,t) = alpha*B(c) + beta*T(c,t) + gamma*A(c,t) + delta*E(c,t)`

avec :

- `B(c)` : susceptibilité natale structurelle
- `T(c,t)` : climat de transit continu
- `A(c,t)` : activation intrajournalière locale
- `E(c,t)` : impulsions ponctuelles d'exactitude

Le signal est ensuite lissé avant toute dérivation produit.

## Versionning et coexistence v2/v3

La transition v2 -> v3 doit être explicitement versionnée à tous les niveaux du cycle de vie:

- `engine_version`
- `snapshot_version`
- `evidence_pack_version`

Ces versions doivent être injectées dans:

- l'`input_hash`
- la politique de réutilisation
- la persistance du run
- la lecture repository
- la comparaison QA v2/v3

Objectif: empêcher toute collision logique entre runs v2 et v3 pendant la coexistence.

## Mode d'exécution

Le moteur doit supporter très tôt les trois modes suivants:

- `v2`
- `v3`
- `dual`

Le mode `dual` permet d'exécuter v2 et v3 sur la même entrée pour comparer courbes, métriques, pivots et fenêtres dès les premières stories techniques.

## Sémantique à stabiliser tôt

### Confidence

`confidence` doit être définie tôt comme combinaison explicite de:

- part de signal expliqué
- stabilité de la courbe
- qualité de baseline disponible
- cohérence inter-drivers

### Rarity

`rarity_percentile` ne doit pas être confondu avec le simple percentile relatif utilisateur. Il représente la rareté du signal observé dans son espace de comparaison.

## Exigences de performance

Epic 42 n'est valide que si le moteur v3 reste exploitable en production. Les stories concernées doivent porter des SLO explicites sur:

- temps max de calcul d'un daily v3
- coût max des couches `T` et `A`
- temps max de calcul d'une baseline enrichie
- stabilité mémoire du pipeline

## Couches fonctionnelles

### 1. Socle astrologique continu

Le moteur doit produire des courbes par thème et par tranche de 15 minutes, plutôt qu'un simple chapelet d'événements.

### 2. Projection métier par thème

Chaque thème quotidien et chaque bloc doivent exposer :

- `score_20` d'orientation
- `intensity_20`
- `confidence_20`
- `rarity_percentile`

### 3. Calibration personnelle robuste

La baseline utilisateur doit être enrichie avec :

- baseline absolue journalière
- baseline intrajournalière par slot
- baseline mensuelle ou saisonnière légère

### 4. Interprétation à partir d'un evidence pack

Le public et un futur moteur d'interprétation doivent consommer une structure propre :

- profil global de journée
- thèmes dominants / faibles
- blocs horaires qualifiés
- vrais pivots
- drivers astrologiques explicites

## Découpage en chapitres

### Chapitre 1 — Socle signal continu

- 42.1 Formaliser le modèle de signal daily v3
- 42.2 Construire la susceptibilité natale structurelle
- 42.3 Construire le climat de transit continu
- 42.4 Construire l'activation intrajournalière
- 42.5 Repositionner la couche impulsionnelle

### Chapitre 2 — Métriques v3 et calibration multi-dimensionnelle

- 42.6 Produire score / intensité / confiance / rareté par thème
- 42.7 Refaire la calibration absolue sur courbes lissées
- 42.8 Étendre snapshot et persistance v3

### Chapitre 3 — Segmentation de régime, blocs et pivots

- 42.9 Segmenter la journée par changement de régime
- 42.10 Refaire les turning points comme changements de régime persistants
- 42.11 Refaire les decision windows à partir des blocs v3

### Chapitre 4 — Calibration personnelle robuste

- 42.12 Étendre la baseline utilisateur en trois niveaux
- 42.13 Refaire le scoring relatif v3
- 42.14 Refaire la logique des flat days et micro-trends

### Chapitre 5 — Evidence pack expert et interprétation

- 42.15 Introduire un evidence pack expert v3
- 42.16 Brancher projection publique et future couche LLM sur l'evidence pack
- 42.17 QA, backtesting et migration progressive

## Contraintes d'architecture

- Le moteur v3 doit être activable derrière feature flag.
- Le moteur v2 doit rester disponible pendant la phase de comparaison.
- Les nouveaux objets de calcul ne doivent pas fuiter directement dans le routeur FastAPI.
- La persistance doit rester audit-grade et versionnée.
- Les tests de non-régression doivent couvrir v2 et v3.

## Critères de réussite

- Les journées plates restent lisibles sans faux relief.
- Les journées intenses mais neutres ne sont plus écrasées autour de `10/20`.
- Les turning points deviennent plus rares et plus crédibles.
- Les blocs horaires deviennent des résumés de régimes, pas des effets de seuil.
- Le système produit un evidence pack suffisamment stable pour une future interprétation experte.

## Ordre d'implémentation recommandé

### Lot 1 — Moteur silencieux

- 42.1
- 42.2
- 42.3
- 42.4
- 42.5
- 42.6
- 42.7
- 42.8

Objectif:

- produire des courbes v3
- produire des métriques v3
- persister des snapshots v3
- sans impact produit public

### Lot 2 — Régimes, pivots, fenêtres

- 42.9
- 42.10
- 42.11

### Lot 3 — Evidence pack et projection

- 42.15
- 42.16

### Lot 4 — Relatif tardif et non bloquant

- 42.12
- 42.13
- 42.14

### Lot 5 — Backtesting et migration

- 42.17
