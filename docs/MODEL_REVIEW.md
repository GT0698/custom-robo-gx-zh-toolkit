# Optional model-assisted review method

This project separates deterministic checks from language judgment. A model may review a small set of uncertain terms/conditions; it does not decide that a whole ROM is correct or automatically overwrite translations.

1. Generate local candidates with source/target IDs and a specific reason: term disagreement, possible reversed condition, a number or a field-budget issue.
2. Remove candidates already reviewed with unchanged source/target hashes. A terminology mismatch can be a valid contextual abbreviation; keep that possibility explicit.
3. Send only the necessary original/target text and short context, not the entire project/chat, ROM, save or private evidence. Set explicit input/output/call limits and avoid tool access or recursive agents for this task.
4. Require structured results with `id`, `verdict`(`keep`, `fix`, `needs_context`) and `reason`. Validate IDs, duplicates, schema and content hashes before considering the answer.
5. The maintainer checks original context and accepts/rejects changes. A model's unneeded rewrite should be discarded.
6. Save decisions with source/target SHA-256, reviewer role and reason. Reuse only while both hashes match.
7. Rebuild changed targets and test the affected mechanism. Same-renderer lines do not require repeated gameplay/image-recognition/model loops.

Providers and credentials are intentionally not configured here. Use your own local review workflow. This method is applicable to other languages, with locale-specific terminology and cultural decisions.
