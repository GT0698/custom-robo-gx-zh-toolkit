# Proposed license split — not yet adopted

Historical research reviewed 2026-10-14. The maintainer subsequently authorized publication with MIT for project-authored tools/docs only; see ../LICENSE_STATUS.md for current scope. CC BY for translations was not adopted. No upstream contact was made by these tools. The sections below retain the researched proposal, not operative license grants.

## Verified English-base terms

Pinned upstream commit: `68a7e2c376c021b5feb3e13be21f30776b2c5344`; GitHub API license field is null. This is not proof of no permission: the [README](https://github.com/Ganenis/Custom-Robo-GX-English/blob/68a7e2c376c021b5feb3e13be21f30776b2c5344/README.txt) explicitly permits free patch distribution, states personal use/not for sale, and prohibits original and pre-patched ROM distribution. It does not explicitly grant modification, derivative-patch publication, source-code reuse or sublicensing under MIT.

The recommended boundary is to require users to obtain that English patch themselves. Do not relicense or copy upstream material merely because it is publicly readable. An English→Chinese incremental BPS reduces bundled upstream material but does not itself establish derivative authorization. Ganenis can clarify rights in Ganenis's contribution; that cannot grant Nintendo/NOISE rights in the underlying game. Do not treat attribution as authorization.

## Verified font terms

The bundled 12px monospaced BDF and four notice files are byte-identical to the original 2026.09.25 release archive. Its SHA-256 matches the official GitHub release asset digest: `d75f5262f108757edb0f47ee8e3d2dfdfbecfd94558faf5ffb0c06dc5866fb3b`.

[Fusion Pixel release](https://github.com/TakWolf/fusion-pixel-font/releases/tag/2026.09.25); [current font/code license split](https://github.com/TakWolf/fusion-pixel-font/blob/d4043e9154273a7f407b50be3f6a1e15c6e4e2c7/README.md).

Font software is OFL-1.1; upstream font-build code is MIT. The latter does not make the BDF MIT. Preserve the bundled OFL and Ark Pixel, Cubic11 and Galmuri notices exactly. Cubic11's file includes legacy permissive and OFL statements; do not replace it with a synthesized uniform notice. No specific Reserved Font Name declaration was found in the headers of the bundled notices; template wording about reserved names is not a declaration. Recheck replacement fonts before naming modified versions.

OFL permits use, modification, subsetting, embedding and redistribution, including bundling with commercial software. The font cannot be sold by itself; redistributed font software and modified/subset glyph tables retain OFL and notices. This does not force our independent tooling to use OFL. Text images rendered with the font are artwork, not automatically OFL font software; original game graphics still have their own rights. Treat converted ROM glyph tables as derived font software and retain font notices with distributed patches.

Primary text: https://openfontlicense.org/open-font-license-official-text/
FAQ: https://openfontlicense.org/ofl-faq/ (1.1.1, 1.3, 1.20, 1.21).

## Recommended scopes

| Material | Proposed license / handling |
|---|---|
| Independently authored Python/C/ASM tools, pure tests and factual interoperability policies | MIT after file-level provenance review; retain third-party licenses on any copied portions |
| Original README, methods and engineering documentation | MIT, same as the tools, excluding quoted/external material |
| Chinese target text and original terminology contributions | Candidate CC BY 4.0 for rights the contributor actually controls, only after derivative/ownership review; underlying game or English text is not relicensed |
| Bundled BDF and generated font subsets | Existing OFL-1.1 plus constituent notices; not MIT |
| English patch and original game/graphics | Excluded inputs; no project license grant; derivative patch clearance remains unresolved |
| Optional mGBA | External MPL-2.0 dependency; no bundled library/source. Audit adapter provenance before MIT designation |

MIT supports the intended reuse in other localization projects with attribution/license preservation, without requiring their tools to use the same license. CC BY 4.0 supports translation-text adaptation and attribution, but permits commercial reuse of rights actually licensed. Neither grants permission to sell the English patch/game. Do not add a noncommercial restriction to MIT and still call it standard MIT/open source. Do not apply CC to executable source code as a substitute for a software license.

MIT: https://opensource.org/license/mit
CC BY 4.0: https://creativecommons.org/licenses/by/4.0/

## Remaining release actions

1. Maintainer approves license selection and a public attribution label (project name or pseudonym; legal name/email not required by this proposed packaging).
2. Review code and bitmap provenance file by file: copied prologues/instructions, reference disassembly snippets and original ROM glyphs are not automatically independently authored. Generic factual offsets/policies and independent implementation must be distinguished from expressive copied material. Current source privacy checks do not perform this review.
3. Clarify Ganenis's permission for another-language derivative patch and any identifiable retained English-project material. Prepare a request if desired, but do not send without authorization. Separately assess game-derived translation/assets; an author reply does not clear Nintendo/NOISE rights.
4. Complete source/translation scope mapping before activating licenses. If text permissions remain unresolved, a reusable independently authored tools/docs + OFL font release can omit the game-derived translation/assets, but it will no longer be the full reproducible Chinese package.
5. Once approved, add standard license texts with explicit scope, per-file SPDX identifiers where appropriate, retained notices and source/patch release notes. Draft MIT remains inactive until that decision. Do not assert the whole ROM/BPS is MIT or the package is fully rights-cleared.

Suggested post-approval README summary: “Project-authored tooling and documentation: MIT. Identified original target-language contributions: CC BY 4.0, only to the extent licensed rights are held. Fonts: OFL-1.1 with constituent notices. Original game and English base are excluded and not relicensed.” This wording is a proposal, not an operative license.
