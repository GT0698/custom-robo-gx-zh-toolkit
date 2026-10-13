# Testing without a gameplay automation loop

## Pure/CI checks

`python3 tests/run.py` runs BPS reconstruction/corruption/bounds cases and ROM-input decoder fixtures on synthetic data. It also scans public files. These tests need no game ROM and do not boot an emulator.

`python3 scripts/verify_public.py` rejects personal paths/config markers, binary/private artifact types, source corpus fields in public target tables and symlinks. It also rejects ignored private artifacts if forcibly tracked in Git. The source archive uses an explicit path/type allowlist.

## Local reference build

Run build.py with `--verify-reference` and checked local inputs. The unmodified source snapshot must produce the exact target digest in reference-build.json. The packager creates a BPS and applies it back to the English input, checking byte identity.

## Optional bounded CPU probes

Build/install a matching mGBA0.10 library and development headers yourself; no mGBA dependency is bundled. Then:

```sh
python3 scripts/build_runtime.py \
  --include /path/to/mgba/include \
  --include /path/to/mgba-build/include \
  --library-dir /path/to/mgba-build
python3 scripts/runtime_check.py \
  --library .build/runtime/emulator_probe.dylib \
  --rom .build/artifacts/custom-robo-gx-zh.gba \
  --output .build/runtime/check.json
```

On Linux the default library suffix is`.so`. The adapter compilation command is generated for the host; runtime probe compilation has been tested locally on macOS against the existing mGBA0.10 dependency.

The representative check sets only synthetic font/context buffers, invokes the actual DrawChar/newline code, records logical placement before pixel drawing and checks the pair stays on one row. It does not import a save, drive buttons or run the game loop.

Between mGBA steps, a Thumb callee entry is observed at entry+2. Intercept before its push; entry+4 can skip cleanup after a push and unbalance the stack. The adapter verifies the returned stack pointer. This is a harness requirement, not a game patch.

## Evidence discipline

- Record the actual tested ROM hash.
- State whether evidence is static, a function probe, a fixture, an offline image preview or normal user feedback.
- Test shared font/render changes by affected mechanism; do not review every same-mechanism line through model/gameplay loops.
- Keep source identity, values, source/destination guards and buffer limits under checks.
- A compile pass, complete extracted-script draft or isolated lookup test does not establish full single-player or postgame acceptance.
