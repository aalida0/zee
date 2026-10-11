#!/usr/bin/env bash
# Gate A1M: unmodified-vs-isolated SuperIso v5 NLO matching diagnostic.
# Does NOT compute a physical B->Xs gamma BR. Never alters vendor source.
set -Eeuo pipefail
if (( $# < 1 || $# > 2 )); then
  echo "Usage: bash $0 /path/to/SuperIso_v5.0 [output_dir]" >&2
  exit 2
fi
vendor=$(realpath "$1")
out=$(realpath -m "${2:-work/gateA1m_isolated_nlo}")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[[ -f "$vendor/src/libsuperiso.a" && -f "$vendor/src/wilson.c" ]] || {
  echo "Built official SuperIso v5 library and source are required" >&2; exit 2;
}
if [[ -e "$out/isolated_superiso" ]]; then
  echo "Refusing to reuse existing isolated patch tree: $out/isolated_superiso" >&2
  echo "Choose a fresh output directory; this avoids stale objects/source." >&2
  exit 2
fi
case "$out/" in "$vendor/"*) echo "Output must be outside official vendor tree" >&2; exit 2;; esac
mkdir -p "$out"
src_original_sha=$(sha256sum "$vendor/src/wilson.c" | awk '{print $1}')
src_original_lib_sha=$(sha256sum "$vendor/src/libsuperiso.a" | awk '{print $1}')
python3 "$script_dir/gateA1m_prepare_isolated_superiso.py" \
  --vendor-dir "$vendor" --isolated-dir "$out/isolated_superiso" \
  --output "$out/source_patch_provenance.json"

patched="$out/isolated_superiso"
( cd "$patched" && make clean ) > "$out/patched_make_clean.log" 2>&1
( cd "$patched" && make -j1 ) > "$out/patched_make_library.log" 2>&1
[[ -f "$patched/src/libsuperiso.a" ]] || {
  echo "Patched SuperIso library missing; see make logs" >&2; exit 1;
}
gcc -std=gnu11 -O2 -Wall -Wextra \
  -I"$vendor/src" "$script_dir/gateA1l_zee_superiso_matching_pilot.c" \
  "$vendor/src/libsuperiso.a" -lm -o "$out/matching_native"
gcc -std=gnu11 -O2 -Wall -Wextra \
  -I"$patched/src" "$script_dir/gateA1l_zee_superiso_matching_pilot.c" \
  "$patched/src/libsuperiso.a" -lm -o "$out/matching_patched"

for variant in native patched; do
  exe="$out/matching_$variant"
  vroot="$vendor"
  if [[ "$variant" == "patched" ]]; then vroot="$patched"; fi
  (cd "$vroot" && "$exe" 300 700 1.089 1.394) \
    > "$out/$variant.txt"
  (cd "$vroot" && "$exe" 300 700 0.0 1.394) \
    > "$out/${variant}_gamma0.txt"
  (cd "$vroot" && "$exe" 300 700 1.5707963267948966 1.394) \
    > "$out/${variant}_gamma90.txt"
done

python3 "$script_dir/gateA1l_superiso_nlo_audit.py" \
  --superiso-dir "$vendor" --output "$out/native_nlo_audit.json"
python3 "$script_dir/gateA1l_check_matching_pilot.py" \
  --gamma0 "$out/native_gamma0.txt" \
  --gamma90 "$out/native_gamma90.txt" \
  --benchmark "$out/native.txt" \
  --audit "$out/native_nlo_audit.json" \
  --output "$out/native_closure.json"
# Patched native bug predicate is intentionally false; manually evaluate
# endpoint closure with matching identities in A1M comparison.
python3 "$script_dir/gateA1m_compare_matching.py" \
  --native "$out/native.txt" --patched "$out/patched.txt" \
  --provenance "$out/source_patch_provenance.json" \
  --output "$out/result.json"

src_after_sha=$(sha256sum "$vendor/src/wilson.c" | awk '{print $1}')
src_after_lib_sha=$(sha256sum "$vendor/src/libsuperiso.a" | awk '{print $1}')
[[ "$src_original_sha" == "$src_after_sha" ]] || {
  echo "ERROR: Original vendor source hash changed" >&2; exit 1;
}
[[ "$src_original_lib_sha" == "$src_after_lib_sha" ]] || {
  echo "ERROR: Original vendor library hash changed" >&2; exit 1;
}
{
 sha256sum "$vendor/src/wilson.c"
 sha256sum "$vendor/src/libsuperiso.a"
 sha256sum "$patched/src/wilson.c"
 sha256sum "$patched/src/libsuperiso.a"
} > "$out/source_library_sha256.txt"
echo "STATUS ISOLATED_NLO_MATCHING_DIAGNOSTIC_RUN_NOT_A_PHYSICAL_BR"
echo "Original vendor source and binary hashes unchanged."
echo "See $out/result.json and $out/source_patch_provenance.json"
