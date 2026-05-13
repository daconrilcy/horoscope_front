# Execution Brief

Implementer une representation runtime riche des maisons dans
`backend/app/domain/astrology`, puis exposer cette structure dans le payload
public sans deplacer de logique astrologique vers `services/chart`.

Contraintes:

- runtime uniquement;
- pas de nouvelle migration SQL;
- source canonique des rulers: `sign_rulerships`;
- pas de fallback hardcode signe -> planete;
- compatibilite publique `sign` documentee comme champ legacy planifie.
