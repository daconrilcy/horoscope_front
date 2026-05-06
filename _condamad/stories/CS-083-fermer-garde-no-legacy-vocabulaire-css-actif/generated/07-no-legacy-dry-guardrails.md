<!-- Garde DRY et No Legacy CS-083. -->

# No Legacy / DRY Guardrails

Applicable guardrails: RG-049, RG-050, RG-052, RG-057, RG-060.

Decisions:

- Aucun registre secondaire cree.
- Aucune exception wildcard ajoutee.
- Les commentaires CSS actifs sont controles par Vitest.
- Les selectors runtime existants ne sont pas renommes.

Static guards:

- `legacy-style-policy.test.ts` couvre les commentaires CSS.
- `design-system-guards.test.ts` continue de couvrir les vocabulaires runtime critiques.

