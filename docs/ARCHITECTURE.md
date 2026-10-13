# Architecture and memory map

The build takes the checked EnglishV1.0.1 base, restores Japanese script/control-flow bytes at their original addresses, redirects exact extracted message addresses to translated bodies, installs display-only native lookup/guarded copy hooks, compiles selected graphic captions, and emits a target ROM plus BPS.

| Region / entry | Role |
|---|---|
| `0x4B5FA0..0x5371D8` | Original Japanese script bytes preserved |
| `0x800000`, `0x840000` | Primary / compact glyph storage |
| `0x880000`, `0x884000` | Primary / compact encoding tables |
| `0x88F000`, `0x88F002` | Separate glyph counts |
| `0x8A0000` | Exact script message redirect table |
| `0x8C0000` | Native ROM presentation lookup |
| `0x8E0000..0x8F0000` | Audited tournament RAM aliases |
| `0x8F0000..0x8F1000` | NPC name aliases |
| `0x8F1000..0x8F2000` | Retry, COM and inventory copy rules |
| `0x900000`, `0x901000` | Script / native Thumb engines |
| `0x940000..0xB00000` | Translated script bodies |
| `0xB00000..0xB20000` | Native text payloads |
| `0xB30000..0xB36000` | Equipment label graphic pools/maps |
| `0xB40000..0xB80000` | Main menu / venue title graphic pools |
| `0xB80000..0xBE0000` | League/result/title/HUD-related replacements |
| `0xBE0000..0xBF0000` | Rookie venue header |
| `0xBF0000..0xC00000` | Map SHOP sign replacement |

Check each compiler's allocation assertions before adding resources. Some images are replaced in place, while others use new pointer/offset slots. Relative image offsets may be negative and require32-bit wraparound.

The whole-glyph native hook guards exact extended font tables, glyph range and left-half parity. It preflights two half-cells before drawing the left half and preserves existing behavior for ordinary glyphs/icons. The original script renderer already has a logical-character preflight.

The commander-name width is a background-tile allocation, not a6px character count:7 tiles ×8px =56px. Player-name validation remains independent. This distinction caused the prior UI overlap and is a useful example of separating field geometry from text metrics.
