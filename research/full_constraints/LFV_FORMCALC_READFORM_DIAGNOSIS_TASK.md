# FormCalc ReadForm/WSTP diagnosis — narrowly bounded LFV unblock

**Starting branch HEAD** `7977236e8b5cbdd1f977025beeda71fc472d6328`.
**Priority:** solve a binary/kernel connection failure, **not** derive any Zee amplitude.
**Stop:** once `Needs["FormCalc\`"]` loads in the same Mathematica kernel as SARAH 4.15.4 and FeynArts 3.12, perform only the predeclared single FlexibleSUSY configure/model-adapter attempt from `LFV_PRACTICAL_APPROXIMATION_TASK.md`. If not repaired after the bounded diagnostics, report a reproducible concrete upstream issue and stop.

## Exact known environment and error

See `LFV_PRACTICAL_IMPLEMENTATION_REPORT.md`.
Scratch `/tmp/zee-lfv-practical-20261107`. Mathematica `/usr/local/bin/math` (15.0.1). SARAH 4.15.4 loads. Official FeynArts 3.12 archive hash `190cb5a2ecbbe35136f218d462b03731c6b797ecf65f088affc89ea01ef5784a`, loads successfully. Official FormCalc 9.10 archive hash `352bff193be4472ce38bb266fcccb653c3dee21c49c6df6c5b784ff8ad53029b`, tar integrity and `./compile` exit zero; `Needs["FormCalc\`"]` prints banner then `LinkOpen::linke: Unknown MathLink problem encountered` and `ReadForm::notcompiled`. Standalone binary behavior NOT YET reported.

Official authoritative documentation:
- https://feynarts.de/formcalc/trouble.html: invoke `./Linux/ReadForm` **standalone** (current system directory may instead be `Linux-x86-64`) and look for `Create Link:`; a crash indicates binary/runtime MathLink SDK incompatibility.
- https://feynarts.de/formcalc/: compiling C helper programs with `./compile` is required.
- https://github.com/FlexibleSUSY/FlexibleSUSY/blob/master/README.rst: FeynArts >=3.10 and FormCalc >=9.8 must independently `Needs[]` successfully within Mathematica.

## Phase 1: exact reproducible OS-level cause before any intervention

1. Work exclusively in the **existing isolated scratch installation**, not a new download. Do not make destructive changes outside scratch or edit system libraries.
2. Locate FormCalc root by searching under scratch for `FormCalc.m`, `ReadForm.tm`, `compile`, then locate **actual** system-specific `ReadForm` binary. Capture full resolved paths and `find ... -name ReadForm` results. Do not assume the command was compiled to the platform loaded by Mathematica.
3. Record `uname -a`, `uname -m`, `file <ReadForm>`, `ls -l`, `ldd <ReadForm>` (if applicable; static is okay), `readelf -l/-d`, `command -v mcc`, `mcc -help` or `mcc -version` if actually supported, `which math`, and `$SystemID` / `$InstallationDirectory` from fresh Mathematica. Capture full `./compile` stdout/stderr and build commands in stdout; a zero shell exit is insufficient.
4. Execute `printf '\\n\\n' | timeout 5s '<full path>/ReadForm'` and preserve **stdout, stderr and exit status**. Passing behavior is a `Create Link:` prompt (terminal standalone WSTP); `ldd` library resolution, no-execute / ELF interpreter, segmentation fault and stderr signal are separate diagnoses.
5. If binary fails: use the exact compiler and SDK paths printed in the build and compare against the running Mathematica installation; avoid linking against a stale archived `mcc` / `libML` / `libWSTP`. Investigate `LD_LIBRARY_PATH` and actual transitive lib resolution, and `strace -f -e trace=execve,openat` *only if installed and relevant*. Attempt **one** source-backed scratch-only rebuild with the *correct* Wolfram 15 SDK/compiler and consistently matching 64-bit architecture. Do not blindly add unsupported linker flags, static libs, or unverified symlinks.
6. If standalone `ReadForm` passes but Mathematica link fails: run a clean Mathematica session with only SARAH/FeynArts/FormCalc original package paths appended; audit `FindFile["FormCalc\`"]`, `$SystemID`, `$Path`, `Directory[]`, `$MessageList`; whether `FormCalc` points to a different older installation, and any auto-selected `ReadForm` path. Try **one** absolute-path `Install[<ReadForm>]` in a separate fresh kernel (record output, then `Uninstall` if connected); a working manually launched link but failing `Needs` suggests wrong path/platform/initialization. Confirm no unpatched FeynArts vs patched FeynCalc package mix in the same kernel. Do not suppress `LinkOpen::linke`.
7. **Success** = reproducible `Needs["FormCalc\`"]` with `ReadForm` connection, in same fresh Mathematica process with SARAH and FeynArts; capture versions and a trivial public FormCalc benchmark where possible. Then proceed with *only* initial FlexibleSUSY configure to reach `BrLTo3L` / `LToLConversion` generator stage per existing limited task. Never claim successful LFV physics based on dependency load.

## Phase 2: decision, outputs and stop

Create or append report `research/full_constraints/LFV_FORMCALC_READFORM_DIAGNOSIS.md` with:
- literal stderr/stdout/exit codes, `file`/library traces and compiled platform, path/config mismatch/root cause (or unresolved hypotheses), upstream doc, exact fix attempted, manual CLI link test, `Needs` result, and target FlexibleSUSY configure result if reached;
- sandbox source and compiled binary hashes (not commit third-party binaries);
- no new model cards, parameter scan, theoretical BR or physical PASS/FAIL without genuinely calculated validation.

Update `LFV_PRACTICAL_IMPLEMENTATION_REPORT.md` with truthful new state and link. If repaired and the generator can run, revert to existing task `LFV_PRACTICAL_APPROXIMATION_TASK.md` for **four saved cards only**. If broken after exact bounded diagnostics, STOP and provide minimal upstream issue reproducer for Thomas Hahn/FormCalc or Wolfram with architecture, Mathematica 15, `mcc` path, ELF/interpreter and clean link test. No repeated installation loops. All frozen source and `global_acceptance=null` remain unchanged. Commit/push research-only diagnostics.
