<!-- Commentaire global: ce document borne la retention des journaux d'acces admin aux audits de reponses IA en attente de decision RGPD finale. -->

# Retention des acces `admin_answer_audit_v1`

Les evenements d'acces admin aux audits de reponses IA doivent etre conserves
dans le store canonique `audit_events` tant que la politique RGPD finale n'a pas
fixe une duree precise pour ce type de trace sensible.

## Regle provisoire

- La duree de retention definitive reste dependante de la decision RGPD produit.
- Les evenements doivent rester minimaux: identite admin, action, cible,
  statut, justification sure et raison technique bornee si necessaire.
- Les details ne doivent pas contenir de prompt brut, payload de preuve, secret,
  date de naissance, heure de naissance, lieu de naissance, coordonnees ou
  timezone brute.
- Aucune route client, replay ou store d'acces separe ne doit etre cree pour
  lire ces evenements.

## Decision attendue

La decision RGPD finale devra preciser la duree, le declencheur de purge et les
eventuelles exceptions legales. Tant que cette decision n'existe pas, les
implementations doivent reutiliser `AuditService.record_event` et le modele
`audit_events` afin d'eviter une retention divergente.
