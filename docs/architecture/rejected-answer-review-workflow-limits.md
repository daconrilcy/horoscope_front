<!-- Commentaire global: ce document borne la revue admin des réponses rejetées sans autoriser replay, support public ou correction automatique. -->

# Limites de revue des réponses rejetées

Le workflow `admin_answer_audit_v1` de revue des réponses rejetées est un outil
de diagnostic interne. Il permet de lire `rejection_reason`, les preuves
manquantes, les versions de prompt et de contrat, puis de qualifier un suivi
manuel.

## Corrections autorisées

- Préparer une story de correction de prompt lorsque la cause est éditoriale.
- Préparer une story de correction de contrat lorsque les champs ou versions
  audités sont incomplets.
- Préparer une story de validation lorsque les `evidence_refs` ou hashes doivent
  être durcis.

## Limites obligatoires

- La revue ne livre jamais une réponse rejetée au client.
- La revue ne modifie pas automatiquement les prompts.
- La revue ne rejoue pas une génération LLM rejetée.
- La revue ne crée pas de workflow de support public.
- La revue ne remplace pas la validation de contrat ou de preuves.

Les statuts internes `pending_review`, `under_review`,
`resolved_prompt_followup`, `resolved_contract_followup`,
`resolved_validation_followup` et `dismissed` servent uniquement au tri admin.
