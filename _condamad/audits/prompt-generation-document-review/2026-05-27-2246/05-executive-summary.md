<!-- Commentaire global: synthese executive courte de l'audit CS-353 des processus paralleles LLM. -->

# Executive Summary

Decision: `parallel processes confirmed; documentation correction required`.

The audit confirms active provider-capable prompt-generation paths outside the modern natal `llm_astrology_input_v1` flow: guidance, contextual guidance, public chat and daily horoscope narration. They reuse `AIEngineAdapter` or `LLMGateway`, but their prompt-visible inputs are textual summaries, chat context or daily prediction context rather than the rich modern natal carrier.

Recovery and fallback paths are non-nominal. Repair is invoked after invalid output and re-enters the gateway as a repair call. The fallback catalog owner is `backend/app/domain/llm/prompting/catalog.py`, not the absent `configuration/catalog.py`; current catalog fallback prompts are synthetic test entries. Bootstrap seeds are provisioning inputs, not runtime truth.

Two decision points remain: `event_guidance` still carries a `chart_json` bootstrap/contract surface without a public trigger found in the audited guidance routes, and admin manual execution is admin-only but provider-capable with sample payload context. No application code was changed.

