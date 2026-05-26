<!-- Commentaire global: cette procedure borne l'activation Plausible sans accepter de collecte production non validee. -->

# Plausible Activation Procedure

Statut: `production_validation_required`

Provider cible: `plausible`

Variables requises:

- `VITE_ANALYTICS_PROVIDER=plausible`
- `VITE_ANALYTICS_ENABLED=true`
- `VITE_ANALYTICS_DOMAIN=<approved Plausible site domain>`
- `VITE_ANALYTICS_API_HOST=https://plausible.io` ou hote Plausible self-hosted approuve

Procedure staging:

1. Configurer les quatre variables dans l'environnement staging seulement.
2. Charger le script Plausible correspondant au domaine approuve.
3. Executer le parcours `/natal` et les CTA analytics couverts par CS-316.
4. Verifier dans Plausible que seuls les noms d'evenements publics et les props redacted sont visibles.
5. Conserver une preuve d'observation externe avant toute promotion production.

Procedure production:

1. Obtenir l'accord explicite du responsable environnement et du responsable produit.
2. Reprendre CS-318 avec l'environnement Plausible observable.
3. Confirmer l'ingestion des evenements attendus sans `birth_date`, `birth_time`, `birth_place`, coordonnees, prompt, raw runtime ou provider response.
4. Marquer l'activation comme acceptee uniquement apres preuve externe.

Condition de reprise CS-318:

CS-318 peut reprendre quand un domaine Plausible et un acces d'observation staging ou production sont fournis. Cette story ne remplace pas cette validation externe.
