# Starting a localization from the Chinese project

## What you can reuse

The input validation, Japanese source decoder, source-span indexes, target-table formats, address-preserving script redirection, audited native display overlay, BPS tools, ELF helpers, subset-font builder, procedural graphic compilers and bounded probe adapter form the reusable foundation.

The shipped translation is Simplified Chinese. Graphical text, UI constants, spelling choices and field budgets contain language-specific assumptions. A new language must review them, not merely replace dialogue strings.

## 1. Establish inputs and source identities

Use the exact Japanese ROM and EnglishV1.0.1 inputs identified in reference-build.json. Build.py validates their SHA-1 values before processing. EnglishV1.0.1 remains the technical base; Japanese remains the source-language reference.

Message-spans.json holds only offset/length pairs. Prepare_inputs.py reads local Japanese glyph tables and reconstructs each message, then checks the stable `ja-<content hash>` identity. It also regenerates native bank strings and off-bank references from local ROMs. Generated original text/raw bytes stay private.

Do not assume that English/Japanese dialogue at an equal address is the same message. The exported English reference is available for validated native/off-bank sources; script English correspondence is intentionally left blank.

## 2. Make a language pack

Run `scripts/new_locale.py <locale>`. The new pack is a Chinese starting copy; translate the target values and terminology. Stable file formats:

- `dialogue.zh.json`: `id`, `source_offset`, `zh` target text.
- `native.zh.json`: `string_id`, target text and identity/layout policies.
- `offbank.zh.json`: exact source locations, target text and typed reference metadata.
- Shared spans, description locations, script-table layouts and graphical-object metadata.

`zh` is a legacy builder key, not a restriction on your target language. Keep it until you deliberately refactor the builder. Edit CSV target columns and import them with import_catalog.py; source keys and policies are never imported from CSV.

Preserve engine controls, player placeholders, icon controls and the audited newline exceptions. Native `$`/`#` sequences and script `{...}` tokens are different formats. Do not translate encrypted password keys, resource selectors, script labels or item identities merely because they look like text.

## 3. Adapt the font and encoding

The existing engine uses a12px bitmap logical character in a16-row container. Each character has two physical6px halves. Ink rows2..13 must be read fully; cropping the first12 rows loses bottom strokes.

- Script custom character: `01 FE + uint16_le character ID`.
- Native custom codes: two codes per logical character, using leadsE8..FE and trails01..FF; no NUL and no FF lead.
- Current native capacity:2932 logical characters. The character subset includes script, native, auxiliary labels and image text requirements.
- Primary/compact fonts have separate original glyph counts and lookup tables. Never mix maps/fonts from different builds.

For accented Latin/Cyrillic/other scripts, check glyph width and coverage in your BDF. ASCII currently advances6px; non-ASCII target characters use the paired12px model. Complex shaping, right-to-left layout, ligatures and combining sequences are not implemented as universal language support. They require new rendering work and dedicated tests.

Use `--font` to supply another appropriately licensed compatible12px BDF. Existing bitmap compilers assume this geometry. Changing geometry requires updating those compilers, metrics and probes.

## 4. Adapt all graphical/UI text

Review `src/stage3/build_chapter1.py` and UI constants in stage4/build_redirect.py. The legacy module name holds four target UI constants only.

Review stage5 modules ending in `_assets.py`, equipment_model_labels.py and league_graphics.py. Some derive captions from the target ledger; others contain Chinese literals, custom bitmaps, scaling, three-character title assumptions or narrow-field abbreviations. Replace each deliberately and retain allocation/palette/OAM invariants.

Images are generated from locally supplied original graphics plus target glyphs. There are no bundled original game image files. Decode and preview ROM resources offline when checking a change. A resource preview is not proof of game timing or unlock progression.

## 5. Keep backend identity separate from display

ROM display lookup replaces only audited presentation pointers. It preserves original source bytes and backend selectors. Typed RAM copies additionally require exact caller/source/destination rules. NPC names and tournament titles use specific context/content guards; the human player's own name is protected.

Map inline labels are a typed exception to normal off-bank pointer-slot references: their source locations come from bounded original map records. Their source/name bytes remain unchanged; a map UI width wrapper and drawing-pointer lookup use target text only for display.

Do not broaden an exact policy into arbitrary RAM translation or a global string-length replacement. New routes need direct source/reference evidence and negative guard checks.

## 6. Verify by mechanism, then collect real feedback

Use pure checks and representative bounded CPU probes first. For paired glyphs, test remaining widths0/6/12px, both extended fonts and ordinary-glyph guards. Compare left/right glyph row coordinates and return stack balance. Buffer changes need exact source/caller guards, limits and unchanged numeric/backend data.

The provided adapter has no frame-driving, input automation or screenshot export API. It runs isolated calls and may bypass unchanged pixel blitters. These results do not prove a full story, a real reward interaction or every translated sentence.

Reuse unaffected evidence with its tested hash. A new build hash does not retroactively change the version on an old test report. Record actual scene feedback separately from structural/fixture evidence.

## 7. Package and attribute your work

A local build emits an EnglishV1.0.1→target BPS and confirms exact BPS reconstruction. Users apply Japanese→EnglishV1.0.1→your target patch. Do not apply a target patch over an older translated ROM.

Before public distribution, finalize the license/permission scope, retain font notices, and state that your localization is based on Ganenis’s English project and this Chinese toolkit. Give credit for each layer. Publish reviewed source/patch artifacts; keep ROMs, saves, full original catalogs and personal evidence private.
