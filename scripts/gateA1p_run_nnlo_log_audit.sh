#!/usr/bin/env bash
# Source-hashed NNLO matching-log check using the *actual compiled*
# SuperIso v5 Delta3H/Delta4H helpers. No matching source changed.
set -Eeuo pipefail
if (( $# != 2 )); then
  echo "Usage: bash $0 A1M_ISOLATED_SUPERISO_DIR EXISTING_A1P_RESULTS_DIR" >&2
  exit 2
fi
a1m=$(realpath "$1")
out=$(realpath "$2")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
a1m_prov="$(dirname "$a1m")/source_patch_provenance.json"
[[ -f "$a1m/src/libsuperiso.a" &&
   -f "$a1m/src/wilson.c" &&
   -f "$a1m_prov" &&
   -f "$out/result.json" &&
   -f "$out/mass_input_provenance.json" &&
   -f "$out/HEPfit_THDMMatching.cpp" &&
   -f "$out/hepfit_provenance.json" ]] || {
  echo "Missing existing A1M/A1P source/provenance/compiled library/results" >&2
  exit 2
}

# Fail before running any helper unless the manifest/source matches.
python3 - "$a1m" "$a1m_prov" "$out" "$script_dir" <<'PY'
import json,pathlib,sys,hashlib
a1m=pathlib.Path(sys.argv[1])
a1m_prov=pathlib.Path(sys.argv[2])
out=pathlib.Path(sys.argv[3])
sys.path.insert(0,sys.argv[4])
from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB, git_blob_sha
si=json.loads(a1m_prov.read_text())
hf=json.loads((out/"hepfit_provenance.json").read_text())
if hashlib.sha256((a1m/"src/wilson.c").read_bytes()).hexdigest()!=si.get("patched_wilson_sha256"):
    raise SystemExit("A1M source does not match source manifest")
if (git_blob_sha((out/"HEPfit_THDMMatching.cpp").read_bytes())!=HEPFIT_BLOB
        or hf.get("upstream_git_blob")!=HEPFIT_BLOB):
    raise SystemExit("HEPfit source does not match pinned reference blob")
print("Pinned SuperIso A1M and HEPfit source provenance verified")
PY

read -r mt tanbeta < <(
  python3 - "$out/mass_input_provenance.json" "$out/result.json" <<'PY'
import json,math,sys
mi=json.load(open(sys.argv[1]))
comparison=json.load(open(sys.argv[2]))
assert mi["status"]=="GATE_A1P_RUNNING_TOP_FROM_SUPERISO_FUNCTION_NOT_LO_INVERSION"
mt=float(mi["mt_muW_GeV"])
tanb=float(comparison["tanbeta"])
assert all(math.isfinite(x) and x>0 for x in (mt,tanb))
print(f"{mt:.17g} {tanb:.17g}")
PY
)

# Link exactly the existing A1M static library. No rebuild or source edits.
gcc -std=gnu11 -O2 -Wall -Wextra -I"$a1m/src" \
  "$script_dir/gateA1p_probe_nnlo_helpers.c" \
  "$a1m/src/libsuperiso.a" -lm \
  -o "$out/gateA1p_probe_nnlo_helpers" \
  > "$out/build_nnlo_helpers.log" 2>&1 || {
    echo "Cannot compile SuperIso helper probe: $out/build_nnlo_helpers.log" >&2
    cat "$out/build_nnlo_helpers.log" >&2
    exit 1
  }
(cd "$a1m" && "$out/gateA1p_probe_nnlo_helpers" "$mt" "$tanbeta") \
  | tee "$out/nnlo_helper_values.txt"

python3 "$script_dir/gateA1p_verify_nnlo_log_difference.py" \
  --existing-result "$out/result.json" \
  --mass-provenance "$out/mass_input_provenance.json" \
  --superiso-source "$a1m/src/wilson.c" \
  --a1m-provenance "$a1m_prov" \
  --hepfit-source "$out/HEPfit_THDMMatching.cpp" \
  --hepfit-provenance "$out/hepfit_provenance.json" \
  --superiso-helper-output "$out/nnlo_helper_values.txt" \
  --output "$out/nnlo_log_difference.json"

printf 'STATUS SOURCE_AND_COMPILED_HELPER_AUDIT_COMPLETE_NOT_NNLO_PHYSICS_VALIDATION\n'
