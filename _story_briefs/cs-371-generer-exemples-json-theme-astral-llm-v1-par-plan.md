# CS-371 - Generer Exemples JSON Theme Astral LLM V1 Par Plan

<!-- Commentaire global: ce brief cadre la generation d'exemples JSON complets qui pourraient etre transmis au LLM apres implementation du nouveau contrat theme astral. -->

## Resume

Generer trois exemples JSON complets, un par plan commercial, representatifs de ce qui pourrait etre transmis au LLM apres implementation du nouveau contrat `theme_astral`. Les exemples doivent utiliser les donnees utilisateur suivantes: personne nee le 24/04/1973 a 11h00 du matin a Paris, France.

## Contexte

Les anciens exemples ont montre deux problemes:

- donnees de naissance incompletes ou incoherentes;
- payloads contenant des variables ou structures divergentes selon les plans.

Les nouveaux exemples doivent permettre de mesurer clairement la difference de densite entre les plans tout en conservant le meme squelette JSON.

## Donnees utilisateur

```text
Date de naissance: 24/04/1973
Heure de naissance: 11:00 du matin
Lieu de naissance: Paris, France
Feature: theme_astral
Plans a illustrer: free, basic, premium
```

## Objectif

Produire des payloads JSON finaux, non envoyes au moteur LLM, qui representent la sortie attendue du backend juste avant appel provider.

## Perimetre inclus

1. Utiliser l'implementation finale du nouveau contrat `theme_astral`.
2. Calculer ou recuperer les donnees astrologiques pour la naissance fournie.
3. Construire `interpretation_material` depuis les tables d'interpretation.
4. Resoudre le plan backend en `delivery_profile`.
5. Generer un JSON complet par plan:
   - free;
   - basic;
   - premium.
6. Verifier que les trois JSON ont le meme squelette.
7. Verifier que les differences portent sur quantite, profondeur, budgets et contrat de retour.
8. Verifier qu'aucun payload n'a ete envoye au provider LLM.
9. Documenter les differences observees.

## Hors perimetre

- Appeler le provider LLM.
- Generer la reponse redigee finale du LLM.
- Modifier le contrat.
- Reintroduire les anciens payloads legacy.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/**`
- `backend/app/services/**`
- `backend/app/ops/**`
- `backend/tests/**`

## Livrables attendus

Creer un dossier:

```text
_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/
```

Avec les fichiers:

```text
README.md
intermediate-data.json
free-provider-payload.json
basic-provider-payload.json
premium-provider-payload.json
structure-comparison.md
```

## Contraintes sur les JSON

Chaque payload doit:

- etre un JSON valide;
- representer le payload final juste avant appel provider;
- utiliser le meme squelette canonique;
- contenir des valeurs resolues, jamais des noms de variables;
- contenir `delivery_profile`, pas le plan commercial dans le contenu LLM-visible;
- contenir `astrologer_voice`;
- contenir `safety_contract`;
- contenir `feature_context`;
- contenir `input_data.birth_context`;
- contenir `input_data.astrological_facts`;
- contenir `input_data.interpretation_material`;
- contenir `input_data.selected_themes`;
- contenir `input_data.limits`;
- contenir `output_contract`;
- ne pas contenir de donnees audit-only dans les messages transmis au LLM;
- ne pas contenir de placeholder comme `{{variable}}`, `TODO`, `TBD` ou `example_value`.

## Differences attendues entre plans

Le fichier `structure-comparison.md` doit prouver que:

- la structure est identique;
- free contient une selection courte et priorisee;
- basic contient plus de faits, plus d'interpretations et plus de sections de retour;
- premium contient la plus grande densite de faits, d'interpretations, de themes croises et de contraintes de restitution;
- la voix de l'astrologue reste presente dans les trois plans;
- le contrat de sortie est plus riche selon le delivery profile;
- le plan commercial n'est pas expose comme instruction au LLM.

## Criteres d'acceptation

1. Les trois payloads JSON sont valides.
2. Les trois payloads concernent bien la naissance du 24/04/1973 a 11:00 a Paris, France.
3. Les trois payloads ont le meme squelette.
4. Les valeurs sont parsees et resolues.
5. `interpretation_material` est present et non vide dans les trois payloads.
6. Les quantites de faits et textes interpretatifs augmentent entre free, basic et premium.
7. Aucun payload n'a ete envoye au provider LLM.
8. `structure-comparison.md` explique clairement les differences.
9. `README.md` precise le scenario, la methode de generation et les commandes executees.

## Commandes de validation minimales

Depuis la racine du repository:

```powershell
Get-Content _condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\free-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content _condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\basic-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content _condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\premium-provider-payload.json | ConvertFrom-Json | Out-Null
rg -n "\{\{|TODO|TBD|example_value|24/04//1973" _condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1
rg -n "interpretation_material|delivery_profile|astrologer_voice|output_contract|1973-04-24|11:00|Paris" _condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1
```

Si un script backend est utilise pour generer les payloads:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q
```

## Risques

Le risque principal est de fabriquer des exemples a la main qui ne refletent pas le code. Les JSON doivent etre produits par le chemin applicatif final ou par un script de generation qui reutilise les memes builders que le runtime.
