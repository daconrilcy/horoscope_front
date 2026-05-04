<!-- Inventaire final des styles inline TSX apres politique CS-029. -->

# Inline Styles After

Guard: `npm run test -- inline-style`.

Resultat:

- Les styles statiques des trois fichiers audites ont ete deplaces vers CSS.
- Les styles inline restants sont inventories par test et documentes via
  `frontend/src/tests/inline-style-allowlist.ts` quand ils representent des
  valeurs dynamiques.
