# Source-preparation verification

The source export was independently built from checked local Japanese and EnglishV1.0.1 inputs. Source Japanese messages were regenerated using ROM glyph/control tables and content identities; native/off-bank source records were regenerated locally as well.

The output matched the current reference build byte-for-byte:

- Size:16777216 bytes
- SHA-1:`4816ac49f58e5e3648e018b976de3ed50451b30c`
- SHA-256:`d1bc109a6bd81b8e99f427ac11d3456c1cc143f90379a843eb6dcc09ed1813c9`
- CRC32:`6066ed98`
- BPS reconstruction:byte-identical

Current counts:6394 unique script drafts,12309 occurrences,1181 native records,234 off-bank records,1952 subset characters,2992 ROM presentation entries and1316 native-engine bytes.

The prepared source bundle contains no ROM/save/state files, user screenshots, private configuration or user absolute paths. Full source catalogs are generated locally and excluded. Third-party original license/author notices are intentionally retained.

This verifies reproducibility and export preparation. It does not establish whole-game completion, semantic perfection, every UI's appearance or public distribution permission. Those statuses are explicitly documented in the README and license status.
