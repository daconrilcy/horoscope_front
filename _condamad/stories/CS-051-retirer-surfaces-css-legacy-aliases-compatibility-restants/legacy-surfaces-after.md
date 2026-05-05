<!-- Inventaire after des surfaces legacy CS-051. -->

# CS-051 Legacy Surfaces After

| Item | Resultat |
|---|---|
| `.chat-layout-mobile-action-legacy` | supprime de `App.css`; zero-hit final |
| Registry `.chat-layout-mobile-action-*` | entree retiree car la surface active canonique vit dans `ChatPage.css` |
| Surfaces admin legacy actives | conservees et classees, suppression bloquee par consommateurs TSX actifs |
| Alias token `--text-*`, `--glass*`, `--primary*` | conserves, consommateurs actifs hors lot |

No shim, wrapper, fallback ou alias nouveau introduit.

