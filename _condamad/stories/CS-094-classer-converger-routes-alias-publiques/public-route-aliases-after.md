<!-- Audit CS-094 apres convergence routes publiques. -->

# CS-094 After

Date: 2026-05-08

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `/today` | route public alias | historical-facade | aucun blocker externe trouve dans repo | `/dashboard/horoscope` | delete | scan `src/app src/tests` zero hit | moyen: anciens liens externes non audites |
| `/natal-chart` | route public alias | historical-facade | tests API adaptes sans route UI | `/natal` | delete | scan route zero hit | moyen: anciens liens externes non audites |
| `/birth-profile` | route public alias | historical-facade | aucun blocker externe trouve dans repo | `/profile` | delete | scan route zero hit | moyen: anciens liens externes non audites |

Liens internes HelpPage mis a jour vers routes canoniques.
