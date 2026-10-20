#!/usr/bin/env bash
# Read-only postprocessing of existing A1P Type-II NNLO matching results.
# Uses original pinned HEPfit executable and A1M SuperIso static library.
set -Eeuo pipefail
if (( $# != 2 )); then
  echo "Usage: bash $0 A1M_ISOLATED_SUPERISO_DIR EXISTING_A1P_OUTPUT_DIR" >&2
  exit 2
fi
a1m=$(realpath "$1")
out=$(realpath "$2")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
a1m_manifest="$(dirname "$a1m")/source_patch_provenance.json"
for input in "$a1m/src/wilson.c" "$a1m/src/libsuperiso.a" \
             "$a1m_manifest" "$out/result.json" \
             "$out/mass_input_provenance.json" \
             "$out/HEPfit_THDMMatching.cpp" "$out/hepfit_provenance.json" \
             "$out/hepfit_matching"; do
  [[ -f "$input" ]] || { echo "Missing original A1P/A1M file: $input" >&2; exit 2; }
done
mt=$(python3 - "$out/mass_input_provenance.json" <<'PY'
import json,sys
data=json.load(open(sys.argv[1]))
if data.get("status")!="GATE_A1P_RUNNING_TOP_FROM_SUPERISO_FUNCTION_NOT_LO_INVERSION":
    raise SystemExit("Missing directly computed SuperIso top-mass provenance")
print(f"{data['mt_muW_GeV']:.17g}")
PY
)
# Compile ONLY the read-only standalone helper probe, linked against
# the existing A1M static archive. No source or physics code patch.
gcc -std=gnu11 -O2 -Wall -Wextra -I"$a1m/src" \
  "$script_dir/gateA1p_probe_nnlo_finite_superiso.c" \
  "$a1m/src/libsuperiso.a" -lm \
  -o "$out/gateA1p_probe_nnlo_finite_superiso" \
  > "$out/build_nnlo_finite_helpers.log" 2>&1 || {
    cat "$out/build_nnlo_finite_helpers.log" >&2
    exit 1
  }
(cd "$a1m" && "$out/gateA1p_probe_nnlo_finite_superiso" "$mt") \
  | tee "$out/nnlo_superiso_finite_helpers.txt"

python3 "$script_dir/gateA1p_audit_nnlo_finite_functions.py" \
  --existing-result "$out/result.json" \
  --mass-input "$out/mass_input_provenance.json" \
  --superiso-finite "$out/nnlo_superiso_finite_helpers.txt" \
  --hepfit-binary "$out/hepfit_matching" \
  --superiso-source "$a1m/src/wilson.c" \
  --a1m-provenance "$a1m_manifest" \
  --hepfit-source "$out/HEPfit_THDMMatching.cpp" \
  --hepfit-provenance "$out/hepfit_provenance.json" \
  --library-paths "$out/hepfit_runtime_library_paths.txt" \
  --output "$out/nnlo_finite_function_audit.json"
