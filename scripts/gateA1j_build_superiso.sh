#!/usr/bin/env bash
# Gate A1J: build and smoke-test an already downloaded/extracted official SuperIso source tree.
# No sudo; no auto-download; no source modification. Not a Zee B->Xs gamma prediction.
set -Eeuo pipefail

usage() {
  cat <<'HELP'
Usage: bash scripts/gateA1j_build_superiso.sh SOURCE_DIR [OUTPUT_DIR] [JOBS]
  SOURCE_DIR: directory containing an official SuperIso Makefile and src/
  OUTPUT_DIR: provenance and logs directory (default: work/gateA1j_superiso_build)
  JOBS: must be 1 (default 1): SuperIso v5 archive recipe is NOT parallel-safe

Builds the library sequentially via make -j1, then sm.x via make sm; runs the SM executable.
IMPORTANT: SuperIso v5 src/Makefile invokes multiple ar rcsU writes to
libsuperiso.a and deletes .o files, so parallel make can break the archive.
After a failed parallel build, run make clean before invoking this script.
Attempts 'make scan_coeffs' and 'make predict' separately. Their failure
is recorded but does not invalidate a successful core+SM build.
Does not build thdm.x: legacy 2HDM path may require 2HDMC.
HELP
}
if [[ ${1:-} == '-h' || ${1:-} == '--help' ]]; then usage; exit 0; fi
if (( $# < 1 || $# > 3 )); then usage >&2; exit 2; fi
src=$(realpath "$1")
out=$(realpath -m "${2:-work/gateA1j_superiso_build}")
jobs=${3:-1}
[[ "$jobs" == "1" ]] || {
  echo "SuperIso v5 uses concurrent ar rcsU writes to a shared archive; JOBS must be 1." >&2; exit 2;
}
[[ -d "$src/src" && -f "$src/Makefile" ]] || {
  echo "Source must contain Makefile and src/: $src" >&2; exit 2;
}
for cmd in make gcc ar sha256sum python3; do
  command -v "$cmd" >/dev/null || { echo "Missing required command: $cmd" >&2; exit 2; }
done
mkdir -p "$out"
# Ensure logs and provenance do not modify the vendor source tree.
case "$out/" in "$src/"*) echo "OUTPUT_DIR cannot be within vendor source tree" >&2; exit 2;; esac
printf 'SOURCE_DIR=%s\nOUTPUT_DIR=%s\nJOBS=%s\n' "$src" "$out" "$jobs" | tee "$out/settings.txt"
( cd "$src" && { gcc --version | head -n1; make --version | head -n1; } ) > "$out/toolchain.txt"
( cd "$src" && find . -maxdepth 2 -type f \( -name '*.c' -o -name '*.h' -o -name 'Makefile' -o -name 'README*' \) -print0 | sort -z | xargs -0 -r sha256sum ) > "$out/source_sha256.txt"

if ( cd "$src" && make -j1 ) > "$out/make_library.log" 2>&1; then
  lib_status=PASS
else
  lib_status=FAIL
fi
if [[ "$lib_status" == PASS ]] && ( cd "$src" && make sm ) > "$out/make_sm.log" 2>&1; then
  sm_build_status=PASS
else
  sm_build_status=FAIL
  if [[ "$lib_status" != PASS ]]; then
    echo 'Skipped: library build failed' > "$out/make_sm.log"
  fi
fi
if [[ "$sm_build_status" == PASS && -x "$src/sm.x" ]] && (cd "$src" && ./sm.x) > "$out/sm_output.log" 2>&1; then
  sm_run_status=PASS
else
  sm_run_status=FAIL
  if [[ ! -f "$out/sm_output.log" ]]; then
    echo 'Skipped: sm.x not built or not executable' > "$out/sm_output.log"
  fi
fi

for program in scan_coeffs predict; do
  if [[ "$lib_status" == PASS ]] && ( cd "$src" && make "$program" ) > "$out/make_${program}.log" 2>&1; then
    printf 'PASS\n' > "$out/${program}.status"
  else
    printf 'UNAVAILABLE_OR_FAILED\n' > "$out/${program}.status"
    if [[ "$lib_status" != PASS ]]; then echo 'Skipped: library build failed' > "$out/make_${program}.log"; fi
  fi
done

python3 - "$src" "$out" "$lib_status" "$sm_build_status" "$sm_run_status" <<'PY'
import hashlib, json, pathlib, sys
src, out = map(pathlib.Path, sys.argv[1:3]); lib, bld, run = sys.argv[3:]
manifest = out/'source_sha256.txt'
r = {
 'status': ('SUPERISO_SM_BASELINE_BUILT_AND_RUN' if lib==bld==run=='PASS'
            else 'SUPERISO_INSTALL_BUILD_OR_SM_SMOKE_FAILED'),
 'scope':'Toolchain/source provenance and SuperIso SM smoke only; NOT two-Higgs Zee b->s gamma',
 'source_dir':str(src), 'logs_dir':str(out),
 'library_build':lib, 'sm_build':bld,'sm_run':run,
 'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
 'source_manifest_entries':len(manifest.read_text().splitlines()),
 'optional_targets':{t:(out/(t+'.status')).read_text().strip() for t in ('scan_coeffs','predict')},
 'executables':{x:(src/(x+'.x')).is_file() for x in ('sm','thdm','scan_coeffs','predict')},
 'confirmed_Zee_two_charged_NLO_NNLO_matching':False,
 'physical_BR_B_to_Xs_gamma_calculated':False,
 'next':'Review source matching functions and validate SM+Type-II controls; then implement both charged states at amplitude level.'}
(out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
PY

echo "SM output log: $out/sm_output.log"
echo "Source fingerprint: $out/source_sha256.txt"
echo 'No Zee physical BR or exclusion calculated.'
[[ "$lib_status" == PASS && "$sm_build_status" == PASS && "$sm_run_status" == PASS ]]
