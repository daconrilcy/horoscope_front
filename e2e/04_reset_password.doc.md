# Test E2E — Reset Password (Manuel)

Ce scénario est **manuel** car il nécessite l'intervention de Mailpit pour vérifier l'email de réinitialisation.

## Prérequis

- Mailpit doit être démarré et accessible sur `http://localhost:8025`
- Le backend doit être configuré pour envoyer les emails via Mailpit

## Étapes manuelles

1. **Aller à la page reset request**
   - Naviguer vers `/reset/request`
   - Entrer un email valide (ex: `test@example.com`)

2. **Soumettre le formulaire**
   - Cliquer sur "Envoyer"
   - Vérifier le message de succès affiché

3. **Vérifier l'email dans Mailpit**
   - Ouvrir `http://localhost:8025` dans un navigateur
   - Trouver le dernier email reçu pour `test@example.com`
   - Extraire le token de réinitialisation depuis le lien dans l'email

4. **Aller à la page reset confirm**
   - Naviguer vers `/reset/confirm?token=<TOKEN_EXTRAIT>`
   - Vérifier que le formulaire s'affiche correctement

5. **Remplir et soumettre le nouveau mot de passe**
   - Entrer un nouveau mot de passe
   - Confirmer le nouveau mot de passe
   - Soumettre le formulaire

6. **Vérifier la redirection**
   - Vérifier que la redirection vers `/login` s'effectue
   - Vérifier le message de succès affiché

## Notes

- Ce test ne peut pas être automatisé facilement car il nécessite:
  - L'accès à Mailpit pour extraire le token
  - La manipulation manuelle de l'email
- Pour automatiser, il faudrait:
  - Un endpoint backend de test qui expose les tokens générés
  - Ou une API Mailpit pour récupérer les emails par programmation
  - Ce n'est pas dans le scope actuel (100% local, pas de CI)

