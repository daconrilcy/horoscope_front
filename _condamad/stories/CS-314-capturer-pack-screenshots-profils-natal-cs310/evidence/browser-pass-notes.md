# Browser pass notes CS-314

Date: 2026-05-26

Capture effectuee dans Chromium via le frontend Vite local sur `/natal`.
Les routes API appelees par la page sont servies de facon deterministe par le script Playwright pour rejouer les cinq profils synthetiques CS-310 sans modifier l'application.

Aucune anomalie reproductible n'a ete observee pendant la capture; `anomaly-ledger.json` reste vide.

Sortie Vite condensee:
```text
> frontend@0.0.0 dev
> node ./scripts/run-vite-logged.mjs vite vite-dev dev --host 127.0.0.1 --port 4173


  [32m[1mVITE[22m v7.3.2[39m  [2mready in [0m[1m190[22m[2m[0m ms[22m

  [32m➜[39m  [1mLocal[22m:   [36mhttp://127.0.0.1:[1m4173[22m/[39m

```
