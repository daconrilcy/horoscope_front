<!-- Commentaire global: registre CS-308 des formulations refusees ou reportees pour les lectures publiques de /natal. -->

# CS-308 Refused Wording

audit_date: 2026-05-26
route: /natal

| projection_type | state | source_file | current_text | decision | final_text | reason | product_decision_owner | evidence_path |
|---|---|---|---|---|---|---|---|---|
| beginner_summary_v1 | success | `frontend/src/i18n/natalChart.ts` | Résumé débutant | refused | Résumé découverte | "Débutant" peut sonner infantilisant dans une expérience B2C. | none | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/refused-wording.md` |
| shared_projection_panel | success | `frontend/src/i18n/natalChart.ts` | Lecture complète | refused | Interprétation client | "Complète" aurait impliqué un niveau produit et une promesse de couverture non validés. | Product si réouverture | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/refused-wording.md` |
| shared_projection_panel | degraded | `frontend/src/i18n/natalChart.ts` | Lecture exacte malgré données manquantes | refused | Lecture partielle : des données de naissance manquent. | Formulation déterministe incompatible avec le mode dégradé. | none | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/refused-wording.md` |
| shared_projection_panel | disclaimer | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Disclaimer depuis payload | refused | App-owned disclaimers only | La politique interdit de faire dépendre les mentions légales du payload LLM/projection. | none | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/refused-wording.md` |
