<!-- Commentaire global: ce document formalise une review adversariale et un plan corrige pour refondre l'interpretation natale basic. -->

# Review adversariale et plan corrige pour la refonte de l'interpretation natale basic

Date: 2026-05-31

Perimetre: backend d'interpretation natale, mode basic, contrat narratif, scoring astrologique, generation IA, restitution utilisateur.

Objectif: transformer le plan de refacto initial en plan technique robuste, testable et applicable a tous les utilisateurs, quelles que soient leurs donnees de naissance.

Hors perimetre:

- implementation du code;
- migration progressive de donnees existantes;
- refonte UI complete;
- interpretation predictive;
- consultations premium longues.

## Synthese executive

Le plan initial allait dans la bonne direction: separer le calcul astrologique brut, l'analyse structuree, le plan narratif et le rendu utilisateur. Sa faiblesse principale etait de rester trop conceptuel. Il disait quoi faire, mais pas assez comment garantir la qualite, la coherence multi-utilisateurs, la non-regression astrologique, la robustesse en cas de donnees incompletes et la maitrise du LLM.

La correction centrale est la suivante: l'intelligence astrologique ne doit pas etre confiee directement au prompt. Le backend doit construire un dossier de lecture versionne, priorise, contraint et valide. Le LLM, s'il est utilise, ne doit etre qu'un redacteur controle. Le moteur doit savoir expliquer pourquoi une section existe, quelles donnees elle utilise, quels signaux ont ete exclus, et quelles limites s'appliquent.

Le pipeline cible devient:

`NatalResult -> EligibilityContext -> FactGraph -> SalienceModel -> ThemeModel -> SynthesisResolver -> ReadingPlan -> NarrativeDraft -> NarrativeValidator -> BasicNatalInterpretation`

## Findings adversariaux sur le plan initial

### P1 - Le plan initial etait trop dependant du LLM

Le plan disait que le LLM devait transformer un plan valide en prose, mais il ne definissait pas assez strictement le plan, les contraintes de generation, ni le validateur post-generation. Risque: obtenir encore une interpretation agreable mais generique, avec des themes non prouves ou une hierarchie faible.

Correction:

- produire un `ReadingPlan` exhaustif avant generation;
- imposer des sections, des faits obligatoires et des faits interdits;
- fournir au LLM uniquement des faits deja selectionnes;
- valider la sortie contre le plan;
- rejeter ou reparer une sortie qui introduit une affirmation non supportee.

### P1 - Aucun traitement formel des donnees de naissance incompletes

Le plan initial supposait que l'heure de naissance etait disponible. Or le mode basic doit fonctionner pour tous les utilisateurs. Sans heure fiable, les maisons, l'Ascendant, le MC, les maitres de maisons et l'angularite deviennent indisponibles ou incertains.

Correction:

- creer un `EligibilityContext`;
- classifier chaque lecture en `full_birth_time`, `approximate_birth_time`, `date_only`;
- desactiver automatiquement les sections fondees sur maisons/angles si l'heure manque;
- remplacer les lectures de maison par une lecture signes/aspects/luminaires;
- exposer une mention claire: "l'heure de naissance n'etant pas renseignee, les maisons et l'Ascendant ne sont pas interpretes".

### P1 - Le scoring risquait de suradapter la refonte au theme test

Le plan initial a ete derive d'un cas tres maison 10. Il pouvait conduire les devs a privilegier vocation/visibilite partout, meme lorsque le theme d'un autre utilisateur est centre sur maison 4, maison 12, Lune, Saturne ou relations.

Correction:

- definir des archetypes de themes representatifs;
- calibrer le scoring sur plusieurs cas;
- ne jamais coder une priorite de section fixe hors "piliers de base";
- rendre l'ordre des sections partiellement dynamique selon les themes actives.

### P1 - Absence de resolver pour les contradictions astrologiques

Le plan initial extrait et score des faits, mais ne decrit pas comment combiner des signaux contradictoires. Exemple: Vénus en domicile mais combuste; Lune maitresse d'Ascendant mais cadente et en detriment; Jupiter fort mais carre au Soleil/Venus.

Correction:

- ajouter un `SynthesisResolver`;
- modeliser chaque theme avec `resources`, `constraints`, `tensions`, `integration`;
- interdire les formulations unilateralement positives ou negatives lorsqu'un theme a des signaux mixtes;
- obliger chaque section importante a restituer au moins une nuance si le score de tension depasse un seuil.

### P2 - La notion de "preuve" etait trop brute pour l'utilisateur basic

Le plan proposait une section `evidence`, mais sans distinguer preuve technique, preuve pedagogique et preuve interne. Risque: afficher des donnees incomprehensibles du type `jupiter major mercury`, `ranking_weight` ou `condition_axis`.

Correction:

- creer trois niveaux de preuve:
  - `internal_evidence`: donnees completes pour debug;
  - `editorial_evidence`: faits selectionnes pour le LLM;
  - `public_evidence`: faits vulgarises pour l'utilisateur;
- exposer uniquement `public_evidence` en basic;
- garder les scores et axes internes hors du contrat public.

### P2 - Le plan ne precisait pas assez la taxonomie narrative

Des codes comme `public_vocation` ou `emotional_pattern` etaient proposes, mais sans contrat de declenchement, de priorite et de contenu. Risque: multiplication de themes voisins et incoherence entre interpretations.

Correction:

- creer une taxonomie versionnee `NatalNarrativeThemeTaxonomy`;
- chaque theme doit avoir:
  - des triggers astrologiques;
  - des exclusions;
  - des sections compatibles;
  - un vocabulaire conseille;
  - des formulations interdites;
  - un niveau de disponibilite selon l'heure de naissance.

### P2 - Les tests etaient insuffisants pour une qualite astrologique durable

Les tests proposes couvraient quelques snapshots, mais pas assez la diversite astrologique ni les erreurs narratives. Risque: regresser sur certains profils sans le voir.

Correction:

- ajouter un corpus de golden charts anonymises;
- tester des archetypes contrastes;
- tester les cas sans heure;
- tester les contradictions;
- tester la non-exposition de jargon interne;
- tester la coherence entre plan et texte final.

### P2 - Pas de versioning clair du contrat d'interpretation

Le plan initial proposait un contrat API, mais pas de versioning fin du moteur narratif. Risque: impossible de comparer deux generations ou de savoir quelle logique a produit une interpretation.

Correction:

- versionner:
  - la taxonomie de faits;
  - le modele de salience;
  - la taxonomie de themes;
  - le builder de plan;
  - le prompt;
  - le validateur;
  - le schema public.

### P2 - Pas de strategie de cache/invalidation

Meme hors production, l'application persiste deja des interpretations. Sans migration progressive, il faut tout de meme definir comment invalider les anciennes interpretations basic.

Correction:

- incrementer `schema_version` et `engine_version`;
- rendre les anciennes interpretations incompatibles avec le nouveau mode basic;
- regenerer a la demande si `engine_version` differe;
- ne pas melanger l'ancien format `short` et le nouveau `basic`.

### P3 - Le plan ne couvrait pas assez la confidentialite

Une interpretation n'a pas besoin d'envoyer au LLM toutes les donnees personnelles brutes. Les coordonnees exactes, l'email ou des identifiants internes ne doivent jamais etre dans le prompt.

Correction:

- construire un payload LLM sans email, user id, place id interne ou coordonnees exactes si non necessaires;
- garder uniquement les faits astrologiques derives;
- conserver les donnees de naissance dans le backend, pas dans la couche narrative.

### P3 - Le plan ignorait la localisation linguistique

L'application possede une logique de langue. La refonte basic doit produire une structure stable, mais le rendu doit etre localisable.

Correction:

- separer les codes astrologiques internes des libelles traduits;
- ne pas hardcoder les phrases pedagogiques en francais dans la couche de scoring;
- prevoir `locale` dans le contrat de rendu;
- tester au minimum la coherence du francais.

## Plan corrige de refacto technique

## 1. Contrat de niveau: `basic` n'est pas `short`

Le mode basic doit etre concis, mais pas superficiel. Il doit fournir une lecture natale fiable, structuree et pedagogique.

Definition cible:

- longueur indicative: 900 a 1300 mots en francais;
- 6 a 8 sections maximum;
- chaque section doit etre fondee sur des faits astrologiques selectionnes;
- aucun score interne visible;
- aucun jargon non explique;
- ton direct en "vous";
- aucune prediction ferme;
- aucune injonction medicale, financiere ou psychologique.

Le mode basic doit remplacer les interpretations actuellement trop generiques de type `natal_interpretation_short`.

## 2. Pipeline cible

### 2.1 `EligibilityContext`

Role: determiner quelles familles de donnees sont interpretables.

Entrees:

- date de naissance;
- heure locale;
- source ou presence de l'heure;
- lieu;
- timezone;
- statut de resolution du theme.

Sortie:

```json
{
  "birth_time_status": "full_birth_time",
  "can_use_houses": true,
  "can_use_angles": true,
  "can_use_house_rulers": true,
  "can_use_lunar_nodes_by_house": true,
  "limitations": []
}
```

Variantes obligatoires:

- `full_birth_time`: interpretation complete;
- `approximate_birth_time`: maisons et angles utilisables avec prudence;
- `date_only`: pas de maisons, pas d'Ascendant, pas de MC.

### 2.2 `FactGraph`

Role: convertir le theme calcule en faits astrologiques atomiques, types et tracables.

Familles minimales:

- `luminary_fact`: Soleil, Lune;
- `angle_fact`: Ascendant, MC, IC, Descendant;
- `planet_position_fact`: planete en signe/maison;
- `house_emphasis_fact`: maison dominante, stellium de maison;
- `sign_emphasis_fact`: signe dominant;
- `element_balance_fact`: element dominant ou faible;
- `modality_balance_fact`: modalite dominante;
- `aspect_fact`: aspects majeurs;
- `rulership_fact`: maitre d'Ascendant, maitre de maison 10, maitre de maison 7;
- `condition_fact`: dignite, combustion, retrogradation, sect, condition notable;
- `node_fact`: noeud nord/sud en signe et maison si eligible.

Chaque fait doit porter:

```json
{
  "id": "fact_sun_taurus_house_10",
  "family": "planet_position",
  "object_codes": ["sun"],
  "sign_code": "taurus",
  "house_number": 10,
  "confidence": "high",
  "requires_birth_time": true,
  "source_paths": [
    "planet_positions.sun.sign_code",
    "planet_positions.sun.house_number"
  ]
}
```

### 2.3 `SalienceModel`

Role: attribuer une importance interpretable aux faits, sans produire de texte final.

Facteurs de priorite:

- luminaire;
- maitre d'Ascendant;
- angularite;
- proximite ASC/MC;
- maison dominante;
- planete dominante;
- dignite essentielle forte;
- condition debilitante forte;
- aspect exact;
- aspect impliquant Soleil, Lune, Ascendant, MC, maitre d'Ascendant ou dominante;
- repetition d'un meme theme par plusieurs faits;
- disponibilite selon `EligibilityContext`.

Sortie:

```json
{
  "fact_id": "fact_sun_taurus_house_10",
  "salience_score": 0.92,
  "salience_level": "major",
  "reason_codes": [
    "luminary",
    "angular_house",
    "dominant_house"
  ]
}
```

Regle critique: un fait spectaculaire mais secondaire ne doit pas passer devant un pilier natal. Exemple: Lilith maison 5 ne doit pas etre prioritaire sur Soleil maison 10, Lune maison 6 ou Ascendant Cancer.

### 2.4 `ThemeModel`

Role: regrouper les faits en themes narratifs standardises.

Themes basic recommandes:

| Code | Role |
| --- | --- |
| `core_identity` | Soleil, Ascendant, dominante generale |
| `emotional_pattern` | Lune, maitre d'Ascendant, aspects lunaires |
| `public_vocation` | MC, maison 10, maitre de 10, planetes elevees |
| `relationship_pattern` | maison 7, Venus, Jupiter, aspects relationnels |
| `mental_style` | Mercure, maison 3, aspects de Mercure |
| `resources_and_values` | maison 2, Venus, signes de Terre |
| `action_and_drive` | Mars, maison 1/8/10, aspects de Mars |
| `growth_direction` | noeuds lunaires, maitre d'Ascendant, tensions recurrentes |
| `tension_to_integrate` | carres, oppositions, contradictions conditionnelles |
| `talents_and_supports` | trigones, sextiles, dignites fortes |

Chaque theme doit contenir:

```json
{
  "theme_code": "public_vocation",
  "activation_score": 0.94,
  "priority_level": "primary",
  "resources": ["fact_venus_taurus_house_10"],
  "constraints": ["fact_venus_combust"],
  "tensions": ["fact_jupiter_square_venus"],
  "must_mention": ["fact_sun_house_10", "fact_venus_house_10"],
  "may_mention": ["fact_mercury_near_mc"],
  "do_not_mention": ["raw_condition_axis_visibility"]
}
```

### 2.5 `SynthesisResolver`

Role: transformer des themes parfois contradictoires en lignes de lecture nuancees.

Il doit produire une synthese par theme:

- `core_statement`: phrase centrale;
- `resource_statement`: force ou facilite;
- `constraint_statement`: tension ou limite;
- `integration_statement`: piste d'integration;
- `confidence`: niveau de confiance.

Exemple generique:

```json
{
  "theme_code": "public_vocation",
  "core_statement": "La vocation et la place sociale structurent fortement le theme.",
  "resource_statement": "La presence de Venus en Taureau favorise la qualite, la valeur et l'attractivite.",
  "constraint_statement": "La combustion et les carres de Jupiter demandent de ne pas confondre reconnaissance et valeur personnelle.",
  "integration_statement": "Le theme invite a construire une visibilite professionnelle alignee sur des valeurs stables."
}
```

Regles adversariales:

- si un theme contient une dignite forte et une contrainte forte, interdire une phrase purement positive;
- si un theme est fonde sur un seul fait faible, ne pas creer de section dediee;
- si deux themes racontent la meme chose, les fusionner;
- si un theme depend de maisons indisponibles, le retrograder ou le supprimer.

### 2.6 `ReadingPlan`

Role: definir exactement la restitution avant generation.

Contrat cible:

```json
{
  "level": "basic",
  "locale": "fr-FR",
  "engine_version": "basic-natal-reading-v1",
  "eligibility": {},
  "title_strategy": "dominant_theme",
  "sections": [
    {
      "section_code": "synthesis",
      "heading_intent": "Synthese du theme",
      "target_length_words": 160,
      "theme_codes": ["core_identity", "public_vocation"],
      "required_fact_ids": [],
      "forbidden_fact_families": ["internal_score"]
    }
  ],
  "public_evidence": [],
  "style_constraints": {}
}
```

Ordre de sections recommande avec heure complete:

1. Synthese essentielle.
2. Identite et temperament.
3. Vie interieure.
4. Vocation et place sociale, si active.
5. Relations, si active.
6. Talents et appuis.
7. Tensions a integrer.
8. Direction de croissance.

Ordre de sections recommande sans heure:

1. Synthese essentielle.
2. Soleil et Lune.
3. Equilibre elements/modalites.
4. Relations et valeurs.
5. Mental et action.
6. Aspects majeurs.
7. Direction de croissance par signes.

## 3. Strategie de generation narrative

## 3.1 Option recommandee: LLM contraint par plan

Le LLM recoit:

- le `ReadingPlan`;
- les syntheses resolues;
- les preuves editoriales;
- les contraintes de style;
- les disclaimers.

Le LLM ne recoit pas:

- email;
- identifiant utilisateur;
- identifiant de lieu;
- coordonnees brutes exactes;
- scores internes non necessaires;
- donnees runtime completes.

## 3.2 Validation post-generation

Ajouter un `NarrativeValidator`.

Controles obligatoires:

- toutes les sections demandees sont presentes;
- aucune section interdite n'apparait;
- les faits astrologiques mentionnes existent dans le plan;
- pas de score interne visible;
- pas de termes techniques non expliques si affiches;
- pas de melange "vous / il / elle";
- longueur maximale respectee;
- disclaimers presents;
- absence de conseils medicaux, juridiques, financiers ou psychologiques prescriptifs.

En cas d'echec:

1. tentative de reparation par prompt contraint;
2. si deuxieme echec, fallback deterministe par templates courts;
3. journalisation de l'erreur avec `request_id`, `engine_version`, `validation_errors`.

## 4. Contrat public cible

```json
{
  "chart_id": "uuid",
  "level": "basic",
  "engine_version": "basic-natal-reading-v1",
  "schema_version": "basic_natal_interpretation_v2",
  "generated_at": "datetime",
  "interpretation": {
    "title": "string",
    "summary": "string",
    "sections": [
      {
        "key": "synthesis",
        "heading": "string",
        "content": "string",
        "supporting_evidence_ids": ["evidence_public_vocation"]
      }
    ],
    "key_points": ["string"],
    "growth_advice": ["string"],
    "used_facts": [
      {
        "id": "evidence_public_vocation",
        "label": "Maison 10 dominante",
        "explanation": "Cette concentration met l'accent sur la vocation, la reconnaissance et la construction d'une place visible.",
        "facts": [
          "Soleil en maison 10",
          "Venus en maison 10",
          "Mercure en maison 10"
        ]
      }
    ],
    "limitations": [],
    "disclaimers": []
  }
}
```

## 5. Regles de contenu pour le mode basic

### 5.1 Obligatoire

- Dire ce qui domine vraiment le theme.
- Expliquer les trois piliers lorsque disponibles: Soleil, Lune, Ascendant.
- Mentionner les themes actifs par repetition de preuves.
- Restituer les tensions principales, mais sans dramatiser.
- Donner une direction de croissance.
- Garder un langage accessible.

### 5.2 Interdit

- Afficher `ranking_score`, `condition_axis`, `score_profile`, `weighted_score`, `prompt_hint`.
- Presenter une hypothese astrologique secondaire comme centrale.
- Utiliser des phrases Barnum sans preuve.
- Faire des predictions.
- Employer un ton fataliste.
- Melanger les personnes grammaticales.
- Utiliser "spirituel", "creatif", "harmonieux", "profond" sans preuve astrologique precise.

### 5.3 A transformer avant affichage

| Donnee interne | Formulation basic possible |
| --- | --- |
| `venus domicile` | Venus est dans un signe ou elle s'exprime avec force et naturel. |
| `venus combust` | Cette force peut etre absorbee par l'image, la reconnaissance ou la volonte de bien faire. |
| `moon detriment` | La vie emotionnelle peut chercher le controle, la retenue ou la maitrise. |
| `mars out_of_sect` | L'action peut devenir plus reactive si elle n'est pas canalisee. |
| `maltreatment` | Une tension structurelle demande de la discipline et de la regulation. |
| `bonification` | Un appui vient adoucir ou soutenir cette fonction. |

## 6. Exemple d'application au theme test

Ce theme ne doit pas servir de modele unique, mais il permet de verifier que le nouveau pipeline priorise correctement.

Themes attendus:

- `public_vocation`: priorite tres forte.
- `core_identity`: forte, via Soleil Taureau maison 10 et Ascendant Cancer.
- `emotional_pattern`: forte, via Lune Capricorne maison 6 et carre Uranus.
- `talents_and_supports`: forte, via Venus dominante et grand trigone d'Air.
- `relationship_pattern`: moyen-fort, via Jupiter maison 7 et Descendant Capricorne.
- `tension_to_integrate`: forte, via Jupiter carre Soleil/Venus et Lune carre Uranus.
- `growth_direction`: moyen, via Noeud Nord Capricorne maison 6.

Sections attendues:

1. Synthese: theme de construction visible, qualite, reconnaissance, responsabilite.
2. Identite: Soleil Taureau maison 10, Ascendant Cancer, Mercure pres MC.
3. Vie interieure: Lune Capricorne maison 6, sensibilite contenue, securite par l'utilite.
4. Vocation: stellium maison 10, Venus dominante, MC Belier.
5. Relations: Jupiter maison 7, Saturne maitre de 7 en maison 11.
6. Talents: grand trigone d'Air Mars-Saturne-Uranus.
7. Tensions: Jupiter carres, Lune-Uranus, Venus combuste.
8. Croissance: Noeud Nord Capricorne maison 6.

Faits a ne pas prioriser en basic:

- Lilith maison 5;
- `voices`, `forms`, `fertility`;
- hayz;
- details numeriques de dignites;
- source technique Swiss Ephemeris.

## 7. Tests attendus

### 7.1 Tests unitaires

- extraction des faits pour Soleil, Lune, Ascendant, MC;
- extraction des aspects majeurs avec orbe;
- detection de maison dominante;
- detection de concentration de maison;
- detection de dignite forte et contrainte forte;
- exclusion automatique des maisons si heure absente;
- mapping interne vers preuve publique.

### 7.2 Tests de scoring

- un luminaire angulaire doit passer devant un point mineur;
- un aspect exact impliquant Lune/Soleil doit passer devant un aspect large entre transpersonnelles;
- une maison dominante doit activer le theme correspondant;
- un theme fonde sur un seul signal faible ne doit pas creer une section.

### 7.3 Golden charts

Creer au minimum un corpus de themes anonymises:

- theme maison 10 dominante;
- theme maison 4 dominante;
- theme maison 7 dominante;
- theme maison 12 dominante;
- theme sans heure de naissance;
- theme avec forte dominante Feu;
- theme avec dominante Eau;
- theme avec Lune tres aspectee;
- theme avec Saturne dominant;
- theme avec Venus dominante mais contrainte.

Chaque golden chart doit stocker:

- facts attendus;
- themes attendus;
- sections attendues;
- faits interdits en basic;
- assertions de qualite narrative.

### 7.4 Tests de validation narrative

- pas de score interne visible;
- pas de "cette personne" si le style attendu est "vous";
- pas de section vocation si aucune preuve suffisante;
- pas d'Ascendant si heure absente;
- disclaimers presents;
- longueur maximale respectee;
- chaque section reference au moins un `supporting_evidence_id`.

## 8. Organisation technique conseillee

Sans imposer les noms finaux, la responsabilite devrait etre separee ainsi:

| Composant | Responsabilite |
| --- | --- |
| `natal_reading_eligibility` | Disponibilite maisons/angles selon donnees de naissance |
| `natal_fact_extractor` | Extraction des faits atomiques |
| `natal_salience_model` | Scoring et priorisation |
| `natal_theme_detector` | Activation des themes narratifs |
| `natal_synthesis_resolver` | Nuance ressources/contraintes/tensions |
| `basic_natal_reading_plan_builder` | Construction du plan |
| `basic_natal_prompt_builder` | Payload minimal pour LLM |
| `natal_narrative_validator` | Validation et rejection/reparation |
| `basic_natal_interpretation_service` | Orchestration applicative |

Regle d'architecture: aucun composant de rendu ne doit reparcourir le `NatalResult` brut pour choisir arbitrairement de nouveaux faits. Toute selection doit passer par le plan.

## 9. Strategie de remplacement hors production

Comme aucune migration progressive n'est requise:

1. Creer le nouveau moteur en parallele dans le code, mais remplacer le use case basic au moment de l'integration.
2. Incrementer le schema public: `basic_natal_interpretation_v2`.
3. Incrementer l'engine: `basic-natal-reading-v1`.
4. Invalider les interpretations basic precedentes si leur version differe.
5. Garder les anciennes donnees uniquement comme historique technique si necessaire.
6. Ne pas maintenir deux logiques basic concurrentes.

## 10. Definition of Done

La refonte est acceptable si:

- le backend produit un `ReadingPlan` inspectable avant generation;
- le LLM ne recoit que les faits selectionnes;
- le mode basic fonctionne avec et sans heure de naissance;
- les golden charts passent;
- les anciennes phrases generiques sont remplacees par des sections fondees sur preuves;
- les preuves publiques sont lisibles;
- les donnees techniques internes ne fuitent pas dans la restitution;
- les disclaimers restent presents;
- la sortie est versionnee;
- le comportement est teste sur plusieurs archetypes astrologiques.

## Conclusion

Le plan corrige transforme la refonte en architecture controlable. La cle n'est pas d'ecrire un meilleur prompt, mais de construire un moteur de lecture natale qui sait prioriser, nuancer, exclure et expliquer. Le mode basic doit rester accessible, mais il doit deja respecter une logique professionnelle: piliers du theme, dominantes, tensions, talents, chemin d'integration et preuves comprehensibles.

La prochaine etape recommandee est de rediger une story CONDAMAD centree uniquement sur la creation du `ReadingPlan` et de ses tests, avant toute generation IA. Cela permettra de verrouiller la logique astrologique avant de travailler le style narratif.
