# Notes browser-equivalent CS-310

Date: 2026-05-26

La story autorise une execution manuelle ou une simulation navigateur equivalente. Cette passe utilise:

- le ledger navigateur CS-306 pour confirmer que `/natal` affiche les deux projections B2C en desktop et mobile;
- les tests `NatalChartPage` pour confirmer les etats degrade, incomplete data et absence de crash;
- les tests `natalInterpretation` pour confirmer loading, empty, error, entitlement, degraded, projections visibles et mentions legales applicatives;
- les tests backend projection pour confirmer le contrat public et le cas `birth_input` sans heure.

Limite: aucune capture nouvelle n'a ete produite pour CS-310; la preuve est un ledger QA trace par profil et des validations executables.

## Mapping de preuve par profil

- `cs310-precise-time-paris`: chemin success `/natal` prouve par captures Chromium CS-306 desktop/mobile et POST projections B2C par `chart_id`.
- `cs310-missing-time-paris`: chemin degrade prouve par `degraded_mode=no_time`, projection `state=degraded`, et backend `birth_input` sans heure.
- `cs310-foreign-location-tokyo`: chemin lieu/fuseau etranger traite comme normalisation de contrat; aucune branche UI pays n'existe dans `/natal`.
- `cs310-controlled-incomplete`: chemin erreur bornee prouve par alertes 404/422, etat erreur projection, et erreurs backend publiques.
- `cs310-standard-lyon`: chemin success standard prouve par le rendu des deux cartes B2C et mentions legales applicatives.

Finding review corrige: la premiere review d'implementation a juge le lien profil -> simulation -> resultat visible trop implicite pour AC2.
Chaque ligne du ledger contient maintenant `execution_trace` pour rendre la preuve auditable sans relire les tests complets.
