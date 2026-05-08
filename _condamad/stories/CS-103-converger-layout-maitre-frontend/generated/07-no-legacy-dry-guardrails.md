# CS-103 - No Legacy / DRY

- Aucun second master layout cree.
- `RootLayout` devient l'unique owner du fond global.
- `AppLayout` ne conserve pas de wrapper de compatibilite.
- Guard executable contre `RootLayout` non monte et fond duplique dans `AppLayout`.
