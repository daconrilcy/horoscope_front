# App CSS TSX consumers after CS-127

| Class / primitive | Before consumers | After consumers | Decision |
|---|---|---|---|
| `.notice` | none | `features/auth/SignInForm.tsx` | introduced primitive composition |
| `.state-centered` | none | `app/routes.tsx` | introduced primitive composition |
| `.select-card` | none | `components/dashboard/DashboardCard.tsx`, `features/consultations/components/AstrologerSelectStep.tsx`, `pages/ConsultationsPage.tsx` | introduced primitive composition |
| `.form-control` | none | `components/ui/Field/Field.tsx` | introduced primitive composition |
| `.stack` | none | `features/auth/SignInForm.tsx` | introduced primitive composition |
| `.cluster` | none | `pages/ConsultationsPage.tsx` | introduced primitive composition |
