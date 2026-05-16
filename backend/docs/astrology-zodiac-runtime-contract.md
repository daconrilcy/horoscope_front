# Contrat runtime zodiaque, ayanamsa et signes

Cette page documente le flux canonique du calcul natal entre le service
applicatif, le provider Swiss Ephemeris et le mapping longitude vers signe.

## Responsabilites

`backend/app/services/natal/calculation_service.py` valide les options
utilisateur du calcul natal. Il refuse une demande sidérale explicite sans
ayanamsa, applique les valeurs par défaut configurées quand la demande ne
précise pas le zodiaque, puis transmet les options normalisées au domaine.

`backend/app/domain/astrology/ephemeris_provider.py` est le propriétaire de
l'application tropicale ou sidérale. En mode sidéral, il appelle
`swe.set_sid_mode`, récupère `get_ayanamsa_ut`, calcule les longitudes avec le
flag sidéral, puis réinitialise l'état Swiss Ephemeris après l'appel.

`backend/app/domain/astrology/zodiac.py` est uniquement le propriétaire du
mapping géométrique entre une longitude déjà calculée et l'un des douze signes.
`sign_from_longitude` normalise la longitude dans `[0, 360)`, divise le cercle
en tranches de 30 degrés et choisit le signe selon l'ordre canonique chargé
depuis `docs/db_seeder/astrology/astral_signs.json`.

## Regle ayanamsa

`sign_from_longitude` n'applique pas l'ayanamsa. Il ne choisit pas non plus le
zodiaque tropical ou sidéral. Le zodiaque et l'ayanamsa sont appliqués en amont
par `ephemeris_provider.py`; `sign_from_longitude` reçoit donc une longitude
déjà exprimée dans le référentiel demandé.

## Gardes

Commandes de preuve à exécuter depuis `backend` après activation du venv:

```powershell
pytest -q tests/unit/domain/astrology/test_zodiac.py app/tests/unit/test_ephemeris_provider.py
pytest -q app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py app/tests/unit/test_natal_calculation_service.py
rg -n "def .*sign.*longitude|ZODIAC_SIGNS|ayanamsa.*sign_from_longitude|set_sid_mode" app/domain/astrology app/services/natal -g "*.py"
```

Résultat attendu:

- `test_zodiac.py` prouve le mapping par tranches de 30 degrés.
- `test_ephemeris_provider.py` prouve le périmètre Swiss Ephemeris.
- `test_golden_zodiac_sidereal_ayanamsa.py` prouve l'écart tropical/sidéral.
- `test_natal_calculation_service.py` prouve la validation applicative.
- Le scan ne doit révéler aucun helper concurrent de longitude vers signe ni
  documentation/code affirmant que `sign_from_longitude` applique l'ayanamsa.
