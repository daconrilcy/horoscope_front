# Brief de stories — Astrology Engine Gap & Productization Audit

## Contexte

Ce brief prepare la vague d'audits a mener apres l'etat post-CS-236 du moteur de theme astral.

Source principale :

- `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md`

Constat de depart :

- le runtime interne `chart_objects` est devenu canonique ;
- le graphe `natal_chart_v1` orchestre maintenant les calculs natals ;
- plusieurs surfaces puissantes restent volontairement internes ;
- le contrat public reste une projection stable et ne doit pas exposer le runtime brut ;
- les prochaines stories doivent etre decidees a partir de gaps produits, astronomiques, interpretatifs et de gouvernance, pas seulement a partir de ce qui existe deja techniquement.

Objectif global :

```text
determiner ce qu'il faut ajouter, exposer, renforcer ou differer
a partir de l'etat post-CS-236.
```

Ordre recommande :

1. Audit de couverture astrologique.
2. Audit des surfaces internes a exposer.
3. Audit du modele `chart_objects`.
4. Audit de gouvernance du referentiel.
5. Audit d'exactitude astronomique.
6. Audit du graphe de calcul.
7. Audit frontiere calcul / interpretation.
8. Audit produit / UX des donnees astrologiques.

Execution conseillee en premiere vague :

1. `ASTRO-AUDIT-01` — Astrology Engine Feature Coverage Audit.
2. `ASTRO-AUDIT-02` — Runtime Surface Exposure Audit.

Ces deux audits doivent produire les decisions qui orienteront les futures stories CS-237+.

---

# ASTRO-AUDIT-01 — Astrology Engine Feature Coverage Audit

## Objectif

Determiner quelles techniques astrologiques le moteur doit couvrir, lesquelles sont deja couvertes, et quelles lacunes doivent devenir des stories produit ou techniques.

Question centrale :

```text
Quelles techniques astrologiques voulons-nous couvrir,
et lesquelles sont deja couvertes par le moteur ?
```

## Livrable

Creer :

```text
docs/audits/astro/astrology-engine-feature-coverage-audit.md
```

## Perimetre d'audit

Auditer au minimum :

- theme natal structurel ;
- dignites essentielles ;
- dignites accidentelles ;
- conditions planetaires avancees ;
- sect, hayz, rejoicing ;
- parts arabes / lots ;
- noeuds, Lilith, apsides ;
- etoiles fixes ;
- parans ;
- midpoints ;
- asteroides ;
- Chiron ;
- transits ;
- progressions ;
- revolutions solaires et lunaires ;
- synastrie ;
- composite ;
- profections ;
- directions symboliques ;
- firdaria / time lords, si pertinent cote astrologie traditionnelle.

## Matrice attendue

Le document doit contenir une matrice avec les colonnes suivantes :

| Technique / objet / condition | Statut actuel | Niveau de couverture | Dependances runtime | Tables necessaires | Calculateur necessaire | Projection publique necessaire | Priorite produit |
| --- | --- | --- | --- | --- | --- | --- | --- |

Les statuts autorises sont strictement :

- `implemented`
- `partially implemented`
- `reference-only`
- `missing`
- `out-of-scope`

## Analyse attendue

Pour chaque sujet, l'audit doit expliciter :

- les fichiers backend qui prouvent l'etat actuel ;
- les contrats runtime existants ou manquants ;
- les donnees de reference disponibles ou absentes ;
- le niveau de maturite produit ;
- le risque de construire une UI ou une interpretation sur une surface incomplete ;
- les stories recommandees, separees entre calcul, reference, projection publique et UX.

## Hors scope

Ne pas implementer de nouvelle technique astrologique.

Ne pas modifier le contrat API.

Ne pas exposer `chart_objects`.

## Acceptance Criteria

### AC-1

Le fichier `docs/audits/astro/astrology-engine-feature-coverage-audit.md` existe et couvre tous les sujets listes.

### AC-2

Chaque sujet possede un statut parmi les cinq statuts autorises.

### AC-3

Chaque statut est justifie par des references concretes au code, aux tests ou aux documents existants.

### AC-4

L'audit distingue clairement :

- ce qui est calcule ;
- ce qui existe seulement dans le referentiel ;
- ce qui est expose publiquement ;
- ce qui est utilisable par l'interpretation ;
- ce qui manque totalement.

### AC-5

L'audit conclut par une priorisation produit des prochaines stories.

## Definition of Done

- Document relu et structure comme une source de backlog.
- Aucun changement applicatif.
- Aucun test backend/frontend requis sauf si un script d'inventaire est ajoute.
- Si un script Python est ajoute, il doit etre execute dans le venv conformement a `AGENTS.md`.

---

# ASTRO-AUDIT-02 — Runtime Surface Exposure Audit

## Objectif

Decider quelles surfaces internes du moteur doivent rester internes, etre projetees publiquement, ou etre exposees uniquement en admin/debug.

Constat de depart :

```text
chart_objects est canonique en interne,
mais exclu du contrat public.
```

Toute exposition frontend doit donc passer par une projection stable dediee.

## Livrable

Creer :

```text
docs/audits/astro/astrology-runtime-surface-exposure-audit.md
```

## Surfaces a auditer

Auditer au minimum :

- `chart_objects` ;
- `advanced_planetary_conditions` ;
- contacts d'etoiles fixes ;
- profils de signes enrichis ;
- `interpretation_input` ;
- hints internes d'aspects ;
- profils de condition ;
- payloads de dominance ;
- payloads de dignite.

## Matrice attendue

| Surface interne | Utilite produit | Risque d'exposition | Stabilite du contrat | Besoin frontend | Besoin admin/debug | Besoin LLM/interpretation | Exposition recommandee |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Decisions attendues

L'audit doit produire des decisions explicites du type :

```text
chart_objects:
- ne pas exposer brut au frontend public ;
- creer une projection controlee `chart_facts` ;
- reserver le runtime complet a un endpoint admin/debug protege.
```

Autre exemple :

```text
fixed_star_contacts:
- exposable cote produit ;
- projection dediee obligatoire ;
- ne pas exposer `ChartObjectRuntimeData` brut.
```

## Stories candidates a produire en sortie

L'audit doit qualifier ou reformuler ces stories candidates :

- CS-237 — Define public chart facts projection contract.
- CS-238 — Expose fixed star contacts through stable public projection.
- CS-239 — Add debug/admin endpoint for internal calculation graph trace.

## Hors scope

Ne pas ajouter d'endpoint.

Ne pas modifier les serializers publics.

Ne pas exposer de surface runtime brute.

## Acceptance Criteria

### AC-1

Le fichier `docs/audits/astro/astrology-runtime-surface-exposure-audit.md` existe.

### AC-2

Chaque surface auditee possede une recommandation explicite :

- rester interne ;
- projection publique dediee ;
- projection interpretation/LLM ;
- endpoint admin/debug ;
- deprecier ;
- differer.

### AC-3

L'audit identifie les risques de stabilite, securite, confusion produit et couplage frontend.

### AC-4

`chart_objects` n'est jamais recommande comme contrat public brut.

### AC-5

Les stories candidates post-audit sont ordonnees et justifiees.

## Definition of Done

- Document exploitable directement pour creer les stories CS-237+.
- Decisions separees entre public, admin/debug et interpretation interne.
- Aucun changement applicatif.

---

# ASTRO-AUDIT-03 — Chart Object Capability & Payload Audit

## Objectif

Auditer la taxonomie runtime `ChartObjectRuntimeData` pour verifier que les capacites, payloads et consommateurs respectent une semantique stable.

## Livrable

Creer :

```text
docs/audits/astro/chart-object-capability-payload-audit.md
```

## Matrice attendue

| Object type | Capabilities | Payloads requis | Payloads optionnels | Calculateurs consommateurs | Calculateurs producteurs | Projection publique | Projection interpretative |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Questions obligatoires

- Toutes les capacites ont-elles une semantique claire ?
- Un payload peut-il exister sans capacite correspondante ?
- Une capacite peut-elle etre vraie sans payload requis ?
- Les etoiles fixes sont-elles des objets ou seulement des sources de contacts ?
- Les angles doivent-ils participer aux aspects ?
- Les cuspides doivent-elles devenir aspectables ?
- Les lots doivent-ils avoir dignites, aspects, maisons ou dominance ?
- Les noeuds doivent-ils etre traites comme planetes, points ou categorie dediee ?

## Stories candidates a produire en sortie

- CS-246 — Formalize chart object capability matrix.
- CS-247 — Add runtime validation for capability/payload consistency.
- CS-248 — Add support for derived calculated points as first-class chart objects.

## Acceptance Criteria

### AC-1

Chaque type d'objet runtime actif est inventorie.

### AC-2

Chaque capacite possede une regle d'eligibilite et une consequence calculatoire.

### AC-3

Les incoherences capacite/payload potentielles sont listees avec une recommandation de validation.

---

# ASTRO-AUDIT-04 — Astrology Reference Governance Audit

## Objectif

Auditer la gouvernance des regles astrologiques, seuils, poids et profils entre Python, DB et documentation doctrinale.

## Livrable

Creer :

```text
docs/audits/astro/astrology-reference-governance-audit.md
```

## Matrice attendue

| Regle metier | Source actuelle | DB ou Python | Versionnee | Testee | Doctrine astrologique associee | Modifiable sans code |
| --- | --- | --- | --- | --- | --- | --- |

## Regles a classer

- orbes ;
- poids de dominance ;
- seuils de combustion ;
- seuils de cazimi ;
- seuils d'under beams ;
- seuils de vitesse ;
- seuils de station ;
- poids des maisons ;
- poids des dignites ;
- profils de signes ;
- regles fixed stars ;
- regles d'aspects ;
- regles d'interpretation.

## Stories candidates a produire en sortie

- CS-249 — Inventory astrology rule sources and static thresholds.
- CS-250 — Move planetary condition thresholds to versioned runtime reference.
- CS-251 — Add reference governance tests for rule source ownership.

## Acceptance Criteria

### AC-1

Les regles critiques sont reliees a une source unique ou a une dette explicite.

### AC-2

Les seuils hardcodes restants sont listes avec leur justification ou leur migration recommandee.

### AC-3

L'audit distingue doctrine astrologique, parametrage runtime et presentation produit.

---

# ASTRO-AUDIT-05 — Astronomical Accuracy Audit

## Objectif

Verifier si le moteur est fiable astronomiquement, et pas seulement coherent architecturalement.

## Livrable

Creer :

```text
docs/audits/astro/astrology-astronomical-accuracy-audit.md
```

## Points a verifier

- usage reel de `swisseph` en production ;
- interdiction du moteur simplifie hors test/dev ;
- version et hash des fichiers d'ephemerides ;
- reproductibilite des positions ;
- gestion UTC, timezone et DST ;
- coherence UT vs TT ;
- ayanamsa sideral ;
- topocentric ;
- altitude ;
- maisons aux hautes latitudes ;
- Placidus quand le systeme echoue ou devient instable ;
- comparaison avec jeux de reference.

## Golden charts obligatoires

Le document doit definir ou recommander un jeu de golden charts :

- Paris normal case ;
- DST ambiguous time ;
- DST nonexistent time ;
- high latitude case ;
- Sidereal Lahiri case ;
- topocentric case ;
- whole sign case ;
- Placidus edge case.

## Stories candidates a produire en sortie

- CS-240 — Enforce swisseph-only production calculation mode.
- CS-241 — Add astronomical golden chart regression suite.
- CS-242 — Persist ephemeris configuration evidence in chart_result trace.

## Acceptance Criteria

### AC-1

L'audit identifie clairement le mode de calcul actif selon environnement.

### AC-2

Les risques astronomiques sont separes des risques d'architecture.

### AC-3

Chaque golden chart attendue possede un objectif de validation.

---

# ASTRO-AUDIT-06 — Calculation Graph Readiness Audit

## Objectif

Auditer si `natal_chart_v1` et le runner peuvent servir de base aux futures familles de graphes.

Graphes futurs cibles :

- `transit_chart_v1` ;
- `synastry_chart_v1` ;
- `solar_return_v1` ;
- `progressed_chart_v1` ;
- `composite_chart_v1`.

## Livrable

Creer :

```text
docs/audits/astro/astrology-calculation-graph-readiness-audit.md
```

## Questions obligatoires

- Le runner supporte-t-il plusieurs graphes ?
- Les nodes sont-elles vraiment pures ?
- Les outputs sont-ils types ?
- Les dependances sont-elles declarees et testees ?
- Peut-on tracer l'execution d'un graphe ?
- Peut-on rejouer un graphe ?
- Peut-on versionner un graphe ?
- Peut-on comparer deux graphes ?
- Le cache local du runner suffit-il ou faut-il un cache applicatif ?
- Comment invalider par version de referentiel ?

## Stories candidates a produire en sortie

- CS-243 — Add calculation graph execution trace contract.
- CS-244 — Add graph manifest and node IO schema validation.
- CS-245 — Prepare graph runner for multi-chart graph families.

## Acceptance Criteria

### AC-1

L'audit separe cache local, cache applicatif, provenance, debug trace et replay.

### AC-2

Les limites actuelles du runner sont documentees avec preuves.

### AC-3

Les prerequisites pour chaque famille de graphe sont listes.

---

# ASTRO-AUDIT-07 — Calculation / Interpretation Boundary Audit

## Objectif

Verrouiller la frontiere doctrinale entre calcul, signaux astrologiques, interpretation, texte et prompt LLM.

## Livrable

Creer :

```text
docs/audits/astro/calculation-interpretation-boundary-audit.md
```

## Grille attendue

| Element | Categorie | Owner | Surface runtime | Surface publique | Risque de confusion |
| --- | --- | --- | --- | --- | --- |

Categories attendues :

- fait astronomique ;
- fait astrologique structurel ;
- scoring structurel ;
- signal interpretatif ;
- texte ;
- prompt LLM ;
- projection produit.

Exemples a utiliser :

- longitude Mars = fait astronomique ;
- Mars maison 10 = fait astrologique structurel ;
- Mars dominant = scoring structurel ;
- Mars combatif = interpretation ;
- "Vous avez une energie de conquete" = narration.

## Stories candidates a produire en sortie

- CS-252 — Define ChartInterpretationInput public/internal contract.
- CS-253 — Add interpretation-readiness projection from structural facts.
- CS-254 — Guard against narrative tokens in calculation runtime.

## Acceptance Criteria

### AC-1

L'audit classe les principales surfaces du moteur selon la grille.

### AC-2

Les violations potentielles de frontiere sont listees.

### AC-3

Les recommandations distinguent contrat interne, contrat public et contrat LLM.

---

# ASTRO-AUDIT-08 — Astrology Product Data Needs Audit

## Objectif

Determiner quelles donnees astrologiques les ecrans produit doivent afficher, sans exposer des surfaces internes par opportunisme technique.

## Livrable

Creer :

```text
docs/audits/astro/astrology-product-data-needs-audit.md
```

## Ecrans cibles

Auditer les besoins de donnees pour :

- theme natal simple ;
- theme expert ;
- debug astrologique ;
- analyse de dominantes ;
- analyse des aspects ;
- analyse traditionnelle ;
- analyse des etoiles fixes ;
- interpretation IA ;
- export PDF ;
- interface astrologue ;
- interface utilisateur grand public.

## Questions par ecran

- Quelle donnee est necessaire ?
- La donnee existe-t-elle ?
- Est-elle publique ?
- Est-elle stable ?
- Est-elle comprehensible ?
- Faut-il une projection dediee ?
- Faut-il une traduction ?
- Faut-il un score ?
- Faut-il masquer la complexite ?

## Matrice attendue

| Ecran | Donnee necessaire | Existe | Publique | Stable | Projection dediee | Traduction | Score | Complexite a masquer | Story recommandee |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Stories candidates a produire en sortie

- CS-255 — Define expert natal chart public data contract.
- CS-256 — Define beginner natal chart summary projection.
- CS-257 — Add fixed-star section projection for frontend display.

## Acceptance Criteria

### AC-1

Chaque ecran cible possede une liste de donnees necessaires.

### AC-2

L'audit identifie les donnees qui existent mais ne doivent pas etre exposees brutes.

### AC-3

Les recommandations UI sont reliees a des projections publiques dediees.

---

# Synthese de priorisation

## Premiere vague recommandee

Executer d'abord :

1. `ASTRO-AUDIT-01` — couverture astrologique.
2. `ASTRO-AUDIT-02` — exposition des surfaces internes.

Ces deux audits doivent repondre a la question :

```text
La prochaine vague doit-elle etre technique, produit, astronomique,
interpretative ou orientee nouvelles techniques astrologiques ?
```

## Deuxieme vague recommandee

Executer ensuite :

1. `ASTRO-AUDIT-03` — modele `chart_objects`.
2. `ASTRO-AUDIT-04` — gouvernance du referentiel.

Ces audits verrouillent la maintenabilite avant d'ajouter de nouvelles techniques.

## Troisieme vague recommandee

Executer ensuite :

1. `ASTRO-AUDIT-05` — exactitude astronomique.
2. `ASTRO-AUDIT-06` — graphe de calcul.

Ces audits preparent les garanties runtime et les futurs graphes.

## Quatrieme vague recommandee

Executer enfin :

1. `ASTRO-AUDIT-07` — frontiere calcul / interpretation.
2. `ASTRO-AUDIT-08` — besoins produit / UX.

Ces audits alignent interpretation, LLM, API publique et frontend.

---

# Contraintes transverses pour toutes les stories d'audit

## Ne pas confondre audit et implementation

Chaque story d'audit doit produire un document de decision, pas un changement applicatif.

Toute implementation detectee doit etre sortie en story separee.

## Preuves obligatoires

Chaque conclusion doit pointer vers au moins une preuve :

- fichier backend ;
- test ;
- document d'architecture ;
- contrat public ;
- schema Pydantic ;
- seed ou table de reference ;
- absence verifiee par recherche.

## Format de conclusion obligatoire

Chaque audit doit finir par :

- decisions ;
- risques ;
- quick wins ;
- stories candidates ;
- stories a differer ;
- points a arbitrer par le produit.

## Regle de non-exposition

Aucun audit ne doit recommander l'exposition brute de `ChartObjectRuntimeData` au frontend public.

Les expositions recommandees doivent passer par :

- projection publique stable ;
- projection LLM/interne ;
- endpoint admin/debug protege ;
- ou maintien strict en interne.
