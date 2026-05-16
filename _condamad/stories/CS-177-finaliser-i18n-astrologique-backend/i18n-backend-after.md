# Inventaire apres CS-177

- `AstrologyLabels` expose `sign_labels`, `planet_labels`, `aspect_labels`, `house_labels` et `effective_language_code`.
- `AstrologyTranslationResolver` résout les signes, planètes, aspects et maisons depuis les tables de traduction DB.
- `json_builder.py`, `shared/natal_context.py` et `pdf_export_service.py` ne portent plus les mappings locaux ciblés.
- `pdf_export_service.py` utilise le resolver canonique et tombe sur `AstrologyLabels.technical_fallback()` uniquement si la résolution DB est indisponible dans un contexte isolé.
- Le scan anti-retour ne trouve plus `PLANET_NAMES_FR`, `ASPECT_NAMES_FR`, `SIGN_LABELS`, `SIGN_NAMES_FR` ou `SIGNS = [` dans `app/services` et `app/domain/astrology`.
