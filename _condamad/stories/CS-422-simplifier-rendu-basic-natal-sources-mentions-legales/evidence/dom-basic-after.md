# DOM apres implementation - CS-422

<!-- Commentaire global: ce fichier resume la preuve DOM apres correction Basic V2. -->

Preuve executable:

- `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading`: PASS.
- `natalInterpretation.test.tsx`: Basic V2 verifie une seule occurrence du titre sources, une seule occurrence `Mentions legales`, une seule occurrence d'une source dupliquee par `source_id`, et metadata `Utilise dans : Axe personnel, Axe relationnel`.
- `natalPublicDomGuard.test.tsx`: Basic V2 verifie absence de source dans `.ni-basic-theme-list`, dedupe legal, et absence de marqueurs techniques.

Structure DOM Basic V2 attendue:

1. titre + introduction;
2. themes narratifs sans preuves inline;
3. conclusion;
4. annexe sources unique;
5. zone legale finale unique.
