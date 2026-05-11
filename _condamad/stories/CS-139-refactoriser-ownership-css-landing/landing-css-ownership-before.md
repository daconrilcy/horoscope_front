# Baseline CS-139 - ownership CSS landing

Baseline capturee avant patch depuis les scans et l'audit source.

- Source audit: `_condamad/audits/frontend-landing-page/2026-05-11-1706/01-evidence-log.md`, evidence `E-005`.
- Scan initial: `rg -n "^\s*--landing-" frontend\src\layouts\LandingLayout.css frontend\src\pages\landing -g "*.css"`.
- Etat initial constate: le bloc `.landing-layout` portait les roles transverses, navigation, mobile, footer, sections et hero dans un meme owner.
- Timers/SEO hors scope CS-139 detectes avant patch mais traites par CS-141 et CS-142.

## Groupes initiaux principaux

- `page`, `surface`, `accent`, `shadow`, `radius`, `type`: roles transverses.
- `navbar`, `language`, `mobile`, `overlay`: navigation et menu mobile encore declares dans `LandingLayout.css`.
- `hero`, `live`: hero preview encore declare dans `LandingLayout.css`.
- `footer`, `text`: footer et texte dark encore declares dans `LandingLayout.css`.
- `icon`, `rating`, `problem`: sections marketing encore declarees dans `LandingLayout.css`.

## Risque initial

Le namespace `--landing-*` avait un owner trop large et ne permettait pas de bloquer un nouveau groupe vague sans guard executable.
