# MVP Fiscalite et Facturation Stripe

Ce document fixe le cadre MVP pour la fiscalite indirecte et les factures Stripe. Stripe reste la seule source de verite fiscale: le backend ne calcule aucune taxe, ne maintient aucune table de taux et ne reconstruit aucun montant fiscal canonique.

## 1. Decision fiscale MVP

Deux modes sont supportes:

- Option A (recommandee): `STRIPE_TAX_ENABLED=true`
- Option B (derogatoire): `STRIPE_TAX_ENABLED=false`

Decision de lancement retenue pour le MVP:

- Pays autorises au lancement: France et pays de l'Union europeenne pour lesquels une tax registration Stripe est effectivement configuree avant mise en production
- Vente B2B: oui
- Collecte du tax ID client: oui via `STRIPE_TAX_ID_COLLECTION_ENABLED=true`
- Source de verite fiscale: Stripe

Contraintes de l'option B:

- Elle n'est acceptable que sur un perimetre geographique explicitement restreint et documente avant lancement
- Aucun calcul fiscal n'est alors fait par l'application
- Toute extension de perimetre impose une revalidation legale et une reconfiguration Stripe avant ouverture

## 2. Configuration backend

Variables d'environnement:

| Variable | Valeur par defaut | Description |
| :--- | :--- | :--- |
| `STRIPE_TAX_ENABLED` | `false` | Active `automatic_tax` dans la Checkout Session d'abonnement. |
| `STRIPE_TAX_ID_COLLECTION_ENABLED` | `false` | Active `tax_id_collection` pour la collecte B2B. |
| `STRIPE_CHECKOUT_BILLING_ADDRESS_COLLECTION` | `auto` | Valeurs autorisees: `auto` ou `required`. Toute autre valeur est invalide et bloque le demarrage backend. |

`billing_address_collection` est toujours envoye a Stripe Checkout:

- `auto`: Stripe collecte uniquement les informations minimales necessaires
- `required`: Stripe force la saisie de l'adresse complete

Quand `STRIPE_TAX_ENABLED=true`, `auto` suffit techniquement pour laisser Stripe demander les donnees de localisation minimales. `required` reste un choix produit plus strict si l'on veut exposer l'adresse complete dans le parcours.

## 3. Triptyque obligatoire Stripe Tax

Activer `automatic_tax=true` dans le code ne suffit pas. Le MVP depend de trois prerequis:

1. `automatic_tax[enabled]=true` sur la Checkout Session.
2. Des `tax_code` et `tax_behavior` coherents sur les Product/Price Stripe utilises par le checkout.
3. Au moins une tax registration active dans `Dashboard > Taxes > Registrations` pour le perimetre geographique cible.

Details catalogue Stripe:

- `tax_behavior` doit etre explicitement `inclusive` ou `exclusive`
- `tax_behavior=unspecified` n'est pas acceptable pour ce MVP
- Le `tax_code` doit correspondre a la categorie fiscale reelle du service vendu

Sans tax registration, Stripe accepte l'API mais peut ne calculer aucune taxe. Ce point ne peut pas etre garanti par le code applicatif et fait partie de la checklist pre-lancement.

## 4. Tax ID client et impact sur les factures

Quand `STRIPE_TAX_ID_COLLECTION_ENABLED=true`:

- Checkout inclut `tax_id_collection={"enabled": true}`
- Si le customer Stripe existe deja, Checkout ajoute `customer_update={"name": "auto", "address": "auto"}`
- Effet de bord assume: le nom et l'adresse saisis pendant le checkout peuvent remplacer les valeurs deja presentes sur le customer Stripe

Configuration Dashboard requise:

- Les account tax IDs du compte Stripe doivent etre renseignes dans le Dashboard pour apparaitre correctement sur les factures emises
- Les tax registrations correspondant au perimetre MVP doivent etre configurees avant lancement

Contrainte importante:

- Une invoice Stripe finalisee ne peut pas etre modifiee a posteriori pour corriger un tax ID oublie ou incorrect

## 5. Factures et surfaces de consultation

Le MVP ne cree aucun endpoint applicatif dedie aux factures:

- Aucun `GET /v1/billing/invoices`
- Aucun proxy backend vers `hosted_invoice_url`
- Aucun stockage local de PDF de facture

Les surfaces Stripe utilisees sont:

- Stripe Customer Portal
- Hosted Invoice Page Stripe

Pour que l'historique soit exploitable, la configuration Customer Portal doit activer:

- `invoice_history`
- les billing information du client
- les tax IDs client si le MVP B2B est actif

## 6. Checklist pre-lancement

Verifier avant mise en production:

1. `STRIPE_TAX_ENABLED` est aligne avec la decision MVP retenue.
2. Le perimetre geographique autorise est explicite et compatible avec les registrations Stripe actives.
3. Tous les Product/Price exposes ont un `tax_code` et un `tax_behavior` valides.
4. `invoice_history` est active dans la configuration Customer Portal.
5. Les billing information et tax IDs client sont actives dans le portail si le MVP B2B est maintenu.
6. Les account tax IDs Stripe sont renseignes pour les entites emettrices concernees.

## 7. Hors perimetre

Le MVP n'implemente pas:

- de moteur fiscal interne multi-pays
- de table locale TVA/VAT/GST
- de recalcul fiscal sur webhook
- de stockage local des factures PDF
- d'UI applicative custom pour afficher les taxes ou l'historique des factures
