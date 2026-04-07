# toute page :
    - Finaliser le mode dark
    - proposer : dark/clear + systeme

# page login :
    - l'oeil du dragon se deplace vers le bas lorsque l'utilisateur le survole
    - Ajouter un bouton pour se connecter avec google
    - Ajouter un bouton pour se connecter avec facebook
    - Dans le cadre de signup, mettre en oeuvre un systeme de validation du mail (code envoyé par mail)

# page dashboard
    - Ne sert à rien, il faut le supprimer => remplacer par la page horoscope

# page natal
    - Mettre un spin pendant que l'utilisateur attend le résultat de son theme natal
    - Il y a une repetition entre la section consacrée au planetes qui inclut les maisons alors qu'il y a une section consacrée aux maisons
    - Les aspects : on ne comprend pas les implications : orbe, sextile, conjonction, carre,etc. : on ne comprend pas ce que cela veut dire. Il faut clarifier. Reformuler et peut etre repartir par thematique.

#LLM :
    - Encore trop de mots techniques / abreviation liés à l'astrologie (MC, AS, etc) passe au travers des reponses de LLM. Prevoir securite pour eviter cela + filtre dans l'app.

## Correctifs livrés le 2026-04-07

- Rétablissement du routing applicatif pour éviter les pages vides :
  - `/chat/:conversationId`
  - `/astrologers`
  - `/astrologers/:id`
- Réintégration du wrapper visuel global `app-bg` dans le shell authentifié afin de réappliquer le fond clair standard en mode light sur les pages hors horoscope du jour.
- Stabilisation des tests front associés au shell, au routing, aux écrans admin et à l’abonnement.
- Vérification complète de la suite front : `npm --prefix frontend test` OK.
