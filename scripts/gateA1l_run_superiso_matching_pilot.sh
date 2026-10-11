#!/usr/bin/env bash
# Gate A1L: external SuperIso Wilson matching pilot. No modifications to vendor.
# Produces matching coefficients, NOT a physical Zee branching ratio.
set -Eeuo pipefail
if (( $# < 1 || $# > 2 )); then
  echo "Usage: bash $0 /path/to/SuperIso_v5.0 [output_directory]" >&2
  exit 2
fi
vendor=$(realpath "$1")
out=$(realpath -m "${2:-work/gateA1l_superiso_pilot}")
[[ -f "$vendor/src/libsuperiso.a" && -f "$vendor/src/include.h" &&
   -f "$vendor/src/wilson.c" ]] || {
    echo "Expected built official SuperIso source + libsuperiso.a" >&2
    exit 2
}
for cmd in gcc python3 sha256sum; do
  command -v "$cmd" >/dev/null || { echo "Missing $cmd" >&2; exit 2; }
done
mkdir -p "$out"
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
python3 "$script_dir/gateA1l_superiso_nlo_audit.py" \
  --superiso-dir "$vendor" --output "$out/vendor_nlo_audit.json"

gcc -std=gnu11 -O2 -Wall -Wextra \
  -I"$vendor/src" "$script_dir/gateA1l_zee_superiso_matching_pilot.c" \
  "$vendor/src/libsuperiso.a" -lm -o "$out/zee_superiso_matching_pilot"

# With identical SM inputs and matching scale, verify Type-II one-state
# limits and the interpolating benchmark at the matching coefficient level.
(cd "$vendor" && "$out/zee_superiso_matching_pilot" 300 700 0.0 1.394) \
  > "$out/gamma0.txt"
(cd "$vendor" && "$out/zee_superiso_matching_pilot" 300 700 1.5707963267948966 1.394) \
  > "$out/gamma90.txt"
(cd "$vendor" && "$out/zee_superiso_matching_pilot" 300 700 1.089 1.394) \
  > "$out/benchmark.txt"

python3 "$script_dir/gateA1l_check_matching_pilot.py" \
  --gamma0 "$out/gamma0.txt" \
  --gamma90 "$out/gamma90.txt" \
  --benchmark "$out/benchmark.txt" \
  --audit "$out/vendor_nlo_audit.json" \
  --output "$out/result.json"

sha256sum "$vendor/src/libsuperiso.a" "$out/zee_superiso_matching_pilot" \
  > "$out/build_sha256.txt"
echo "Source untouched. Results in: $out"
