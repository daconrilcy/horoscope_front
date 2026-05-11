# Baseline CS-142 - SEO/head landing

Baseline capturee avant patch.

- Fichier initial: `frontend/src/pages/landing/LandingPage.tsx`.
- Scan initial: `rg -n "document\.|AC[0-9]" frontend\src\pages\landing\LandingPage.tsx frontend\src\pages\landing -g "*.tsx"`.
- Hits initiaux: `document.title`, `document.querySelector`, `document.createElement`, `document.head.appendChild`, `document.getElementById` dans `LandingPage.tsx`.
- Commentaires story-era initiaux: `AC2`, `AC1`, `AC1.1.4` dans `LandingPage.tsx` et `AC1.3` dans `TestimonialsSection.tsx`.

## Tags geres initialement

- `title`.
- `meta[name="description"]`.
- `og:title`, `og:description`, `og:type`, `og:url`.
- `link[rel="canonical"]`.
- JSON-LD `json-ld-app` et `json-ld-faq`.
