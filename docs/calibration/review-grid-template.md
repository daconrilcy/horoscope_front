# Template de Grille de Revue de Calibration

Ce document sert de support a la validation metier des notes produites par le moteur apres calibration.

## Legende des Bandes UX

- **fragile** : Note <= 5
- **tendu** : 6 <= Note <= 9
- **neutre** : 10 <= Note <= 12
- **porteur** : 13 <= Note <= 16
- **tres favorable** : Note >= 17

## Grille de Revue

Colonnes obligatoires :
- `Date`
- `Categorie`
- `Raw Day`
- `Note/20`
- `Bande UX`
- `Top Contributeurs`
- `Commentaire`

Colonnes d'enrichissement :
- `Power`
- `Volatilite`

| Date | Categorie | Raw Day | Note/20 | Bande UX | Power | Volatilite | Top Contributeurs | Commentaire |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| YYYY-MM-DD | category_code | 0.XXX | XX | band_name | 0.XXX | 0.XXX | rule_1, rule_2 | Exemple : Note coherente avec le climat du jour |
<!-- Les lignes suivantes seront generees par le script generate_review_grid.py -->
