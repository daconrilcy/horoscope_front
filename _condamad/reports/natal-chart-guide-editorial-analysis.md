<!-- Analyse editoriale anonymisee du guide de lecture du theme natal public. -->

# Analyse éditoriale du guide `natal-chart-guide`

## Sources examinées

- Le contenu du guide n'est pas enregistré dans le backend. Il appartient au dictionnaire
  `frontend/src/i18n/natalChart.ts` et est rendu par `frontend/src/components/NatalChartGuide.tsx`.
- Les lectures Astral terminées sont persistées dans
  `user_astral_natal_themes.response_payload`.
- Le corpus local anonymisé contient deux lectures Basic récentes et uniques : une lecture
  de dix chapitres et une lecture de six chapitres.
- Les contrats et exemples Basic/Premium du dépôt complètent ce corpus local, qui ne contient
  pas de lecture Premium récente.

Aucune date de naissance, position astrologique personnelle, identité, clé technique ou texte
individualisé n'est reproduit dans ce rapport.

## Évolution observée

Les lectures récentes ne demandent plus seulement de comprendre la géométrie d'un cercle natal.
Elles proposent une synthèse puis des chapitres comme l'identité, la vie émotionnelle, les
relations, la vocation, les talents, les conflits intérieurs et le chemin de croissance. Chaque
chapitre combine plusieurs indices astrologiques, avec un rôle principal, d'appui ou de nuance.

| Notion utilisée dans les lectures | Couverture de l'ancien guide | Manque constaté | Réponse du nouveau guide |
|---|---|---|---|
| Synthèse et chapitres thématiques | Absente | Le lecteur ne sait pas par où commencer | Parcours conseillé en quatre étapes |
| Planète, signe, maison et aspect | Très technique | La relation entre les quatre repères reste abstraite | Formule « quoi / comment / où / dialogue » |
| Soleil, Lune et Ascendant | Partielle | Le rôle de chacun n'est pas expliqué simplement | Carte dédiée aux trois premiers repères |
| Maisons et axes dominants | Absente | Une dominante peut être prise pour une prédiction | Explication de la répétition d'un thème et de son contrepoint |
| Maître d'une maison | Absente | Le lien entre une maison et une planète est opaque | Définition courte avec analogie du « fil conducteur » |
| Facteur principal, appui et nuance | Absente | La hiérarchie des bases astrologiques n'est pas lisible | Métaphore équipe : moteur, soutien, modérateur |
| Confiance de lecture | Absente | Le niveau de confiance peut être confondu avec une certitude | Distinction entre solidité des indices et vérité personnelle |
| Aspects fluides ou tendus | Géométrique | Risque de lecture « bon contre mauvais » | Présentation en dynamiques de facilité, tension et ajustement |
| Heure manquante ou données partielles/imprécises | Présente pour l'heure manquante | Le signal applicatif couvre aussi les lectures simplifiées | Note contextuelle sur Ascendant, maisons, Lune et aspects |
| Vocabulaire de calcul | Très détaillé | Les degrés, intervalles et passages à 0° prennent trop de place | Mini-glossaire limité aux termes rencontrés dans la lecture |

## Principes éditoriaux retenus

1. Partir de l'expérience de lecture plutôt que du calcul.
2. Définir un terme avant de l'utiliser et limiter chaque carte à une idée principale.
3. Employer des exemples génériques et des analogies, jamais une affirmation déterministe.
4. Présenter les tensions comme des possibilités d'ajustement, pas comme des défauts.
5. Inviter le lecteur à observer ce qui résonne sans transformer la lecture en diagnostic ou
   en prédiction certaine.

## Garde-fous de mise en œuvre

- `RG-182` : conserver une lecture progressive, scannable et accessible.
- `RG-183` : préserver une colonne mobile sans débordement et des contrôles tactiles.
- `RG-184` : réutiliser la largeur, la typographie et les tokens visuels de `/natal`.
- `RG-187` : préserver le parcours débutant, ses traductions, son accessibilité et son
  affichage mobile en une colonne.
- Différences autorisées : contenu, structure interne et styles de `natal-chart-guide`.
- Différences interdites : contrats backend, soumission Astral, composition des chapitres et
  données publiques du thème natal.
