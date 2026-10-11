#!/usr/bin/env bash
# Gate A1N: candidate BR(B->Xs gamma), controlled native/isolated SuperIso v5.
# Does NOT establish a Zee benchmark exclusion/viability.
set -Eeuo pipefail
if (( $# < 2 || $# > 3 )); then
  echo "Usage: bash $0 OFFICIAL_SUPERISO_DIR A1M_ISOLATED_DIR [OUTPUT_DIR]" >&2
  exit 2
fi
vendor=$(realpath "$1")
patched=$(realpath "$2")
out=$(realpath -m "${3:-work/gateA1n_br_candidate}")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[[ "$vendor" != "$patched" ]] || {
  echo "Native and isolated SuperIso roots must be distinct" >&2;exit 2;
}
case "$out/" in "$vendor/"*|"$patched/"*)
  echo "Output directory must be outside vendor and isolated sources" >&2;exit 2;; esac
for root in "$vendor" "$patched"; do
  [[ -f "$root/src/libsuperiso.a" && -f "$root/src/include.h" &&
     -f "$root/src/wilson.c" ]] || {
    echo "Missing built SuperIso vendor or isolated library in $root" >&2;exit 2;
  }
done
# Provenance must match the exact A1M isolated build; never use an
# arbitrary third-party or externally patched source tree.
provenance=$(dirname "$patched")/source_patch_provenance.json
[[ -f "$provenance" ]] || {
  echo "Gate A1M source_patch_provenance.json missing" >&2; exit 2;
}
python3 - "$vendor" "$patched" "$provenance" <<'PY'
import hashlib,json,pathlib,sys
vendor,patched=map(pathlib.Path,sys.argv[1:3])
manifest=json.loads(pathlib.Path(sys.argv[3]).read_text())
if manifest["vendor_dir"]!=str(vendor) or manifest["isolated_dir"]!=str(patched):
    raise SystemExit("Source provenance tree paths do not match")
if set(manifest["changed_symbols"])!={"C7H_1","C8H_1","C9H_1","C10H_1"}:
    raise SystemExit("Unexpected isolated source patch content")
for root,key in ((vendor,"vendor_wilson_sha256"),(patched,"patched_wilson_sha256")):
    current=hashlib.sha256((root/"src/wilson.c").read_bytes()).hexdigest()
    if current!=manifest[key]:
        raise SystemExit(f"Source hash mismatch for {root}")
print("Verified A1M source provenance: official and isolated versions")
PY

ref_sm=work/gateA1j_superiso_build/sm_output.log
[[ -f "$ref_sm" ]] || {
  echo "Missing Gate A1J official SM output: $ref_sm" >&2; exit 2;
}
mkdir -p "$out"
for variant in vendor isolated; do
  root="$vendor"
  if [[ "$variant" == "isolated" ]]; then root="$patched"; fi
  gcc -std=gnu11 -O2 -Wall -Wextra -I"$root/src" \
    "$script_dir/gateA1n_superiso_br_candidate.c" \
    "$root/src/libsuperiso.a" -lm -o "$out/gateA1n_$variant"
  (cd "$root" && "$out/gateA1n_$variant") > "$out/$variant.txt"
done

python3 "$script_dir/gateA1n_check_br_candidate.py" \
  --vendor "$out/vendor.txt" \
  --isolated "$out/isolated.txt" \
  --reference_sm "$ref_sm" \
  --output "$out/result.json"

{
  sha256sum "$vendor/src/wilson.c" "$patched/src/wilson.c"
  sha256sum "$vendor/src/libsuperiso.a" "$patched/src/libsuperiso.a"
  sha256sum "$out/gateA1n_vendor" "$out/gateA1n_isolated"
} > "$out/library_binary_sha256.txt"

echo "STATUS BR_CANDIDATE_CONTROLS_COMPLETE_NOT_A_ZEE_EXCLUSION"
echo "Outputs: $out/result.json $out/vendor.txt $out/isolated.txt"
