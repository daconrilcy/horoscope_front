<!-- Snapshot apres CS-115 pour NatalInterpretation. -->

# CS-115 Natal Interpretation After

Line counts:
- `NatalInterpretation.tsx`: 458 lignes.
- `NatalInterpretationContent.tsx`: 191 lignes.
- `NatalInterpretationMenus.tsx`: 238 lignes.
- `NatalInterpretationEvidence.tsx`: 226 lignes.
- `NatalInterpretationPersonaSelector.tsx`: 64 lignes.

Responsibilities:
- `NatalInterpretation.tsx`: container API/runtime natal.
- `NatalInterpretationContent.tsx`: rendu presentational du contenu.
- `NatalInterpretationMenus.tsx`: menus, modal, skeleton et erreur.
- `NatalInterpretationEvidence.tsx`: helpers `formatEvidenceId`, `categorizeEvidence` et tags d'evidence.
- `NatalInterpretationPersonaSelector.tsx`: sous-container exact pour selection astrologue.

Focused tests:
- `natalInterpretationEvidence.test.ts` couvre les helpers extraits.
