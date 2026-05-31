# Politique de remediation quota natal transactionnel

Cette preuve durable documente la politique attendue pour `natal_chart_long` et
la regeneration corrective des lectures completes invalides.

## Debit quota

- `check_access_for_complete_generation` verifie l'acces avant generation sans
  consommer de quota.
- `consume_on_acceptance` est appele uniquement apres une lecture complete non
  cachee et non rejetee.
- Le debit reste dans la meme unite de travail applicative que la persistance et
  le `commit` de la lecture acceptee.
- Un rejet editorial, un rejet grounding, une erreur provider ou un echec de
  commit declenche un rollback ou une liberation de claim sans debit definitif.

## Remediation corrective

- Une lecture complete historique invalide est detectee par absence de payload
  narratif valide, chapitre manquant, contenu duplique ou sources vides.
- La regeneration corrective est reservee via
  `claim_corrective_regeneration_eligibility`; la ligne invalide devient
  temporairement `natal_corrective_regeneration_pending`, donc invisible des
  relectures publiques.
- La regeneration corrective est gratuite: `consume_on_acceptance` ne consomme
  rien quand `corrective_regeneration=True`.
- La reservation est idempotente: une seconde demande concurrente ne trouve plus
  la ligne invalide comme candidate publique active.
- En cas de rejet ou d'erreur, `release_corrective_regeneration_claim` restaure
  le `use_case` d'origine sans modifier silencieusement le texte historique.

## Frontend

Aucun changement React n'est attendu: le contrat public garde la route
`/v1/natal/interpretation` et les noms de champs existants. Les marqueurs
correctifs restent internes au backend.
