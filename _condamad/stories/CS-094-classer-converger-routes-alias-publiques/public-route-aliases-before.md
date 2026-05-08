<!-- Baseline CS-094 des alias routes publiques. -->

# CS-094 Before

Date: 2026-05-08

| Route | Classification | Canonical replacement | Decision |
|---|---|---|---|
| `/today` | historical-facade | `/dashboard/horoscope` | delete |
| `/natal-chart` | historical-facade | `/natal` | delete |
| `/birth-profile` | historical-facade | `/profile` | delete |

Preuve initiale: routes presentes dans `frontend/src/app/routes.tsx`.
