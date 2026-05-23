# ASTRO-ARCHI-01 — Canonical Astrology Runtime Product Architecture

## Résumé

Produire l'architecture produit qui transforme les constats des audits CS-237 à CS-244 en plan de plateforme astrologique.

L'objectif n'est plus de vérifier si le moteur natal fonctionne. L'objectif est de décider si, comment et dans quel ordre `ChartObjectRuntimeData` et `CalculationGraph` deviennent le runtime canonique transversal de l'astrologie du produit.

Livrable attendu :

```text
_condamad/architecture/astro-canonical-runtime-transition/<YYYY-MM-DD-HHMM>/
```

Le dossier d'architecture CONDAMAD doit contenir les fichiers suivants :

- `00-architecture-plan.md` avec la synthèse transverse, les matrices de décision et le plan d'architecture produit ;
- `01-evidence-log.md` avec les preuves reproductibles issues du code, des tests, des stories et des audits CS-237 à CS-244 ;
- `02-gap-register.md` avec les écarts qui empêchent le runtime canonique de devenir transversal ;
- `03-story-candidates.md` avec les stories candidates priorisées et remappées vers des IDs disponibles ;
- `04-risk-matrix.md` avec les risques architecture, produit, exposition, doctrine, cache, trace, replay et narration ;
- `05-executive-summary.md` avec la synthèse décisionnelle exploitable pour arbitrage produit/technique.

## Contexte

Les audits post-CS-236 montrent que le moteur natal dispose désormais de fondations solides :

- `ChartObjectRuntimeData` comme surface runtime interne des objets du thème ;
- `CalculationGraph` et `natal_chart_v1` comme orchestration calculatoire ;
- projections publiques contrôlées, sans exposition brute de `chart_objects` ;
- séparation calcul, interprétation, prompt LLM et projection produit ;
- gouvernance partielle des référentiels, poids, seuils et profils astrologiques ;
- bornage explicite des limites : visibilité simplifiée, étoiles fixes limitées aux conjonctions, moteur simplifié non astronomique, absence de cache applicatif global.

Le changement de phase à architecturer est le suivant :

```text
ChartObjectRuntimeData
+
CalculationGraph
=
base commune potentielle de l'astrologie produit
```

Cette base pourrait porter :

- thème natal ;
- transits ;
- synastrie ;
- progressions ;
- révolutions solaires et lunaires ;
- profections ;
- forecasting ;
- scoring IA ;
- génération narrative ;
- debug astrologique ;
- interface astrologue ;
- projections publiques débutant/expert.

## Sources obligatoires

La story d'architecture doit lire et citer explicitement les audits suivants :

- `_condamad/audits/astro-feature-coverage/2026-05-23-1905/`
- `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919/`
- `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928/`
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/`
- `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950/`
- `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000/`
- `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013/`
- `_condamad/audits/astro-product-data-needs/2026-05-23-2024/`

La story d'architecture doit aussi consulter les stories source associées :

- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md`
- `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md`
- `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md`
- `_condamad/stories/CS-240-audit-reference-governance/00-story.md`
- `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md`
- `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md`
- `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md`
- `_condamad/stories/CS-244-audit-product-data-needs/00-story.md`

## Questions obligatoires

### Runtime canonique

- `ChartObjectRuntimeData` peut-il devenir le contrat interne commun pour toutes les familles astrologiques ?
- Quelles données sont communes entre natal, transit, synastrie, progression, return, profection, forecasting et scoring ?
- Quelles données doivent rester spécifiques à une famille ?
- Quelles capacités doivent être portées par l'objet lui-même et lesquelles doivent rester au niveau graphe, relation ou projection ?
- Faut-il un registre canonique des familles de graphes ?

### CalculationGraph

- `CalculationGraph` est-il le bon mécanisme transversal pour orchestrer les familles non natales ?
- Quelles familles peuvent partager le runner actuel sans modification majeure ?
- Quelles familles exigent des graphes multi-chart, multi-date ou multi-techniques ?
- Quels prérequis manquent encore : manifest, node IO schemas, trace, replay, comparaison, versioning, cache applicatif, invalidation ?
- Quelle est la frontière entre cache local de runner et cache produit durable ?

### Surfaces internes et produit

- Quelles surfaces deviennent des primitives produit officielles ?
- Quelles surfaces doivent rester internes ?
- Quelles surfaces peuvent être exposées uniquement via admin/debug protégé ?
- Quelles projections publiques sont nécessaires pour utilisateur débutant, expert, astrologue et export PDF ?
- Quelles surfaces sont autorisées comme entrée d'interprétation LLM sans devenir API publique ?

### Objets astrologiques

- Quelle doctrine d'objet faut-il appliquer à planète, luminaire, angle, noeud, Lilith, apside, lot, astéroïde, Chiron, midpoint et étoile fixe ?
- Quelles familles d'objets sont positionnelles, aspectables, interprétables, scorables, dignité-éligibles ou dominance-éligibles ?
- Quels objets nécessitent une source astronomique, un calcul symbolique, une table DB ou une règle produit ?
- Comment éviter les branches ad hoc par type d'objet ?

### Techniques temporelles et multi-techniques

- Quelle première technique temporelle doit être implémentée après le natal ?
- Faut-il prioriser transits, synastrie, solar return, progressed chart, composite, profections ou forecasting ?
- Quelles techniques exigent plusieurs thèmes, plusieurs dates ou une relation entre objets ?
- Quelles sorties doivent alimenter le scoring IA et la génération narrative ?

### Doctrine et écoles astrologiques

- Quelles décisions relèvent de la doctrine astrologique plutôt que de l'architecture logicielle ?
- Comment classer DB-owned, Python-owned, documentation-only, test-only, mixed et needs-user-decision ?
- Faut-il introduire une gouvernance des écoles astrologiques avant d'ajouter des techniques traditionnelles, hellénistiques, modernes ou prévisionnelles ?
- Comment empêcher qu'une valeur doctrinale soit modifiée sans source, version ou décision explicite ?

### Narration, IA et produit

- Quelle donnée structurelle doit être disponible avant narration ?
- Quelle donnée interprétative pré-narrative doit rester séparée du prompt final ?
- Quel minimum déterministe faut-il pour scoring IA, forecasting et génération narrative ?
- Quels contrats évitent que les prompts deviennent une source de vérité astrologique ?

## Matrice obligatoire 1 — Familles runtime

Le plan d'architecture doit contenir une matrice avec au minimum les colonnes suivantes :

| Famille | Statut actuel | Runtime canonique cible | Inputs requis | Graph requis | Objets requis | Surfaces publiques | Surfaces internes | Trace/replay requis | Cache/invalidation | Blockers | Story recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Familles obligatoires :

- `natal_chart_v1`
- `transit_chart_v1`
- `synastry_chart_v1`
- `solar_return_v1`
- `lunar_return_v1`
- `progressed_chart_v1`
- `composite_chart_v1`
- `profection_v1`
- `forecasting_v1`
- `ai_scoring_v1`
- `narrative_generation_v1`

Statuts autorisés :

- `implemented`
- `partially-ready`
- `reference-only`
- `missing`
- `blocked-by-product-decision`
- `blocked-by-doctrine-decision`
- `out-of-scope`

## Matrice obligatoire 2 — Surfaces et exposition

Le plan d'architecture doit contenir une matrice avec au minimum les colonnes suivantes :

| Surface | Owner actuel | Statut cible | Public API | Admin/debug | LLM/input | Frontend | Risque d'exposition brute | Projection requise | Guard requis | Story recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Surfaces obligatoires :

- `ChartObjectRuntimeData`
- `chart_objects`
- `CalculationGraphDefinition`
- `CalculationGraphRunner`
- `CalculationGraphExecutionResult`
- provenance
- trace d'exécution
- replay snapshot
- graph manifest
- node IO schema
- fixed-star contacts
- advanced planetary conditions
- dignities
- dominance
- aspects structural data
- interpretation input
- chart facts projection
- beginner summary projection
- expert technical projection

## Matrice obligatoire 3 — Objets astrologiques

Le plan d'architecture doit contenir une matrice avec au minimum les colonnes suivantes :

| Objet | Type canonique proposé | Source calcul/référence | Positionnel | Aspectable | Interprétable | Scorable | Dignité-éligible | Dominance-éligible | Projection publique | Décision requise |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Objets obligatoires :

- Soleil ;
- Lune ;
- planètes classiques ;
- planètes modernes ;
- ASC/MC/angles ;
- noeuds lunaires ;
- Lilith ;
- apsides ;
- parts arabes/lots ;
- astéroïdes ;
- Chiron ;
- midpoints ;
- étoiles fixes.

## Matrice obligatoire 4 — Roadmap d'architecture produit

Le plan d'architecture doit proposer un ordre de mise en oeuvre avec au minimum :

| Rang | Chantier | Pourquoi maintenant | Dépendances | Risque si ignoré | Taille estimée | Story candidate |
| --- | --- | --- | --- | --- | --- | --- |

Cette roadmap doit distinguer :

- prérequis de plateforme ;
- premières surfaces produit ;
- premières techniques temporelles ;
- gouvernance doctrine/références ;
- garde-fous anti-exposition brute ;
- amélioration de preuve astronomique ;
- narration/IA.

## Stories candidates à qualifier

La story d'architecture doit qualifier des stories candidates remappées vers les prochains IDs disponibles, sans réutiliser les labels source déjà conflictuels signalés par CS-242.

Les candidats minimaux attendus sont :

- Define canonical astrology graph family registry.
- Add graph manifest and node IO schema contract for canonical runtime.
- Add calculation graph execution trace contract.
- Define chart object capability and object taxonomy matrix.
- Define official product primitives and public projection roadmap.
- Select first temporal technique implementation path.
- Define astrology doctrine and school governance model.
- Define AI scoring and narrative input contract from canonical runtime.

Chaque candidat doit inclure :

- source findings depuis CS-237 à CS-244 ;
- priorité ;
- domaine primaire ;
- fichiers probables à modifier ;
- fichiers explicitement hors périmètre ;
- validation attendue ;
- stop condition ;
- décisions utilisateur requises.

## Périmètre inclus

1. Synthèse architecturale des audits CS-237 à CS-244.
2. Consolidation des findings redondants ou contradictoires.
3. Identification des décisions produit/architecture encore manquantes.
4. Définition d'une doctrine de runtime canonique pour `ChartObjectRuntimeData` et `CalculationGraph`.
5. Cartographie des familles astrologiques futures.
6. Cartographie des surfaces internes, publiques, admin/debug et LLM.
7. Cartographie des objets astrologiques et de leurs capacités.
8. Roadmap d'architecture produit en stories priorisées.
9. Remapping des labels de stories conflictuels vers des IDs disponibles.

## Hors périmètre

Ne pas modifier le backend applicatif.

Ne pas modifier le frontend.

Ne pas ajouter de nouveau graphe.

Ne pas ajouter d'endpoint.

Ne pas changer les serializers.

Ne pas ajouter de cache applicatif.

Ne pas modifier les seeds, migrations ou référentiels DB.

Ne pas décider une doctrine astrologique à la place du produit : marquer `needs-user-decision` quand l'arbitrage est doctrinal, éditorial ou commercial.

## Critères d'acceptation

1. Le dossier d'architecture existe sous `_condamad/architecture/astro-canonical-runtime-transition/`.
2. Les huit audits CS-237 à CS-244 sont cités avec preuves concrètes.
3. Les quatre matrices obligatoires sont présentes et complètes.
4. Chaque famille runtime obligatoire possède un statut autorisé, un owner cible et au moins un blocker ou une next action.
5. `ChartObjectRuntimeData` et `CalculationGraph` sont évalués explicitement comme primitives internes, pas implicitement exposés.
6. Les surfaces publiques, internes, admin/debug, frontend et LLM sont séparées.
7. Les objets astrologiques obligatoires sont classés avec capacités et décisions requises.
8. La roadmap distingue les prérequis de plateforme des fonctionnalités produit.
9. Les stories candidates sont priorisées et ne réutilisent pas des IDs déjà alloués sans remapping explicite.
10. Aucun changement applicatif n'est introduit.

## Validation attendue

Validation documentaire :

```powershell
$archiFolder = Get-ChildItem -Directory .\_condamad\architecture\astro-canonical-runtime-transition | Sort-Object Name -Descending | Select-Object -First 1
rg -n "CS-237|CS-238|CS-239|CS-240|CS-241|CS-242|CS-243|CS-244" "$($archiFolder.FullName)"
rg -n "ChartObjectRuntimeData|CalculationGraph|natal_chart_v1|transit_chart_v1|synastry_chart_v1|progressed_chart_v1|solar_return_v1|profection|forecasting|scoring|narrative" "$($archiFolder.FullName)\00-architecture-plan.md"
rg -n "blocked-by-product-decision|blocked-by-doctrine-decision|partially-ready|reference-only|missing|implemented" "$($archiFolder.FullName)\00-architecture-plan.md"
rg -n "Public API|Admin/debug|LLM|Frontend|Projection|Guard" "$($archiFolder.FullName)\00-architecture-plan.md"
```

Validation de non-modification applicative :

```powershell
git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations docs/db_seeder
```

Validation de cohérence documentaire :

```powershell
Test-Path "$($archiFolder.FullName)\00-architecture-plan.md"
Test-Path "$($archiFolder.FullName)\01-evidence-log.md"
Test-Path "$($archiFolder.FullName)\02-gap-register.md"
Test-Path "$($archiFolder.FullName)\03-story-candidates.md"
Test-Path "$($archiFolder.FullName)\04-risk-matrix.md"
Test-Path "$($archiFolder.FullName)\05-executive-summary.md"
```

## Formulation courte pour Codex

```markdown
Réalise ASTRO-ARCHI-01.

Crée un dossier d'architecture CONDAMAD sous _condamad/architecture/astro-canonical-runtime-transition/<YYYY-MM-DD-HHMM>/.
Produis l'architecture produit qui consolide CS-237 à CS-244 et transforme leurs constats en plan de plateforme astrologique.
Évalue explicitement si ChartObjectRuntimeData + CalculationGraph doivent devenir la base commune de natal, transit, synastrie, progressions, returns, profections, forecasting, scoring IA et génération narrative.

Le plan doit contenir :
- une matrice des familles runtime ;
- une matrice des surfaces et niveaux d'exposition ;
- une matrice des objets astrologiques et capacités ;
- une roadmap d'architecture produit priorisée ;
- des stories candidates remappées vers des IDs disponibles.

Interdictions :
- pas de changement applicatif ;
- pas de frontend ;
- pas de nouveau graphe ;
- pas d'endpoint ;
- pas d'exposition brute de ChartObjectRuntimeData ou chart_objects ;
- marquer needs-user-decision quand une décision relève de la doctrine, du produit ou de la sécurité.
```
