# CS-421 - Renforcer Le Contrat Redactionnel Basic Natal

<!-- Commentaire global: ce brief cadre la correction backend du contenu Basic natal pour produire une lecture humaine, exacte et non mecanique. -->

## Resume

Transformer la generation Basic V2 en vrai rapport redige, sans perdre l'exactitude astrologique
garantie par `BasicNatalReadingPlan`.

L'exemple utilisateur `daconrilcy@hotmail.com` montre que le contenu accepte reste actuellement
un assemblage de donnees:

- repetitions de la phrase `cette lecture s'appuie uniquement sur ... avec nuance`;
- libelles bruts comme `Luminaire: moon`, `Position planetaire: saturn, gemini`;
- explications de sources generiques (`Ce repere retient ... comme matiere astrologique...`);
- absence de fil conducteur lisible pour un non-initie;
- fallback deterministe publiquement visible qui ressemble a un diagnostic de pipeline.

La story doit imposer un contrat redactionnel Basic: chaque section doit expliquer le sens humain
des faits retenus, relier les themes entre eux, vulgariser les termes astrologiques et rester
strictement bornee aux preuves du plan.

## Analyse Produit

Le probleme n'est pas seulement une insuffisance de donnees. Les stories CS-409 a CS-418 ont
securise le plan, la privacy et la validation, mais le payload transmis au redacteur et le fallback
restent trop proches de la structure interne:

- le LLM recoit surtout des labels de preuves, pas une consigne de rapport avec arc narratif;
- les preuves publiques sont fabriquees depuis les objets runtime avec des noms anglais;
- le fallback deterministe fabrique des phrases valides contractuellement mais inutilisables
commercialement;
- la validation accepte une prose courte qui nomme des donnees au lieu d'en donner le sens.

Le moyen propose: ajouter une couche `BasicNatalEditorialBrief` derivee du reading plan, qui
fournit au provider des consignes section par section:

- role de la section dans le rapport;
- facts autorises deja vulgarises;
- sens humain court autorise pour chaque fait ou groupe de faits;
- manifestation possible en langage courant;
- nuance anti-fataliste;
- limite d'usage et claims interdits;
- vocabulaire public FR pour les objets astrologiques;
- transition attendue avec le fil conducteur;
- contraintes de comprehension non-initie;
- interdiction explicite de lister les sources comme contenu principal.

Cette couche ne recalcule rien: elle reformule uniquement les preuves autorisees par
`BasicNatalReadingPlan`. Elle ne doit pas recreer de referentiel astrologique local: les libelles
de planetes, signes, aspects et axes doivent venir des owners existants de traduction/runtime, ou
d'un helper explicitement classe comme formatteur de presentation derive de ces owners.

Point critique: le brief redactionnel ne doit pas seulement traduire les labels. Il doit fournir au
modele une matiere interpretative controlee, suffisante pour eviter deux echecs symetriques:
l'inventaire mecanique de donnees et l'invention libre.

## Objectif

Obtenir une interpretation Basic exacte mais lisible comme un rapport humain:

```text
Introduction
=> annonce du fil conducteur en langage courant.

Themes
=> chaque theme explique ce que signifie le fait astrologique, comment il peut se vivre,
   quelle nuance evite le fatalisme, et comment il se relie aux autres themes.

Conclusion
=> synthese actionnable mais non prescriptive.

Sources
=> presentes comme annexe courte, pas comme corps de lecture.
```

## Perimetre Inclus

1. Ajouter un modele interne de brief redactionnel Basic derive exclusivement du
   `BasicNatalReadingPlan`.
2. Remplacer les libelles publics bruts par des libelles FR resolus via les owners canoniques
   existants ou via un formatteur de presentation qui ne porte aucune table astrologique metier
   concurrente.
3. Ajouter des explications publiques specifiques par famille de fait, sans score, ID brut,
   chemin technique ou recalcul astrologique.
4. Ajouter une matiere interpretative controlee par fait ou groupe de faits:
   - `public_label`;
   - `reader_meaning`;
   - `possible_manifestation`;
   - `nuance`;
   - `allowed_section_role`;
   - `forbidden_claims`;
   - `source_fact_refs` ou references internes equivalentes, audit-only et non publiques.
5. Enrichir le payload provider Basic avec:
   - `report_arc`;
   - `section_editorial_briefs`;
   - `plain_language_glossary`;
   - `forbidden_template_phrases`;
   - `source_usage_policy`.
6. Clarifier la structure publique Basic pour eviter toute ambiguite entre `summary`,
   `introduction` et `Fil conducteur`.
7. Ne pas utiliser `summary` comme substitut faible a l'introduction si cela duplique le premier
   theme ou le fil conducteur.
8. Modifier le fallback deterministe Basic uniquement dans le workflow CS-417 existant: il doit
   rester plan-backed, audite avec `fallback_used=True`, et ne jamais devenir un second moteur
   narratif silencieux. Si la qualite minimale ne peut pas etre atteinte, la sortie doit suivre le
   rejet audite existant.
9. Renforcer le validateur Basic pour refuser:
   - la phrase template `cette lecture s'appuie uniquement sur`;
   - les libelles techniques/anglais publics (`moon`, `sun`, `saturn`, `north node`, etc.);
   - les formes publiques francaises non accentuees quand une forme accentuee attendue existe
     (`Synthese`, `theme`, `repere`, `planetaire`, `a integrer`, etc.);
   - les sections qui ne font que lister des preuves;
   - les conclusions/disclaimers qui remplacent le contenu.
10. Traiter le theme `Fil conducteur` comme une introduction ou un chapitre de synthese non
    duplicatif: il ne doit pas etre rendu comme theme ordinaire s'il repete l'introduction.
11. Ajouter des tests sur le profil fixture equivalent a `daconrilcy@hotmail.com`.
12. Ajouter un snapshot JSON avant/apres du payload Basic et du contrat public accepte.

## Hors Perimetre

- Modifier les calculs astrologiques.
- Ajouter de nouvelles sources astrologiques non presentes dans le plan.
- Faire deduire au LLM seul le sens astrologique depuis des codes ou des labels.
- Changer les quotas, droits commerciaux ou persistance.
- Refaire le rendu React de `/natal` (traite par CS-422).
- Corriger le template/assembly du prompt final `theme_astral_prompt_v1` (traite par CS-424).
- Invalider ou regenerer les lectures historiques degradees (traite par CS-425).
- Faire un appel provider live dans les tests automatises.
- Elargir le plan Basic a Premium.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- Piece jointe utilisateur: DOM actuel `/natal` du 31/05/2026 18:22.
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`
- `backend/app/domain/astrology/interpretation/natal_fact_graph.py`
- `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py`
- `backend/app/domain/astrology/runtime` et resolvers de traduction astrologique existants.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `backend/tests/unit/test_basic_natal_reading_contracts.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-152` - le contrat public ne doit pas exposer `chart_json`, audit ou signaux internes.
  - `RG-154` - les marqueurs techniques restent absents du DOM public et donc des textes publics.
  - `RG-155` - pas de padding semantique ni de chapitres dupliques.
  - `RG-156` - la matiere Basic reste diverse et plan-driven.
  - `RG-109` - les libelles de signes astrologiques localises ne doivent pas etre recrees en mapping local.
  - `RG-112` - aucun referentiel astrologique metier local ne doit etre reintroduit.
  - `RG-164` - la selection Basic reste portee par `BasicNatalReadingPlan`.
  - `RG-165` - le payload Basic exclut PII, scores, chemins et IDs bruts.
  - `RG-166` - les drafts acceptes correspondent au plan.
  - `RG-167` - Basic complete utilise `basic-natal-reading-v1`.
  - `RG-168` - `BasicNatalInterpretationV2` reste le contrat public canonique.
- Required regression evidence:
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/unit/test_basic_natal_narrative_validator.py tests/unit/test_basic_natal_reading_contracts.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q app/tests/unit/test_astrology_translation_resolver.py --tb=short` si les libelles localises sont touches.
  - Scan: `rg -n "cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node" backend/app backend/tests`
  - Scan: `rg -n "SIGN_NAMES_FR|SIGN_LABELS|PLANET_LABELS|NODE_LABELS|ASPECT_LABELS|\\bSIGNS\\s*=\\s*\\[" backend/app/domain/astrology backend/app/domain/llm/runtime backend/app/services/llm_generation/natal`
  - Les hits de scan sont autorises uniquement dans tests negatifs, denylist ou evidence historique.
- Registry enrichment expected:
  - Ajouter un nouvel invariant `RG-169` si la story cree une garde durable de qualite
    redactionnelle Basic.
- Allowed differences:
  - Le payload provider Basic gagne des champs redactionnels publics et non sensibles.
  - Les textes publics changent pour devenir plus explicatifs, sans ajout de faits astrologiques.

## Criteres D'acceptation

1. Le payload provider Basic contient des briefs redactionnels par section, sans PII, scores,
   chemins, fact IDs bruts, `chart_json` ou `natal_data`, et ses tests de squelette sont mis a jour.
2. Les preuves publiques utilisent des libelles francais comprehensibles pour un non-initie.
3. Chaque `section_editorial_brief` contient au minimum des labels publics localises, un sens
   humain court, une manifestation possible, une nuance anti-fataliste, une limite d'usage et les
   faits du `BasicNatalReadingPlan` dont ce sens est derive.
4. Le LLM n'a pas a deduire seul le sens astrologique depuis des codes ou des labels.
5. Le brouillon Basic accepte contient une introduction, des themes et une conclusion qui
   expliquent le sens des faits au lieu de les lister.
6. Le champ `summary` ne sert pas de substitut faible a l'introduction et ne duplique pas le theme
   `Fil conducteur`.
7. Le theme `Fil conducteur` n'est pas rendu comme theme ordinaire s'il duplique l'introduction.
8. Chaque theme accepte contient au moins deux phrases informatives: sens astrologique vulgarise,
   manifestation possible, nuance ou lien avec le fil conducteur.
9. Le validateur refuse les phrases templates observees dans l'exemple utilisateur.
10. Le validateur refuse les labels anglais bruts dans le contenu public.
11. Les textes publics francais utilisent des accents et une formulation naturelle; les formes non
    accentuees issues de cles internes sont refusees dans le contenu public.
12. Le fallback deterministe ne peut plus produire le texte mecanique observe; s'il est conserve,
   il reste derive du plan, marque `fallback_used=True`, et rejette/audite selon le workflow
   existant quand le seuil editorial n'est pas atteint.
13. Les disclaimers restent presents mais ne comptent pas comme contenu redactionnel.
14. Le profil fixture equivalent a `daconrilcy@hotmail.com` produit un contrat public lisible et
   borne au plan.
15. Aucune garde CS-409 a CS-418 n'est affaiblie.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short
python -B -m pytest -q tests/unit/test_basic_natal_narrative_validator.py tests/unit/test_basic_natal_reading_contracts.py --tb=short
python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short
python -B -m pytest -q app/tests/unit/test_astrology_translation_resolver.py --tb=short
```

Scans:

```powershell
rg -n "cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node" backend/app backend/tests
rg -n "\\b(Synthese|theme|themes|repere|planetaire|a integrer)\\b" backend/app/domain/astrology/interpretation backend/app/domain/llm/runtime backend/app/services/llm_generation/natal backend/tests
rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input|chart_json|natal_data" backend/app/domain/astrology/reading backend/app/domain/llm/runtime backend/app/services/llm_generation/natal
rg -n "SIGN_NAMES_FR|SIGN_LABELS|PLANET_LABELS|NODE_LABELS|ASPECT_LABELS|\\bSIGNS\\s*=\\s*\\[" backend/app/domain/astrology backend/app/domain/llm/runtime backend/app/services/llm_generation/natal
```

Les hits doivent etre classes: denylist/test negatif/evidence historique ou fuite bloquante.

## Dependances

- CS-409 a CS-418.
- CS-419 pour le contrat public free/basic stabilise.
- CS-424 complete cette story sur le prompt final rendu au provider.
- CS-425 doit invalider ou regenerer les lectures historiques produites avant ce contrat
  redactionnel.

## Risques

Le risque principal est de remplacer un texte exact mais illisible par un texte agreable qui invente.
La story doit donc ameliorer le brief redactionnel et la validation sans desserrer le lien au
`BasicNatalReadingPlan`.

Risque secondaire: corriger les libelles en recreant des tables astrologiques locales. Toute
traduction doit passer par un owner existant ou etre classee comme formatage derive, avec scan
anti-referentiel concurrent.
