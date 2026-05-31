# No Legacy / DRY - CS-422

<!-- Commentaire global: ce fichier decrit les garanties anti-legacy et anti-duplication appliquees a CS-422. -->

## Decisions

- Pas de renderer Basic parallele: le changement reste dans `NatalInterpretationContent.tsx`.
- Pas de shim, alias, fallback silencieux ou branche legacy ajoutee.
- L'ancien rendu inline des sources Basic V2 est supprime, pas conserve via CSS ou prop `embedded`.
- La deduplication sources est centralisee dans `collectBasicPublicEvidence`.
- La deduplication legale est centralisee dans `mergePublicLegalLines`.
- Les branches free short et narrative v1 restent sur leurs chemins existants.

## Scans

- `rg -n "style=\\{" ...`: PASS no matches.
- `rg -n "ni-evidence-tags|ni-projections|LockedSection|NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" ...`: PASS no matches.
- `rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" ...`: PASS no matches.
- `rg -n "ni-public-evidence-inline|\\.ni-basic-theme \\.ni-content-card--public-evidence|<PublicEvidenceList embedded" ...`: PASS no active legacy inline source path.

## Guardrails

- `RG-170` existe deja dans le registre et protege l'annexe source unique + zone legale Basic V2 unique.
- Aucun nouvel invariant durable supplementaire n'a ete cree.
