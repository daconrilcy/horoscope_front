# Prédiction astrologique quotidienne personnalisée : catégories, méthode de calcul et découpage horaire

## Cadre du besoin et données nécessaires
L’objectif décrit correspond à une « météo du jour » personnalisée : on part d’un thème natal (positions planétaires et angles au moment de la naissance), auquel on superpose les configurations célestes d’une date/heure donnée (la journée de l’utilisateur) afin de produire :  
- une lecture thématique par catégories (santé, énergie, travail, argent, sexe, etc.) ;  
- une lecture temporelle (par tranches ou par heure), mettant en évidence des « faits émergents » et des « points de bascule » ;  
- une note enregistrable (échelle 1–20) par catégorie.  

Sur le plan épistémologique, l’astrologie est généralement décrite comme une forme de divination (et non comme une discipline scientifique) ; la littérature de vulgarisation scientifique insiste sur le fait qu’elle n’est pas considérée comme une science (au sens méthodologique). entity["company","Encyclopaedia Britannica","encyclopedia publisher"] présente l’astrologie comme une pratique de divination fondée sur l’interprétation des positions et mouvements des corps célestes. citeturn2search0 entity["organization","University of California, Berkeley","public university, berkeley ca"] (Understanding Science) explique pourquoi l’astrologie peut « ressembler » à une démarche scientifique sans en respecter les critères. citeturn2search21 entity["organization","NASA","us space agency"] a également communiqué à plusieurs reprises sur la distinction astronomie/astrologie, en rappelant que l’astrologie n’est pas une science. citeturn2news40  

Pour l’implémentation, deux conséquences pratiques découlent de ce cadre :  
- il est utile de présenter la production comme une guidance/lecture symbolique, et non comme une promesse d’événements factuels ;  
- certaines catégories (santé/argent) doivent être rédigées comme tendances/attentions et non comme diagnostics médicaux ou conseils financiers impératifs.

### Données à « injecter » (entrées) et précision attendue
Pour passer d’un horoscope générique à une prédiction personnalisée *basée sur thème natal + date/heure du jour*, il faut au minimum :

- **Données de naissance (thème natal)** : date, heure la plus précise possible, et lieu (au moins ville/pays, idéalement coordonnées). Les maisons/angles dépendent directement de l’heure et du lieu (rotation de la Terre). citeturn0news40  
- **Données de contexte (jour J)** : date et heure locales, fuseau horaire (Europe/Paris dans votre contexte), et idéalement **position géographique** du jour si vous calculez Ascendant/maisons « du moment » (et pas uniquement des transits en longitude).  
- **Option haute précision** : altitude approximative si vous choisissez des positions topocentriques (observateur), particulièrement sensible pour la Lune. La documentation du Swiss Ephemeris souligne que la position topocentrique nécessite la géographie (et l’altitude) et que l’écart peut dépasser un degré pour la Lune. citeturn4view0  

Enfin, la précision de l’heure de naissance est structurante parce que l’Ascendant change rapidement (communément « environ toutes les deux heures »). citeturn1search11turn1search15 Cette contrainte a un impact direct sur la segmentation horaire et sur la personnalisation par maisons.

## Recherche des catégories quotidiennes pertinentes
Votre demande comporte deux niveaux :  
1) **identifier les catégories réellement utilisées dans les horoscopes quotidiens** (pratique éditoriale) ;  
2) **proposer une taxonomie “complète”** pour couvrir l’ensemble des domaines de vie sur une journée (pratique de modélisation).

### Catégories observées dans les horoscopes quotidiens grand public
La plupart des horoscopes « du jour » se structurent autour d’un noyau stable de rubriques. En presse/generalistes, on retrouve souvent **amour, travail, santé** (et fréquemment **argent**) : c’est explicitement le cas dans des pages d’horoscope quotidien de titres grand public (ex. « Amour, travail, santé… »). citeturn6view3turn0search5  
Des sites d’horoscope français proposent aussi des variantes du noyau, en ajoutant **chance** et **bien-être** à côté d’amour/travail/santé. citeturn3search10  

Quand l’horoscope est plus « découpé », on voit émerger des rubriques supplémentaires :  
- **Humeur / climat astral / météo astrale** (ton émotionnel et ambiance générale) ;  
- **Vitalité** (distinct de santé) ;  
- **Amis** et **famille** (relationnel hors couple) ;  
- parfois des rubriques de type « conseil du jour ». citeturn6view1turn6view0  

Enfin, certains acteurs anglophones structurent explicitement des horoscopes « par domaines » en incluant **sex** (sexualité) à côté de love/career/health/money. citeturn3search0turn3search25  

**Conclusion de recherche (niveau produit)** : la « liste empirique » la plus fréquente pour une journée est :  
- Amour / relations ; Travail / carrière ; Argent / finances ; Santé / bien-être,  
avec des extensions récurrentes : Humeur, Vitalité/Énergie, Famille, Amis, Chance, Sexualité. citeturn6view1turn3search10turn3search0  

### Taxonomie « complète » basée sur les maisons astrologiques
Pour une couverture exhaustive et cohérente, la méthode la plus robuste consiste à prendre **les 12 maisons** comme *taxonomie interne* : elles sont classiquement présentées comme représentant des domaines de vie distincts, et dépendent du lieu/heure (donc du temps). citeturn0news40turn0search10  
Cette approche est particulièrement adaptée à votre besoin, car vous voulez : (a) des catégories, (b) une lecture « sur la journée », donc sensible à l’horloge locale.

Dans cette logique, on peut aligner les catégories “UI” (santé, argent, sexe…) sur les maisons ; par exemple :  
- **Maison II** : argent, ressources, valeurs (plusieurs synthèses pédagogiques l’énoncent explicitement). citeturn0search6turn0news46  
- **Maison VI** : santé, routines, hygiène de vie, organisation du quotidien. citeturn0search10turn0search29  
- **Maison VIII** : intimité/sexualité, transformation, ressources partagées (argent « à deux », investissements). citeturn0search10  
- **Maison X** : carrière, réputation, trajectoire professionnelle. citeturn0news47turn0news40  
- **Maison XI** : amis, réseaux, projets collectifs. citeturn0news47turn0news40  
- **Maison IV** : foyer, racines, famille (thème du “home”). citeturn0news40turn0search10  
- **Maison V** : créativité, romance, plaisir (souvent mobilisée pour « amour » au sens flirt/joie). citeturn0search10turn0news47  

**Conclusion de recherche (niveau modèle)** : partir des 12 maisons permet de dériver une liste « complète » de thématiques journalières, sans oublier des domaines moins couverts par l’éditorial (apprentissages, spiritualité, communauté, etc.). citeturn0news47turn0news40  

### Recommandation de catalogue de catégories à “checker” pour la journée
Pour concilier **réalisme produit** (catégories familières) et **exhaustivité** (modèle interne), une bonne pratique est un modèle à deux étages :

**Étage A — catégories “UI” (recommandées pour l’utilisateur, 8 à 12 max)**  
- Santé & hygiène de vie (Maison VI). citeturn0search29  
- Énergie & vitalité (Maison I/VI, + indicateurs rapides type Lune/angles dans la pratique éditoriale « vitalité »). citeturn6view1  
- Humeur & émotions (rubrique « humeur » fréquente). citeturn6view0turn6view1  
- Travail & productivité (Maison VI) + Carrière & image publique (Maison X). citeturn0news47turn0search29  
- Argent & finances personnelles (Maison II). citeturn0search6turn0news46  
- Amour & relation de couple (Maison V/VII). citeturn0search10turn0news47  
- Sexualité & intimité (Maison VIII, et parfois Maison V selon votre cadrage). citeturn0search10turn3search0  
- Famille & foyer (Maison IV). citeturn0search10turn0news40  
- Amis & réseau (Maison XI). citeturn0news47  
- Chance / opportunités (catégorie éditoriale fréquente). citeturn3search10turn6view1  

**Étage B — catégories “moteur” (les 12 maisons, exhaustif, pour calcul + explication)**
Vous pouvez conserver en interne les 12 maisons comme clé de routage des signaux astrologiques vers les domaines de vie. citeturn0news40turn0search10  

## Méthodes astrologiques adaptées à une prédiction du jour
Votre formulation (« données du thème natal + date et heure du jour ») correspond le plus naturellement à une approche **par transits**, éventuellement enrichie d’angles/maisons « du moment » pour produire une granularité horaire.

### Transits, aspects et orbes : briques minimales
Dans la pratique astrologique, un **transit** est généralement décrit comme la relation entre la position actuelle d’une planète et une position (planète ou point sensible) du thème natal ; c’est une technique de timing populaire. citeturn2search2turn1search2 entity["podcast","The Astrology Podcast","astrology podcast"] décrit les transits comme une technique centrale de datation/phasage, reliant le ciel actuel au thème natal. citeturn2search2  

Les transits s’expriment le plus souvent via des **aspects**, c’est-à-dire des angles (conjonction, sextile, carré, trigone, opposition…) entre deux points. citeturn7search11turn7search6  
Pour transformer un aspect en événement *dans la journée*, on introduit les **orbes** : une marge de distance à l’exactitude qui détermine quand l’aspect est considéré comme « actif ». citeturn2search19turn2search15  
De nombreux guides d’interprétation indiquent aussi que plus l’aspect est proche de l’exactitude (« orbe serré »), plus il est considéré comme fort. citeturn7search6turn7search5  

Enfin, certains cadres distinguent un aspect **applying / forming** (qui se rapproche de l’exact) et **separating / fading** (qui s’en éloigne), distinction utilisée pour qualifier l’intensité “immédiate” vs “intégrée”. citeturn7search11  

### Calcul astronomique : éphémérides, maisons, Ascendant, MC
Pour obtenir une prédiction « au jour et à l’heure », il faut un calcul fiable des positions planétaires et des points/maisons. La documentation du **Swiss Ephemeris** (diffusé via entity["company","Astrodienst","astrology services, zurich ch"]) détaille des fonctions de calcul des **cuspides de maisons** et des angles (Ascendant, Milieu du Ciel/MC, etc.), par exemple via `swe_houses()`. citeturn5view0turn5view2  
Cette même documentation rappelle aussi qu’il existe plusieurs **systèmes de maisons** (Whole Sign, Equal Houses, Placidus, etc.) et que la bibliothèque en implémente un large éventail. citeturn5view2  

Deux implications techniques importantes pour votre produit :  
- si vous voulez un découpage horaire cohérent avec « ce qui est angulaire » (Ascendant/MC), vous devez recalculer les maisons/angles à chaque tranche horaire (ou à chaque point de bascule) ;  
- il faut choisir et figer un système de maisons et un zodiaque (tropical/sidéral) au niveau produit, sinon les résultats ne seront pas comparables d’un jour sur l’autre. citeturn5view2turn4view0  

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["roue astrologique 12 maisons thème natal","diagramme aspects astrologiques conjonction carré trigone opposition","heures planétaires heptagramme ordre chaldéen"],"num_per_query":1}

## Découpage de la journée et détection des points de bascule
La difficulté clé est la suivante : beaucoup de transits (surtout des planètes lentes) changent très peu « d’heure en heure », alors que vous souhaitez une **lecture dynamique** sur une journée. Une stratégie solide consiste à superposer **3 couches de temps**, chacune justifiée par une pratique existante.

### Couche horaire produit : tranches fixes (H+0 à H+23)
C’est la couche la plus simple pour l’expérience utilisateur (24 segments). Techniquement, vous calculez pour chaque heure :  
- positions transitantes (au minimum Lune + planètes rapides, ou toutes) ;  
- angles/maisons « du moment » si vous voulez contextualiser (Ascendant/MC). citeturn5view0turn0news40  

### Couche astrologique traditionnelle : heures planétaires (variable selon lieu/saison)
Les **heures planétaires** constituent un découpage traditionnel explicitement pensé pour « timing intrajournalier ». Le principe récurrent est :  
- le jour (du lever au coucher du Soleil) est divisé en 12 « heures » ;  
- la nuit (du coucher au lever du lendemain) est divisée en 12 « heures » ;  
- ces heures sont *inégales* et dépendent du lieu et de la saison. citeturn1search1turn1search0turn1search29  

Cette couche est utile car elle fournit une **narration horaire** (« heure de Mars », « heure de Vénus »…) et des changements fréquents, même quand les transits bougent peu.

### Couche “angles rapides” : changement d’Ascendant (≈ toutes les 2h)
L’Ascendant étant lié à l’horizon local, il change vite (souvent résumé comme « environ toutes les deux heures »), ce qui crée des **paliers** naturels dans une journée, et explique pourquoi l’heure de naissance est cruciale. citeturn1search11turn1search15turn0news40  
Dans un découpage « points de bascule », un changement de signe à l’Ascendant (ou un passage d’angle exact sur une planète natale) peut être traité comme **pivot narratif**.

### Définition opérationnelle des “points de bascule”
Pour que ces points soient calculables, il faut une définition falsifiable au niveau logiciel. Une définition cohérente avec la littérature astrologique sur aspects/orbes est :

Un **point de bascule** survient quand, pour une catégorie donnée, un signal majeur :  
- **entre dans l’orbe** (activation),  
- **atteint l’exactitude** (pic),  
- **sort de l’orbe** (désactivation). citeturn2search19turn7search6turn7search5  

En pratique, vous générez une liste d’événements ordonnés dans la journée, par exemple :  
- exactitude d’un aspect transit ↔ planète/angle natal (ou transit ↔ transit si vous l’utilisez) ;  
- changement d’heure planétaire (pivot narratif récurrent) ;  
- changement de signe de l’Ascendant (pivot “cadre de la scène”). citeturn1search1turn1search11turn7search6  

## Échelle de notation enregistrable par catégorie (1 à 20)
Votre demande mentionne une note « du jour » par catégorie (1–20). Pour qu’elle soit exploitable et stable jour après jour, il faut :  
1) une **intensité** (combien c’est actif) ;  
2) une **polarité** ou “valence” (plutôt fluide/aidant vs plutôt exigeant/tendu) ;  
3) une règle d’agrégation vers un entier.

### Intensité : fonction de l’orbe (proche de l’exact = plus fort)
Les sources pédagogiques sur les aspects/orbes expriment généralement que l’orbe mesure la proximité à l’exactitude, et que la proximité augmente la “force” attribuée à l’aspect. citeturn7search6turn2search19turn7search5  
Proposition d’implémentation (simple, explicable) :  
- définir, par type d’aspect et par corps, un **orbe max** (p.ex. plus serré pour les transits rapides si vous voulez des bascules nettes) ;  
- calculer une intensité continue `I` entre 0 et 1, par exemple : `I = 1 - (orb_actuel / orb_max)` (bornée à [0,1]).

### Polarité : “soft vs hard aspects” comme heuristique, plus dignités/maisons en option
De nombreux guides distinguent des aspects « harmonieux/soft » (trigone, sextile) et « difficiles/hard » (carré, opposition, parfois conjonction selon les planètes), ce qui peut servir de première heuristique pour la valence. citeturn7search2turn7search6turn7search8  
Proposition d’implémentation (progressive) :  
- **niveau 1 (MVP)** : valence basée sur type d’aspect (soft = +, hard = −, conjonction = dépend des planètes) ;  
- **niveau 2** : moduler selon les planètes impliquées (bénéfiques/maléfiques dans certaines traditions, ou grammaire interne “facilitant vs structurante”) ;  
- **niveau 3** : moduler selon la maison natale impactée (un même signal affecte différemment “argent” ou “relations”).  

L’intérêt produit est que vous pouvez conserver une note **non-fataliste** : un carré peut être scoré comme “exigeant mais productif”, plutôt que “mauvais”.

### Conversion en note 1–20
Une conversion claire (et facile à stocker) consiste à placer **10 comme neutre**, puis à décaler selon le total des signaux :  
- ScoreCatégorie = `clamp(1, 20, round(10 + 10 * S))`  
où `S` est une somme pondérée de signaux `valence * intensité` (ex. S ∈ [−1, +1] après normalisation).

Pour garder une expérience stable, il est utile d’associer des **libellés** à des bandes (ex. 1–4 “fragile”, 5–8 “tendu”, 9–12 “neutre”, 13–16 “porteur”, 17–20 “très favorable”), tout en rappelant le caractère interprétatif (divinatoire) du score. citeturn2search0turn2search21  

## Format de restitution : synthèse horaire, faits émergents et stockage
La restitution demandée contient deux objets : (a) une synthèse temporelle, (b) des notes par catégories.

### Synthèse horaire : une structure lisible et “actionnable”
Une structure qui correspond bien à votre besoin est :
- **Intro du jour** : 3–5 phrases (ton général + 2–3 domaines saillants), calée sur les signaux les plus intenses et sur une « météo astrale » de type climat/humeur souvent observée dans l’éditorial. citeturn6view1turn6view0  
- **Timeline** par heure (ou par blocs 2h si vous suivez les changements d’Ascendant), chaque bloc contenant :  
  - tendance (verbe d’action + prudence)  
  - domaine(s) touché(s) (catégories)  
  - étiquette “pivot” si un point de bascule tombe dans le bloc  

Dans une implémentation “points de bascule”, les blocs peuvent être *event-driven* : si aucun événement important n’existe sur 2–3 heures, vous pouvez regrouper. À l’inverse, si plusieurs exactitudes/aspects clés arrivent la même matinée, vous pouvez raffiner l’heure.

### Schéma d’enregistrement conseillé (exemple)
Sans figer votre stack, l’objet logique à stocker pour 1 journée comprend typiquement :
```json
{
  "date_local": "2026-03-07",
  "timezone": "Europe/Paris",
  "categories": {
    "sante": { "score_1_20": 12, "summary": "..." },
    "energie": { "score_1_20": 9, "summary": "..." },
    "travail": { "score_1_20": 14, "summary": "..." },
    "argent": { "score_1_20": 11, "summary": "..." },
    "sexe_intimite": { "score_1_20": 13, "summary": "..." }
  },
  "timeline": [
    {
      "start": "07:00",
      "end": "08:00",
      "headline": "...",
      "categories_impacted": ["energie", "travail"],
      "turning_point": false
    },
    {
      "start": "10:15",
      "end": "11:30",
      "headline": "...",
      "categories_impacted": ["argent", "travail"],
      "turning_point": true,
      "why": "aspect exact / changement d'heure planétaire / Ascendant"
    }
  ]
}
```

### Notes de prudence (santé/argent) et cohérence rédactionnelle
Étant donné que l’astrologie est présentée comme divination et non comme science, et qu’elle est souvent perçue comme guidance symbolique, les rubriques **santé** et **argent** gagnent à être rédigées sous forme de tendances, d’attention et de priorités (et non sous forme d’injonctions ou de certitudes). citeturn2search0turn2search21turn2news40  

Sur la cohérence, les sites d’horoscope « par rubriques » montrent qu’un cadrage stable (mêmes catégories, mêmes définitions, même style) aide à la lisibilité quotidienne. citeturn6view1turn3search10turn3search0