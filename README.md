# Custom Robo GX — Simplified Chinese Localization Toolkit

[中文说明](README.zh-CN.md)

**This is a Simplified Chinese localization built on top of Ganenis’s [Custom Robo GX Full English translation V1.0.1](https://github.com/Ganenis/Custom-Robo-GX-English).** The Japanese game script is the translation reference; the English localization provides the patched engine/base ROM and a secondary language reference. Credit for the English project belongs to Ganenis.

The repository is a reproducible development snapshot and a starting point for other language projects. It contains Chinese target tables, extraction/build tools, ARM/Thumb display hooks, bitmap-asset compilers and testing methods. Full single-player/postgame acceptance remains incomplete. The latest three UI fixes have engineering evidence and await normal user confirmation.

## Repository contents

| Path | Purpose |
|---|---|
| `data/` | Target translations, source locations, terminology and layout policies |
| `src/stage4/` | Original script restoration, exact message redirection and subset font |
| `src/stage5/` | Native display overlay, whole-glyph wrapping and image compilers |
| `src/catalog/` | Audited identity, control and bounded buffer rules |
| `scripts/` | Portable build, local catalog export/import and language-pack creation |
| `src/runtime/` | Optional bounded mGBA probes without gameplay/input/screenshot APIs |
| `docs/` | Localization guide, architecture, verification and release notes |
| `third_party/fusion_pixel/` | Font and its original license notices |

The stage numbers preserve legacy module paths for compatibility. They are not the current project roadmap.

## 1. Install and open the toolkit

Extract the source ZIP and open a terminal in its `custom-robo-gx-zh` directory. Alternatively, download or clone the public repository: `git clone https://github.com/GT0698/custom-robo-gx-zh-toolkit.git custom-robo-gx-zh`. All commands below run from this directory. The core build requires Python 3.9+ and Clang supporting `armv4t-none-eabi`; it uses the Python standard library. Pillow is optional for offline previews. No API key, paid model or emulator is needed for the build.

### macOS

Install the Apple command-line tools if they are not installed:

```sh
xcode-select --install
```

Finish the installer before continuing. If Python 3.9+ is absent, install Python from [python.org](https://www.python.org/downloads/). Then:

```sh
cd /path/to/custom-robo-gx-zh
python3 --version
clang --version
python3 -m venv .venv
. .venv/bin/activate
```

### Ubuntu / Debian Linux

```sh
sudo apt-get update
sudo apt-get install -y python3 python3-venv clang
cd /path/to/custom-robo-gx-zh
python3 --version
clang --version
python3 -m venv .venv
. .venv/bin/activate
```

Confirm Python is at least 3.9. For Windows, use Ubuntu under WSL and follow the Linux commands; a native Windows build has not been validated. macOS is the environment used for the reference rebuild; the Linux commands are setup instructions, not a claim of an independently verified Linux build.

Check the compiler target and source-only tests:

```sh
mkdir -p .build
printf 'int probe(void) { return 0; }\n' > .build/clang-probe.c
clang --target=armv4t-none-eabi -mthumb -c .build/clang-probe.c -o .build/clang-probe.o
python3 tests/run.py
python3 scripts/verify_public.py
```

For optional image-preview dependencies:

```sh
python3 -m pip install -r requirements.txt
```

In a new terminal, return to the project and run `. .venv/bin/activate` again. Replace all `/path/to/...` placeholders below with your own paths; keep quotes around paths with spaces. Store inputs outside the public source tree.

## 2. Build the bundled Chinese version

Provide these exact inputs:

| Input | Required SHA-1 |
|---|---|
| Japanese ROM | `0b5ce051aa1fd83ab0ec79122b07b02bb41096a5` |
| English V1.0.1 ROM, when used instead of BPS | `e033251c780dbbd83b15623159b743d2e624d8a0` |

Obtain the **English V1.0.1 BPS** from [Ganenis's releases](https://github.com/Ganenis/Custom-Robo-GX-English/releases), extract the downloaded archive, and pass the `.bps` file, not the ZIP. Supply your own Japanese ROM. Neither ROM nor the English patch is bundled here.

Recommended reference build:

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-bps "/path/to/english-v1.0.1.bps" \
  --verify-reference
```

If you already have the exact English V1.0.1 ROM:

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom "/path/to/english-v1.0.1.gba" \
  --verify-reference
```

Successful reference output has SHA-1 `3815c71e19ee66bc071475ff725d65fa17f339c4`. The isolated source export has reproduced this ROM byte-for-byte. `--verify-reference` checks the bundled, unchanged Chinese build; omit it after changing translations, fonts or code.

Default outputs:

- `.build/artifacts/custom-robo-gx-zh.gba`: open this local ROM in a GBA emulator.
- `.build/artifacts/custom-robo-gx-zh.bps`: **English V1.0.1 → Chinese** patch.
- `.build/artifacts/custom-robo-gx-zh.manifest.json`: input/output hashes, counts and patch round-trip result.
- `.build/artifacts/reports/`: generated engineering reports.

The builder validates inputs, reconstructs source text locally, runs catalog audits, compiles scripts/fonts/native display hooks/images, and verifies that its BPS reconstructs the target exactly. Complete Japanese/English catalogs are not shipped. Keep `.build/` private.

A target BPS is applied in this order: **Japanese → English V1.0.1 → target language**. Do not apply it directly to Japanese or over another Chinese build. The built `.gba` is already patched. Keep ordinary saves backed up; do not load an older ROM's emulator instant state into a new build.

## 3. Make another language version

### A. Generate the English ROM locally for catalog export

The exporter accepts an English ROM, not BPS. If you only have the English BPS, create this private input once:

```sh
mkdir -p .build/inputs
python3 src/tools/bps.py \
  "/path/to/japanese.gba" \
  "/path/to/english-v1.0.1.bps" \
  .build/inputs/english-v1.0.1.gba
```

The BPS CLI checks CRCs and refuses to overwrite an existing output. The subsequent exporter checks both ROM SHA-1 values. If you already have the exact English ROM, use its path instead of `.build/inputs/english-v1.0.1.gba` in subsequent commands.

### B. Create and export a language pack

Example: French (`fr`). Replace `fr` consistently with your locale tag.

```sh
python3 scripts/new_locale.py fr
python3 scripts/export_catalog.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom .build/inputs/english-v1.0.1.gba \
  --translations locales/fr \
  --output .build/catalogs-fr
```

This creates `locales/fr/` and three private UTF-8 CSVs: `dialogue.csv`, `native.csv`, `offbank.csv`. A new pack is a **copy of Chinese translations, not an automatically translated French pack**. Each CSV has `id`, `source_offset`, `ja`, `en_reference`, `target`. Edit only `target`; preserve IDs, rows, CSV quoting, placeholders and controls. The Japanese column is authoritative. Dialogue `en_reference` is intentionally blank because equal ROM addresses do not establish Japanese/English correspondence.

Do not commit source CSVs. Import target values only:

```sh
python3 scripts/import_catalog.py --pack locales/fr --kind dialogue --csv .build/catalogs-fr/dialogue.csv
python3 scripts/import_catalog.py --pack locales/fr --kind native --csv .build/catalogs-fr/native.csv
python3 scripts/import_catalog.py --pack locales/fr --kind offbank --csv .build/catalogs-fr/offbank.csv
```

Blank `target` cells are skipped and retain the previous value. Unknown or duplicate IDs fail. The files retain the legacy names `*.zh.json` and target field `zh` even for French; do not rename these without changing the builder. Review the copied glossary and `locale.json` separately; CSV import does not update them.

### C. Build your pack

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom .build/inputs/english-v1.0.1.gba \
  --translations locales/fr \
  --output .build/artifacts-fr/custom-robo-gx-fr.gba
```

To use your own compatible, licensed 12px BDF font:

```sh
python3 scripts/build.py \
  --japanese-rom "/path/to/japanese.gba" \
  --english-rom .build/inputs/english-v1.0.1.gba \
  --translations locales/fr \
  --font "/path/to/compatible-12px.bdf" \
  --output .build/artifacts-fr-v2/custom-robo-gx-fr.gba
```

Outputs use the requested ROM stem: `.gba`, `.bps`, `.manifest.json`, plus `reports/` in the same directory. Use a new output directory/version for each changed build. The builder refuses to overwrite an existing ROM if its bytes differ; catalog export and language-pack creation also refuse existing destinations. Use a new catalog directory when exporting again.

## 4. What you must adapt for a new language

| Area | Required work |
|---|---|
| Text and terminology | Replace all Chinese target values and copied glossary entries; preserve controls, player placeholders, resource/item identities and actual password keys. Partial translation builds still contain Chinese. |
| Fonts and encoding | Ensure all target glyphs exist. ASCII advances 6px; non-ASCII currently uses two 6px halves forming a 12px logical glyph in a 16-row container. Native capacity is 2,932 logical custom characters. Wider glyphs, combining marks, shaping and right-to-left writing need renderer/encoding work. |
| Line wrapping and fields | Recheck menu widths, buffers, abbreviations, alignment and line counts. Whole-glyph Chinese wrapping is not word-aware wrapping for Latin languages. Do not widen all buffers or change backend identity rules globally. |
| Fixed UI constants | Adapt `src/stage3/build_chapter1.py` and auxiliary labels in `src/stage4/build_redirect.py`; CSVs do not cover every literal. |
| Image text | Review `src/stage5/*_assets.py`, `equipment_model_labels.py` and `league_graphics.py`. Some captions/bitmaps are hardcoded Chinese and have fixed geometry. A locale pack alone does not translate these images. Preserve palettes, tiles, pointers and non-overlapping allocations. |
| Tests and acceptance | Run source/catalog/build checks and representative bounded function probes for changed rendering paths. Engineering checks do not prove full story, rewards or postgame acceptance; collect actual user feedback separately. |
| Release | Retain English-base and toolkit attribution plus font notices. Finalize the applicable permissions/licenses. Distribute reviewed source/patches without ROMs, saves, source catalogs or personal configuration. |

See [localization guide](docs/LOCALIZATION_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [testing](docs/TESTING.md) and [verification](docs/VERIFICATION.md) for details. Optional mGBA probes require a separately built matching mGBA library; they are not required for ROM construction and do not automate gameplay.

## 5. Checks, troubleshooting and licensing

```sh
python3 tests/run.py
python3 scripts/verify_public.py
```

- `Wrong Japanese ROM` / `English input must beV1.0.1`: check exact input versions; do not bypass the hash check.
- Clang target failure: ensure `clang` on PATH supports the target shown in the installation check.
- Missing glyph/control/length audit failure: fix the font, target text or audited layout; do not disable validation.
- `Reference build differs`: only use `--verify-reference` for the unchanged reference pack/font/code.
- Existing output/catalog/locale error: select a new path, preserving your prior work.

CI checks source/export safeguards and pure BPS/input-decoder tests, without ROMs. It does not claim game acceptance. See [contribution rules](CONTRIBUTING.md).

ROMs, saves, emulator states, user screenshots, chat/session history, personal paths, credentials and local AI configurations are excluded from this export. Generated original text and build reports stay private.

**Project-authored tooling and technical documentation are MIT-licensed**, with third-party and game-derived material excluded from that grant. Fonts remain OFL-1.1 with their original notices. Localization data is experimental and is not a blanket MIT/CC license for the underlying game or English project. This is a noncommercial knowledge-sharing project; that purpose does not restrict the MIT-covered tooling or grant permission to redistribute ROMs. Read [license scope](LICENSE_STATUS.md) and [credits](CREDITS.md).

Current experimental display version: **v1.0**. Title background: bottom-right “云之君个人汉化”, bottom-left “v1.0”. Development is on hold pending player feedback; full single-player acceptance remains incomplete. These labels are hardcoded in `src/stage5/title_branding_assets.py` and should be adapted by other language projects.
