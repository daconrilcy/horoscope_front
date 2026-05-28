# CS-370 - Documenter Synthese Nouvelle Structure JSON Theme Astral LLM

<!-- Commentaire global: ce brief cadre la production d'un document de synthese de la nouvelle structure JSON envoyee au LLM pour le theme astral. -->

## Resume

Produire un document de synthese clair et maintenable qui decrit la nouvelle structure JSON envoyee au LLM pour la feature `theme_astral` apres implementation du contrat cible.

## Contexte

Le nouveau contrat remplace les anciens payloads divergents par un squelette stable. Les plans commerciaux ne doivent plus definir des structures differentes; ils resolvent un `delivery_profile` qui module la densite, les quantites, les budgets et la profondeur de retour.

La documentation doit permettre a un developpeur, un product owner ou un futur editeur de prompts de comprendre rapidement:

- ce qui est commun a tous les plans;
- ce qui varie selon le delivery profile;
- quelles donnees sont visibles par le LLM;
- quelles donnees restent backend-only;
- comment les textes d'interpretation alimentent la redaction;
- comment la voix d'astrologue influence le style.

## Objectif

Creer un document de reference de la nouvelle structure JSON `theme_astral`.

## Perimetre inclus

1. Lire l'architecture CS-363.
2. Lire l'implementation finale CS-364 a CS-367.
3. Lire la review CS-369 si elle existe.
4. Documenter le squelette JSON final.
5. Documenter chaque bloc, son role, sa source et sa visibilite.
6. Documenter les differences attendues entre delivery profiles.
7. Ajouter des exemples courts de champs pour illustrer, sans reproduire un payload complet.
8. Ajouter un diagramme Mermaid de construction du JSON.
9. Ajouter un diagramme Mermaid des frontieres backend-only / LLM-visible.

## Hors perimetre

- Generer les payloads complets par plan; cela appartient a CS-371.
- Modifier le code.
- Modifier les contrats DB.
- Appeler un provider LLM.

## Sources obligatoires

- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `_condamad/audits/theme-astral-prompt-contract/**`
- `backend/app/domain/**`
- `backend/app/services/**`
- `backend/app/ops/**`
- `backend/tests/**`

## Livrable attendu

Creer ou mettre a jour:

```text
_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md
```

## Structure attendue du document

1. Resume executif.
2. Principes de construction.
3. Frontiere backend-only / LLM-visible.
4. Squelette JSON canonique.
5. Description des blocs:
   - `runtime_contract`;
   - `safety_contract`;
   - `astrologer_voice`;
   - `feature_context`;
   - `delivery_profile`;
   - `input_data.birth_context`;
   - `input_data.astrological_facts`;
   - `input_data.interpretation_material`;
   - `input_data.selected_themes`;
   - `input_data.limits`;
   - `output_contract`.
6. Variations par delivery profile.
7. Contrat de retour demande au LLM.
8. Diagrammes Mermaid.
9. Checklist de validation.
10. Liens vers les exemples complets CS-371.

## Squelette canonique a documenter

```json
{
  "runtime_contract": {},
  "safety_contract": {},
  "astrologer_voice": {},
  "feature_context": {},
  "delivery_profile": {},
  "input_data": {
    "birth_context": {},
    "astrological_facts": {},
    "interpretation_material": {},
    "selected_themes": {},
    "limits": {}
  },
  "output_contract": {}
}
```

## Contraintes de documentation

- Ne pas dire que le LLM recoit le plan commercial.
- Expliquer que `delivery_profile` est une resolution backend du plan.
- Expliquer que les textes d'interpretation viennent des tables et restent source-tracables cote backend.
- Expliquer que les preuves techniques, hashes, traces, migrations, IDs internes sensibles et audit complet restent backend-only.
- Expliquer que l'astrologue influence le style, le ton, les emphases et le lexique, pas les faits.
- Expliquer que le contrat de sortie varie en profondeur mais reste explicite.

## Criteres d'acceptation

1. Le document permet de comprendre le JSON sans lire le code.
2. Le squelette canonique est present.
3. Chaque bloc a une description, une source et une regle de visibilite.
4. Les differences entre delivery profiles sont expliquees sans exposer `free`, `basic` ou `premium` comme donnees LLM.
5. Deux diagrammes Mermaid valides sont presents.
6. Le document reference les audits, l'architecture et les exemples.
7. Le document ne contient pas de placeholder non resolu.

## Commandes de validation minimales

```powershell
rg -n "theme_astral_llm_input_v1|runtime_contract|safety_contract|astrologer_voice|delivery_profile|interpretation_material|output_contract" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md
rg -n "\{\{|TODO|TBD|free.*LLM|basic.*LLM|premium.*LLM" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md
```

## Risques

Le risque principal est de produire une documentation trop abstraite. Le document doit etre suffisamment concret pour servir de reference de maintenance et de validation des futurs changements de prompts.
