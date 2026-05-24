# CS-274 — Define astrology_full_data_v1 Internal Expert Projection

## Résumé

Définir `astrology_full_data_v1` comme projection interne complète pour usage expert astro.

## Contexte

Un expert astro peut avoir besoin de données plus complètes qu'une projection technique synthétique. Cette surface reste interne, protégée et distincte du debug techno.

## Objectif

Spécifier une projection astrologique complète, orientée expertise métier, sans l'exposer au client.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les familles de données astrologiques complètes.
2. Distinguer données métier astro et debug calcul.
3. Définir les règles de masquage des données personnelles.
4. Définir les dépendances à `structured_facts_v1`.
5. Définir les conditions d'accès et journalisation.

## Hors périmètre

- Implémenter la projection.
- Ajouter une UI expert.
- Ajouter replay ou logs techniques.
- Exposer fixed stars au client.

## Critères d'acceptation

1. `astrology_full_data_v1` est documentée comme projection interne.
2. Elle est réservée admin/futur expert astro.
3. Elle est séparée de `admin_chart_diagnostics_v1`.
4. Les données personnelles sont masquées ou justifiées.
5. Les dépendances factuelles et versions source sont explicites.

## Validation attendue

```powershell
rg -n "astrology_full_data_v1|expert astro|interne|diagnostics|structured_facts" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-273 pour la projection technique expert.
- CS-271 pour les permissions.

## Risques

Le risque principal est de mélanger projection métier complète et replay/debug. Ces surfaces doivent rester distinctes.



