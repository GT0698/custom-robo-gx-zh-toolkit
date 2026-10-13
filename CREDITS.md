# Credits and provenance

## English base — Ganenis

This Simplified Chinese project is based on **Ganenis/Custom-Robo-GX-English, Full EnglishV1.0.1**:

- Project: https://github.com/Ganenis/Custom-Robo-GX-English
- README snapshot inspected: https://github.com/Ganenis/Custom-Robo-GX-English/blob/68a7e2c376c021b5feb3e13be21f30776b2c5344/README.txt
- README Git blob: `9d3e55c9430f87bba9ede85e2dd97d35e2fb346a`
- English input SHA-1: `e033251c780dbbd83b15623159b743d2e624d8a0`

The English patch provides the base engine/localization changes used by this project. Chinese translation uses Japanese as the source reference. This source archive does not redistribute the English BPS or an English ROM.

## Original game

The original game is Custom Robo GX. The upstream README attributes the original game copyrights to Nintendo and NOISE. Game ROMs and original graphic assets are supplied locally by users and are not included as files in this export. Translation data and game-specific interoperability details are identified separately from project-authored tooling.

## Font — Fusion Pixel and its sources

- Fusion Pixel Font: https://github.com/TakWolf/fusion-pixel-font
- Bundled BDF: Fusion Pixel12px monospaced Simplified Chinese, version2026.09.25.
- Font SHA-256: see `reference-build.json`.
- Original notices: `third_party/fusion_pixel/OFL.txt` and `third_party/fusion_pixel/LICENSES/`, including Ark Pixel, Cubic11 and Galmuri notices.

Original copyright/author notices in those files are retained. They are third-party attribution, not user personal information.

## Reverse-engineering reference

The development process consulted the public robogx disassembly/decompilation project and its source comments: https://github.com/pizdex/robogx . That disassembly and its complete original script/source dump are not redistributed here. The portable input decoder reconstructs required text directly from local ROM tables.

## Optional verification dependency

mGBA is an optional external dependency for bounded CPU probes. Its locally inspected source license is MPL2.0. No mGBA source, compiled library or emulator state is bundled. The probe adapter is supplied as project tooling.
