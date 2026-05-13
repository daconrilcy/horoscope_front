# No Legacy / DRY Guardrails

- Une seule structure runtime active: `HouseRuntimeData`.
- `HouseResult` peut rester comme alias d'import existant, mais ne doit pas
  devenir une deuxieme implementation.
- La compatibilite `sign` est limitee au payload public et doit porter un TODO
  explicite de suppression planifiee.
- Aucun mapping local signe -> planete ne doit etre introduit.
- Aucune logique astrologique ne doit etre ajoutee dans `json_builder.py`.
