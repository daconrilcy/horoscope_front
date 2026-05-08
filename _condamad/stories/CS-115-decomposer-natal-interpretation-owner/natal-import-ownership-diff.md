<!-- Diff d'ownership des imports natals apres CS-115. -->

# CS-115 Natal Import Ownership Diff

Allowed API/feature owners:
- `components/NatalInterpretation.tsx`: API orchestration natal, billing type.
- `components/natal-interpretation/NatalInterpretationPersonaSelector.tsx`: sous-container persona avec `useAstrologers` et `AstrologerGrid`.

Presentational API-free files:
- `NatalInterpretationContent.tsx`
- `NatalInterpretationEvidence.tsx`
- `NatalInterpretationMenus.tsx`
- `NatalInterpretationTypes.ts`

Guard evidence:
- `npm run test -- component-architecture` verifies the owner split and API-free presentational files.
