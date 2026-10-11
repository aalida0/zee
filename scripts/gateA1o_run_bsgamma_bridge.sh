#!/usr/bin/env bash
# Gate A1O: run isolated internal rematching correction.
# NO modifications to original vendor or Gate A1M source.
# No physics exclusion or allowed point claim.
set -Eeuo pipefail
if (( $# < 1 || $# > 2 )); then
  echo "Usage: bash $0 A1M_ISOLATED_DIR [OUTPUT_DIR]" >&2
  exit 2
fi
a1m=$(realpath "$1")
out=$(realpath -m "${2:-work/gateA1o_bsgamma_bridge}")
scripts=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[[ -f "$a1m/src/libsuperiso.a" && -f "$a1m/src/wilson.c" &&
   -f "$a1m/src/bsgamma.c" ]] || {
    echo "Expected complete compiled A1M isolated SuperIso" >&2; exit 2;
}
provenance=$(dirname "$a1m")/source_patch_provenance.json
[[ -f "$provenance" ]] || { echo "A1M provenance missing" >&2; exit 2; }
if [[ -e "$out/A1O_isolated_superiso" ]]; then
  echo "Refusing to reuse an existing A1O source tree; choose fresh output directory" >&2
  exit 2
fi
case "$out/" in "$a1m/"*) echo "Do not build A1O inside A1M tree" >&2;exit 2;; esac
mkdir -p "$out"
sha_wilson_before=$(sha256sum "$a1m/src/wilson.c" | awk '{print $1}')
sha_bsgamma_before=$(sha256sum "$a1m/src/bsgamma.c" | awk '{print $1}')
sha_library_before=$(sha256sum "$a1m/src/libsuperiso.a" | awk '{print $1}')

python3 "$scripts/gateA1o_prepare_bsgamma_bridge.py" \
  --a1m-source "$a1m" \
  --a1m-provenance "$provenance" \
  --isolated-output "$out/A1O_isolated_superiso" \
  --report "$out/source_bridge_provenance.json"

bridge="$out/A1O_isolated_superiso"
# Empty all preexisting objects from copied source, forcing a clean rebuilt
# archive with the guarded bsgamma extension.
(cd "$bridge" && make clean) > "$out/build_clean.log" 2>&1 || {
  echo "make clean failed; inspect $out/build_clean.log" >&2;exit 1;
}
(cd "$bridge" && make -j1) > "$out/build_serial.log" 2>&1 || {
  echo "Serial isolated build failed; see $out/build_serial.log" >&2;exit 1;
}
[[ -f "$bridge/src/libsuperiso.a" ]] || {
  echo "A1O isolated compiled archive missing" >&2; exit 1;
}

# Use same A1N prototype and physics inputs for A1M control and A1O.
gcc -std=gnu11 -O2 -Wall -Wextra -I"$a1m/src" \
  "$scripts/gateA1n_superiso_br_candidate.c" \
  "$a1m/src/libsuperiso.a" -lm -o "$out/br_a1m"
gcc -std=gnu11 -O2 -Wall -Wextra -DGATE_A1O_MATCHED_C0W \
  -I"$bridge/src" \
  "$scripts/gateA1n_superiso_br_candidate.c" \
  "$bridge/src/libsuperiso.a" -lm -o "$out/br_a1o"
(cd "$a1m" && "$out/br_a1m") > "$out/a1m.txt"
(cd "$bridge" && "$out/br_a1o") > "$out/a1o.txt"

ref_sm=work/gateA1j_superiso_build/sm_output.log
[[ -f "$ref_sm" ]] || {
  echo "Official A1J SM reference file missing at $ref_sm" >&2;exit 2;
}
python3 "$scripts/gateA1o_check_internal_matching_bridge.py" \
  --a1m "$out/a1m.txt" \
  --a1o "$out/a1o.txt" \
  --official-sm "$ref_sm" \
  --output "$out/result.json"

[[ "$sha_wilson_before" == "$(sha256sum "$a1m/src/wilson.c" | awk '{print $1}')" &&
   "$sha_bsgamma_before" == "$(sha256sum "$a1m/src/bsgamma.c" | awk '{print $1}')" &&
   "$sha_library_before" == "$(sha256sum "$a1m/src/libsuperiso.a" | awk '{print $1}')" ]] || {
   echo "A1M source/library unexpectedly changed; blocked" >&2; exit 1;
}
{
  sha256sum "$a1m/src/wilson.c" "$a1m/src/bsgamma.c" "$a1m/src/libsuperiso.a"
  sha256sum "$bridge/src/wilson.c" "$bridge/src/bsgamma.c" "$bridge/src/libsuperiso.a"
} > "$out/source_library_sha256.txt"

echo "STATUS GATE_A1O_BRIDGE_CONSISTENCY_PILOT_NOT_PHYSICAL_EXCLUSION"
echo "Diagnostics: $out/result.json"
