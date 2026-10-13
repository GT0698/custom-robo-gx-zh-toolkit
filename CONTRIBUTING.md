# Contributing

Read LICENSE_STATUS.md for component boundaries. Contributions of independently authored tooling and documentation are under MIT. Do not submit game assets or third-party material without identifying their separate permission scope.

1. Create a target-language pack. Keep the source IDs, offsets, control tokens, resource keys and password input keys stable.
2. Export Japanese/English catalogs from your own local inputs. For script dialogue, equal ROM addresses do not establish English/Japanese correspondence; the exporter intentionally leaves the English script reference blank.
3. Edit only target values. Preserve color/icon controls; only explicitly reviewed newline policies may change layout controls.
4. Check font coverage, fixed buffer capacity, field dimensions and graphical captions. A successful build is not full language or gameplay QA.
5. Run `python3 tests/run.py` and `python3 scripts/verify_public.py`. Rebuild locally; compare hashes when validating the unmodified reference snapshot.
6. For shared render changes, use representative bounded probes. Reuse unaffected evidence; do not replace test ROM hashes with a current hash unless the check was rerun.
7. Submit a focused change with language, affected UI/mechanism, source reasoning, validation and remaining limitations.

Public contributions must exclude ROMs, saves, emulator states, user/private screenshots, full source catalogs, personal information and credentials. Build artifacts belong in `.build/`. No messages to upstream authors or public releases are triggered by these tools.
