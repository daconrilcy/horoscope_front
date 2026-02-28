# Epic 21-27: Upgrade "Calcul Pro" (audit-grade)

Status: done

## Objectif

Passer le calcul natal au niveau "pro" avec reproductibilite, tracabilite forte et comparabilite externe.

## Decisions verrouillees

- Defaults: `engine=swisseph`, `zodiac=tropical`, `frame=geocentric`, `house_system=placidus`.
- `zodiac=sidereal` exige `ayanamsa` (defaut `lahiri`).
- `frame=topocentric` applique `altitude_m=0` si absente.
- House systems supportes: `placidus`, `whole_sign`, `equal`.
- Aspects: `conjunction`, `sextile`, `square`, `trine`, `opposition`.
- Tolerances Golden Pro:
  - planetes: `+-0.01deg`
  - angles (ASC/MC/cusp I/X): `+-0.05deg`

## Ordre d'execution et dependances

1. Epic 21 - Fondations ephermerides pro et observabilite engine.
2. Epic 22 - Pipeline temps strict UT puis option TT/DeltaT.
3. Epic 23 - Conventions de calcul configurables et tracees.
4. Epic 24 - Regles d'aspects versionnees (schools).
5. Epic 25 - Validation croisee "Golden Pro" sur dataset large.
6. Epic 26 - Robustesse lieu/timezone historique.
7. Epic 27 - Contrat API audit-grade final + documentation.

## Rollout par phases

- Phase 1 (`SWISSEPH_PRO_MODE`): stories 21.1 -> 22.2.
- Phase 2 (`SWISSEPH_PRO_MODE`): stories 23.1 -> 23.4.
- Phase 3 (`SWISSEPH_PRO_MODE`): stories 24.1 -> 27.2.

## Stories creees (ready-for-dev)

- 21.1 Packager les fichiers Swiss Ephemeris en prod
- 21.2 Initialisation SwissEph robuste + erreurs explicites
- 21.3 Observabilite perf engine swisseph
- 22.1 Standardiser le temps dans prepared_input
- 22.2 Ajouter DeltaT et JD TT optionnels
- 23.1 Exposer ruleset zodiac/ayanamsa/frame/house_system
- 23.2 Houses: Placidus + Whole Sign + Equal
- 23.3 Frame: geocentric vs topocentric
- 23.4 Zodiac: tropical vs sidereal + ayanamsa
- 24.1 Modele de regles d'aspects versionnees (schools)
- 24.2 Calcul aspects avec orbs et overrides
- 25.1 Dataset Golden Pro 50-200 cas
- 25.2 Script cross-tool report (dev-only)
- [x] 26.1 Timezone IANA derivee + source de verite
- 26.2 Gestion des dates historiques ambiguës (DST/fold)
- 27.1 Sortie API audit-grade standardisee
- 27.2 Documentation dev + endpoints + validation

