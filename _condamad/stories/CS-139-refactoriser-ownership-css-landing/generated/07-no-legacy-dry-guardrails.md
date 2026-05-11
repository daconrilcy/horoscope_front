# No Legacy / DRY CS-139

Interdits vérifiés:
- `app-bg--landing`
- `style=`
- groupes `--landing-misc-*`, `--landing-common-*`, `--landing-temp-*`, `--landing-shared-*`, `--landing-base-*`, `--landing-general-*`, `--landing-global-*`
- owner CSS landing non classé.

Résultat:
- aucun alias, wrapper, fallback ou owner concurrent introduit;
- les valeurs ont été routées vers des owners locaux existants;
- le guard `design-system` porte une carte finie des groupes landing.
