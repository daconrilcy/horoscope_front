# CS-423 - QA Live Lecture Basic Natal Lisible

<!-- Commentaire global: ce brief cadre la validation finale live de la lecture Basic natal apres correction redactionnelle et rendu frontend. -->

## Resume

Valider sur `/natal` que le profil utilisateur `daconrilcy@hotmail.com` obtient une lecture Basic
lisible, exacte, non repetitive et sans fuite technique apres CS-421, CS-422, CS-424 et CS-425.

Cette story ne doit pas corriger le fond directement. Elle doit produire les preuves finales,
identifier les regressions restantes et fermer le cycle par des tests automatises et une capture
browser. Si une regression produit est detectee, elle doit etre classee dans le rapport QA et
renvoyee vers une story de correction, sauf ajustement strictement limite a un test ou un artefact
d'evidence incorrect.

## Analyse De L'exemple Initial

Baseline observee le 31/05/2026 18:22:

- le titre `Lecture natale Basic` est suivi d'un resume qui liste les sources;
- cinq themes utilisent la meme structure de phrase;
- les termes astrologiques sont exposes comme codes (`moon`, `sun`, `saturn`, `gemini`);
- la source `Ce que j'ai utilise...` apparait dans les themes puis en fin de lecture;
- les limites, mentions legales et footer legal se repetent;
- l'utilisateur ne peut pas comprendre ce que signifie son theme sans connaitre deja les codes.

Definition du resultat attendu:

- le rapport commence par une idee centrale comprehensible;
- chaque theme explique une dynamique humaine, pas seulement un fait astrologique;
- les sources sont visibles mais annexes;
- les mentions legales sont presentes une seule fois;
- les textes restent non fatalistes, non prescriptifs et sans invention hors plan.

## Objectif

Capturer une preuve executable que `/natal` respecte le standard de lecture Basic:

```text
Exactitude
=> chaque phrase astrologique publique reste reliee au BasicNatalReadingPlan.

Lisibilite
=> pas de dump de donnees, pas de jargon brut, pas de phrases templates.

Experience
=> pas de repetition de sources ni de mentions legales.
```

## Perimetre Inclus

1. Creer une fixture ou snapshot de payload Basic representatif du profil utilisateur exemple,
   anonymise si necessaire.
2. Ajouter un test backend ou contractuel qui verifie les tokens interdits du contenu initial:
   `cette lecture s'appuie uniquement`, `Ce repere retient`, `avec une confiance editoriale controlee`.
3. Ajouter un test frontend DOM qui extrait le texte rendu Basic et verifie:
   - maximum un bloc de sources;
   - maximum un titre de mentions legales;
   - absence de labels anglais bruts dans le corps principal;
   - absence de formes publiques non accentuees issues de cles internes quand la forme francaise
     accentuee existe;
   - absence de message `Lecture complete a regenerer`.
4. Executer une QA browser locale sur `/natal` avec l'utilisateur test
   `daconrilcy@hotmail.com`.
5. Capturer evidence avant/apres:
   - payload API;
   - extrait texte DOM;
   - screenshot desktop;
   - screenshot mobile;
   - rapport de validation.
6. Documenter les ecarts acceptes et les eventuels points restants.
7. Bloquer la QA si le profil live sert encore une lecture historique contenant les tokens
   interdits, meme si les fixtures automatisees passent.

## Hors Perimetre

- Modifier la generation backend.
- Modifier le rendu frontend.
- Ajouter un correctif produit sous couvert de QA.
- Faire une migration de toutes les lectures historiques.
- Changer les contrats Basic V2.
- Ajouter une nouvelle offre ou changer les quotas.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- Piece jointe utilisateur: DOM actuel `/natal` du 31/05/2026 18:22.
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `_story_briefs/cs-422-simplifier-rendu-basic-natal-sources-mentions-legales.md`
- `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`
- `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md`
- `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md` si la story a deja ete transformee.
- `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md` si la story a deja ete transformee.
- `_condamad/stories/CS-424-verifier-corriger-generation-prompts-basic-natal/00-story.md` si la story a deja ete transformee.
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/00-story.md` si la story a deja ete transformee.
- `backend/tests/integration/test_basic_natal_v2_pipeline.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- Backend/frontend evidence produits par CS-421 et CS-422.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-152` - pas de fuite technique dans les lectures publiques.
  - `RG-153` - `/natal` reste centree sur la lecture publique.
  - `RG-154` - denylist DOM publique respectee.
  - `RG-155` - pas de padding semantique ni de contenu duplique.
  - `RG-156` - couverture editoriale Basic diversifiee.
  - `RG-164` - Basic reste plan-backed.
  - `RG-165` - pas de PII, scores, chemins, raw IDs.
  - `RG-166` - draft Basic conforme au plan.
  - `RG-167` - Basic complete relit `basic-natal-reading-v1`.
  - `RG-168` - contrat public Basic V2 canonique.
  - `RG-169` - qualite redactionnelle Basic, seulement si cree par CS-421.
  - `RG-170` - anti-duplication DOM sources/mentions legales, seulement si cree par CS-422.
  - `RG-171` - prompt final Basic redactionnel, seulement si cree par CS-424.
  - `RG-172` - version editoriale Basic/cache, seulement si cree par CS-425.
- Required regression evidence:
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py tests/unit/test_basic_natal_narrative_validator.py --tb=short`
  - `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - Scans texte contre les tokens du baseline initial.
  - Browser QA locale `/natal` desktop + mobile.
  - Inventaire du cache utilisateur: prouver si la lecture observee vient d'une regeneration,
    d'une relecture cache compatible ou d'une donnee historique invalidee.
- Registry enrichment expected:
  - Non attendu, sauf si la QA formalise une nouvelle garde durable non couverte par CS-421/CS-422.
- Allowed differences:
  - Le texte exact varie selon provider/cache, mais les contraintes de lisibilite et de non-repetition
    restent fixes.

## Criteres D'acceptation

1. Le payload API Basic accepte ne contient pas les phrases templates du baseline initial.
2. Le texte DOM public ne contient pas `cette lecture s'appuie uniquement`, `Ce repere retient`,
   `avec une confiance editoriale controlee`.
3. Le texte DOM public ne contient pas les codes anglais bruts `moon`, `sun`, `saturn`, `north node`,
   `south node` dans le corps principal.
4. Le DOM public affiche une seule zone de sources publiques maximum.
5. Le DOM public affiche une seule zone de mentions legales maximum.
6. `/natal` n'affiche pas `Lecture complete a regenerer` pour une lecture Basic V2 valide.
7. Le rapport final contient une introduction, au moins trois themes explicatifs et une conclusion.
8. Les sources et disclaimers restent accessibles.
9. Les screenshots desktop et mobile montrent une lecture sans chevauchement ni overflow evident.
10. Le rapport de QA classe explicitement les ecarts restants: bloquant, acceptable ou hors scope.
11. Le rapport de QA indique l'origine de la lecture live: cache compatible, regeneration controlee
    ou fixture, et signale tout cache historique encore degrade.
12. Le snapshot DOM ne contient pas les formes non accentuees `Synthese`, `theme`, `repere`,
    `planetaire`, `a integrer` quand elles correspondent a des libelles publics attendus.
13. La QA est bloquante si le profil live sert encore une lecture historique contenant les tokens
    interdits; le rapport indique l'action attendue: cache compatible, regeneration declenchee ou
    lecture legacy invalidee.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py tests/unit/test_basic_natal_narrative_validator.py --tb=short
cd ..
```

Frontend:

```powershell
pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage
pnpm --dir frontend lint
pnpm --dir frontend build
```

Scans:

```powershell
rg -n "cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node" backend/app frontend/src backend/tests frontend/src/tests
rg -n "\\b(Synthese|theme|themes|repere|planetaire|a integrer)\\b" backend/app frontend/src backend/tests frontend/src/tests
rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" backend/app frontend/src
```

Evidence attendue:

```text
_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-api-after.json
_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-dom-text-after.txt
_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-desktop-after.png
_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-mobile-after.png
_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/validation.txt
_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/qa-report.md
```

## Dependances

- CS-421.
- CS-422.
- CS-424.
- CS-425.

## Risques

Le risque principal est de valider une fixture propre alors que le profil live reste degrade par le
cache. La QA doit distinguer fixture, cache existant, regeneration controlee et rendu browser.

Risque secondaire: transformer la story QA en story de correction. Toute correction produit doit
etre sortie du scope et rattachee a CS-421 ou CS-422, sauf correction d'un test ou d'un artefact
d'evidence manifestement faux.
