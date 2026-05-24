# CS-254 — Define AI Scoring And Narrative Input Contract From Canonical Runtime

## Résumé

Définir le contrat d'entrée pour scoring IA et narration à partir du runtime canonique, en empêchant les prompts de devenir source de vérité astrologique.

Cette story remappe `SC-ARCH-008`.

## Contexte

CS-243 sépare calcul, interprétation et narration. CS-244 montre que le produit a besoin de données structurées pour scoring et récit. CS-245 exige un contrat versionné entre runtime canonique, projection interprétative et LLM.

## Objectif

Créer ou cadrer un contrat interne de faits versionnés consommable par :

- scoring IA ;
- préparation narrative ;
- génération LLM ;
- debug contrôlé.

Ce contrat doit rester distinct des projections publiques et du prompt final.

## Périmètre inclus

1. Définir les champs structurels autorisés.
2. Définir les champs interprétatifs pré-narratifs autorisés.
3. Versionner le contrat.
4. Ajouter une garde contre les tokens narratifs dans le runtime de calcul.
5. Définir la relation avec les projections publiques.
6. Ajouter les tests boundary calcul/interprétation/narration.

## Hors périmètre

- Écrire des prompts.
- Intégrer un provider LLM.
- Décider une politique commerciale de scoring.
- Exposer le contrat comme API publique.
- Modifier le frontend.

## Contrat attendu

Le contrat doit séparer au minimum :

```text
structural_facts
interpretive_signals
readiness_flags
source_versions
masking_policy
public_projection_links
```

Les données narratives finales ne doivent pas remonter vers le calcul.

## Critères d'acceptation

1. Le contrat d'entrée IA/narration est versionné.
2. Les champs structurels et interprétatifs pré-narratifs sont séparés.
3. Les prompts et sorties LLM ne sont pas sources de vérité.
4. Les tests empêchent les tokens narratifs dans les modules de calcul.
5. Aucune intégration provider n'est ajoutée.
6. Les données publiques restent des projections contrôlées.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter les scans boundary et tests d'adaptation interprétative.

## Dépendances

- CS-248 pour trace/provenance si le scoring doit expliquer ses sources.
- CS-251 pour les projections produit.
- CS-252 pour les règles doctrinales.

## Risques

Le risque principal est de laisser une sortie narrative influencer le runtime calculatoire. Les dépendances doivent rester orientées calcul -> faits -> signaux -> narration, jamais l'inverse.
