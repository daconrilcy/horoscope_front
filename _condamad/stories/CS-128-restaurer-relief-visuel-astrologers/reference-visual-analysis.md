<!-- Analyse visuelle de reference pour cadrer la remise a niveau /Astrologers. -->

# Reference Visual Analysis - /Astrologers

Source: capture fournie par l'utilisateur le 2026-05-09.

## Details stylistiques a retrouver

- Fond de page: degrade pastel rose/violet avec voile diffus et bruit tres discret; la page ne doit pas devenir un aplat blanc ou une surface neutre.
- Conteneur principal: colonne centree et compacte, largeur proche de 600px, effet glass clair, coins arrondis et ombre externe douce.
- Header: titre compact sombre, sous-titre gris-violet, espacement serre; pas de hero marketing.
- Grille: premiere carte en pleine largeur, cartes suivantes en deux colonnes desktop, empilement mobile.
- Cartes: surface translucide avec radial highlight interne, ombre basse douce, bord colore par theme, relief visible sans effet lourd.
- Carte mise en avant: bord bleu/cyan plus lisible, ombre cyan/violet et halo interne; elle doit garder plus de presence que les cartes secondaires.
- Petit logo/icon: pastille ronde coloree en haut a gauche de chaque carte, avec symbole astrologique/persona lisible et teinte themee.
- Avatar: photo ronde avec ombre et leger liseret lumineux; la photo ne doit pas etre plate ni collee au fond.
- Badges de specialites: chips petits, colores par theme, translucides, bordes, avec texte compact.
- Typographie carte: nom sombre en gras, nom d'affichage en petites capitales pale, style en texte court, bio legere.
- Transparences: les surfaces gardent une impression verre/papier translucide; pas de badge provider visible sur la liste compacte.
- Couleurs par persona: Orion cyan, Luna rose, Atlas violet, Nox violet profond, Etienne bleu clair, Selene dore.

## Points a ne pas reproduire litteralement

- Aucun style inline.
- Aucun ajout de selecteur ou token page-specific directement dans `frontend/src/App.css`.
- Aucun nouveau fichier sous `frontend/src/styles/app/` sans decision explicite de type owner.
- Aucun badge provider visible si cela surcharge la page compacte par rapport a la capture.
