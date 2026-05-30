# CS-394 - Ajouter « Ce Que Nous Avons Utilise » En Fin De Lecture Natale

<!-- Commentaire global: ce brief cadre la justification astrologique vulgarisee de fin de lecture /natal. -->

## Resume

Ajouter apres les cinq chapitres narratifs un bloc replie « Ce que nous avons utilise » qui
explique les principaux appuis astrologiques en langage lisible. Ce bloc doit satisfaire le
lecteur curieux sans reexposer les calculs ou les identifiants internes.

## Contexte

La page possede deja plusieurs surfaces de preuve:

- `EvidenceTags` formate des identifiants comme `SUN_TAURUS_H10`;
- `NatalAstrologicalDna` affiche des `explanation_facts`;
- les projections B2C exposent `support_elements`, `interpretive_signals` et `audit_input`;
- `NatalAstrologerMode` reserve les donnees techniques detaillees.

La justification publique doit etre un niveau intermediaire: assez claire pour repondre
« pourquoi dites-vous cela ? », mais sans scores, syntaxe moteur ni traces d'audit.

## Objectif

Afficher a la fin de la lecture:

```text
Ce que nous avons utilise

- Venus dominante - les relations et la recherche d'harmonie structurent votre lecture.
- Soleil conjoint Venus - votre expression personnelle et votre besoin de lien se renforcent.
- Milieu du Ciel en Belier - votre vocation demande initiative et autonomie.
```

## Perimetre inclus

1. Introduire un composant presentational `NatalReadingSources`.
2. Lire `used_astrological_elements` depuis le contrat narratif public.
3. Afficher une liste courte repliee par defaut avec `aria-expanded` et navigation clavier.
4. Ne jamais afficher `title={rawEvidenceId}`, score, centrality, rank technique,
   `condition_axis:*`, codes adapter, identifiants audit ou payload provider.
5. Repositionner ou retirer `EvidenceTags` de la lecture publique principale.
6. Conserver les details complets dans `NatalAstrologerMode`.
7. Ajouter tests et i18n FR/EN/ES/DE.

## Hors perimetre

- Modifier la generation backend.
- Ajouter des calculs React pour produire les explications.
- Supprimer le mode astrologue.
- Afficher les `evidence_refs` backend-only.

## Sources obligatoires

- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalAstrologerMode.tsx`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/tests/natalInterpretationEvidence.test.ts`
- `backend/docs/narrative-natal-reading-v1-contract.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - aucun style inline statique.
  - `RG-052` - reutiliser les tokens CSS canoniques.
  - `RG-071` - conserver le rendu de preuve dans un composant dedie.
  - `RG-073` - ne pas recreer d'orchestration API dans `components/**`.
  - `RG-129` - ne pas recalculer de justification astrologique en React.
  - `RG-150` - ne pas afficher de contenu issu d'un rejet.
- Required regression evidence:
  - `pnpm --dir frontend test -- natalInterpretationEvidence natalInterpretation NatalAstrologerMode`
  - `rg -n "title=\\{.*evidence|condition_axis|centrality|interpretive_signal|audit_input|explanation_facts" frontend/src/components/natal-interpretation frontend/src/features/natal-chart`
- Allowed differences:
  - Remplacement de la surface publique `EvidenceTags` par la justification vulgarisee.

## Criteres d'acceptation

1. Le bloc « Ce que nous avons utilise » apparait apres les cinq chapitres.
2. Le bloc est replie par defaut et accessible au clavier.
3. Chaque element possede un libelle astrologique lisible et une consequence courte.
4. Aucun identifiant brut, score ou trace d'audit n'est rendu dans le DOM public.
5. `EvidenceTags` n'expose plus de raw evidence ID dans la lecture publique principale.
6. Le mode astrologue conserve les details experts existants.
7. Les quatre locales publiques ont un wording coherent.

## Commandes De Validation Minimales

```powershell
cd frontend
pnpm test -- natalInterpretationEvidence natalInterpretation NatalAstrologerMode
pnpm lint
pnpm build
```

## Dependances

- CS-392.
- CS-393.

## Risques

Le risque principal est de deplacer la fuite technique plutot que de la supprimer. Les tests
doivent inspecter le DOM public et verifier l'absence des identifiants internes.
