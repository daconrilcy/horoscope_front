# CS-342 - Cloturer Le Process Evidence Hors Prompt Et Validation Redaction LLM Natale

<!-- Commentaire global: ce brief cadre la preuve finale que les evidences restent hors prompt et servent bien a valider la redaction LLM natale. -->

## Resume

Produire une validation finale apres CS-341 pour prouver que le process est definitivement ferme:

- aucune evidence n'est envoyee au prompt engine natal moderne;
- le prompt ne contient plus de bloc `evidence` vide;
- la redaction obtenue du LLM est validee cote backend contre les donnees et preuves internes;
- l'audit conserve les informations necessaires pour expliquer la decision.

## Contexte

CS-339/CS-340 ont ferme la fuite `provenance` / hashes audit-only. CS-341 doit fermer l'ambiguite restante autour du bloc `evidence`: il n'est pas utile de transmettre les evidences au LLM, mais il est indispensable d'utiliser ces preuves pour controler la redaction produite.

Cette story est une cloture de preuve, pas une nouvelle fonctionnalite LLM.

## Prerequis

La story suivante doit etre terminee:

- CS-341 - Sortir evidence du prompt et valider la redaction LLM natale.

## Source obligatoire

Lire avant validation:

- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`
- `_condamad/reports/cs-339-cs-340-delivery-report.md`
- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md`

## Objectif

Verifier et documenter la frontiere finale:

- prompt-visible: uniquement les donnees qui guident la redaction;
- validation-only / audit-only: evidences, refs, hashes, statut de grounding et decisions de validation;
- output LLM: redaction structuree ou assez inspectable pour etre controlee;
- audit: trace les donnees ayant servi a accepter, rejeter ou marquer partiellement conforme la redaction.

## Perimetre inclus

1. Verifier par tests et scans que `evidence` n'est plus dans les blocs prompt-visible canoniques.
2. Verifier par test de handoff provider que le message utilisateur natal ne contient pas:
   - `evidence`;
   - `evidence_refs`;
   - `grounding_status`;
   - `validation_owner`;
   - `projection_hash`;
   - `llm_input_hash`;
   - `provenance`.
3. Verifier que les evidences restent disponibles dans l'objet interne complet et dans l'audit persistant.
4. Verifier que la validation post-generation couvre au moins:
   - une redaction conforme;
   - une redaction qui invente une donnee absente;
   - une redaction qui contredit une limite ou un missing data;
   - une redaction non groundee par les evidences internes.
5. Scanner les prompts, registries, schemas et fixtures pour detecter toute dependance a `{{evidence}}`, `{{evidence_refs}}` ou `evidence: {}`.
6. Produire un rapport de validation final dans `_condamad/reports`.
7. Classer les occurrences restantes d'evidence:
   - validation/audit ownerise;
   - contrat interne non prompt;
   - test de garde;
   - documentation historique;
   - dette a corriger.

## Hors perimetre

- Implementer un nouvel appel provider reel.
- Modifier le contenu editorial fin des prompts au-dela du strict necessaire.
- Reprendre l'extinction legacy `chart_json` / `natal_data` deja couverte.
- Modifier le frontend ou les endpoints publics.
- Supprimer les evidences de l'audit.

## Livrable attendu

Creer un rapport:

```text
_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/<YYYY-MM-DD-HHMM>/validation-evidence-hors-prompt.md
```

Le rapport doit contenir:

1. Resume de la correction verifiee.
2. Definition finale des blocs prompt-visible.
3. Definition finale des roles evidence/validation/audit.
4. Preuve de handoff provider sans evidence.
5. Preuve de validation post-generation avec cas positif et negatif.
6. Resultats de scans.
7. Commandes de validation executees.
8. Risques residuels.

## Criteres d'acceptation

1. Le rapport de validation existe au chemin attendu.
2. `evidence` est absent de `prompt_visible`.
3. Le payload provider natal moderne ne contient aucun champ evidence/provenance/hash/audit.
4. L'audit persistant conserve les evidences, refs, hashes et statuts necessaires.
5. La validation post-generation utilise les evidences internes pour accepter ou rejeter une redaction.
6. Les tests incluent au moins un cas positif et deux cas negatifs d'invention ou de contradiction.
7. Aucun prompt ou fixture active ne depend d'un bloc `evidence` vide.
8. Les validations backend passent.
9. Les occurrences restantes sont classees sans ambiguite.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short
pytest -q tests --tb=short
rg -n "evidence|evidence_refs|grounding_status|validation_owner|prompt_visible|validation_only|audit_only|llm_input_hash|projection_hash|provenance" app tests ..\_condamad ..\_story_briefs
rg -n "{{evidence}}|{{evidence_refs}}|{{grounding_status}}|\"evidence\": \{\}|prompt_payload\\[\"evidence\"\\]" app tests
```

La validation ne doit pas exiger l'absence totale du vocabulaire evidence dans le depot. Elle doit prouver que les occurrences restantes sont hors prompt provider et servent a la validation, a l'audit ou aux guards.

## Risques

Le risque principal est une fausse cloture: retirer les evidences du prompt mais ne valider que la forme JSON de la reponse LLM. La cloture doit prouver une validation semantique minimale contre les donnees internes, meme si elle reste locale et testee avec des doubles.

