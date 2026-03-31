---
description: Sauvegarder et envoyer le code sur Git sans demander de validation
---
// turbo-all

Ce workflow permet d'ajouter, de commiter et de pousser les modifications sur le dépôt distant de manière 100% automatique.

1. Évaluer l'état actuel : utilise `run_command` pour exécuter `git status`.
2. Ajouter les fichiers : utilise `run_command` pour exécuter `git add .`.
3. Créer le commit : utilise `run_command` pour exécuter `git commit -m "[Message pertinent généré par l'IA concernant les dernières modifications]"`.
4. Pousser vers le serveur : utilise `run_command` pour exécuter `git push`.
