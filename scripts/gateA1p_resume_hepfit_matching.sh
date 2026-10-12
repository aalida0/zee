#!/usr/bin/env bash
# Gate A1P continuation: resume existing compiled HEPfit source and compare
# exact Type-II Wilson matching to isolated SuperIso A1M.
# No HEPfit source download/re-extraction; no vendor modifications.
set -Eeuo pipefail
if (( $# != 2 )); then
  echo "Usage: bash $0 A1M_ISOLATED_SUPERISO_DIR EXISTING_A1P_OUTPUT_DIR" >&2
  exit 2
fi
a1m=$(realpath "$1")
out=$(realpath "$2")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
[[ -f "$out/hepfit_matching" && -f "$out/hepfit_matching.cpp" &&
   -f "$out/HEPfit_THDMMatching.cpp" &&
   -f "$out/hepfit_provenance.json" &&
   -f "$a1m/src/libsuperiso.a" ]] || {
  echo "Missing compiled HEPfit reference / pinned source / A1M library" >&2
  exit 2
}

# The upstream source must match the exact immutable Git blob already
# vetted for A1P; otherwise stop, regardless of successful compilation.
python3 - "$script_dir" "$out" <<'PY'
import hashlib,json,pathlib,sys
sys.path.insert(0,sys.argv[1])
from gateA1p_prepare_hepfit_matching import HEPFIT_BLOB,git_blob_sha,extract
out=pathlib.Path(sys.argv[2])
manifest=json.loads((out/"hepfit_provenance.json").read_text())
source=(out/"HEPfit_THDMMatching.cpp").read_bytes()
if (manifest.get("upstream_git_blob")!=HEPFIT_BLOB or
    git_blob_sha(source)!=HEPFIT_BLOB or
    hashlib.sha256(source).hexdigest()!=manifest.get("upstream_source_sha256")):
    raise SystemExit("A1P HEPfit source/provenance mismatch")
fragment=extract(source.decode())
if fragment not in (out/"hepfit_matching.cpp").read_text():
    raise SystemExit("A1P generated reference no longer contains the unmodified HEPfit formula")
print("Verified independent HEPfit source provenance and original formula")
PY

# Resolve compile-time GSL vs runtime dynamic loader mismatch.
# Probe the package configuration, compiler-selected library directory,
# and any explicitly supplied path, but do not silently swap SONAMEs.
# A pinned original HEPfit reference must stay linked to the actual GSL.
need_gsl=$(ldd "$out/hepfit_matching" | awk '/^[[:space:]]*libgsl\.so/{print $1;exit}')
[[ -n "$need_gsl" ]] || { echo "No GSL dependency found in HEPfit executable" >&2; exit 2; }
declare -a candidates=()
[[ -z "${GATE_A1P_GSL_LIBDIR:-}" ]] || candidates+=("$GATE_A1P_GSL_LIBDIR")
if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists gsl; then
  candidates+=("$(pkg-config --variable=libdir gsl)")
  while IFS= read -r part; do
    [[ -z "$part" ]] || candidates+=("$part")
  done < <(pkg-config --libs-only-L gsl | tr ' ' '\n' | sed -n 's/^-L//p')
fi
if command -v gsl-config >/dev/null 2>&1; then
  prefix=$(gsl-config --prefix)
  candidates+=("$prefix/lib" "$prefix/lib64")
fi
compiler_gsl=$(g++ -print-file-name=libgsl.so)
[[ "$compiler_gsl" != "libgsl.so" ]] &&
  candidates+=("$(dirname "$(realpath "$compiler_gsl")")") || true
IFS=':' read -ra inherited <<< "${LD_LIBRARY_PATH:-}"
for d in "${inherited[@]}"; do [[ -z "$d" ]] || candidates+=("$d"); done
IFS=':' read -ra linked <<< "${LIBRARY_PATH:-}"
for d in "${linked[@]}"; do [[ -z "$d" ]] || candidates+=("$d"); done

found_libdir=""
for d in "${candidates[@]}"; do
  if [[ -d "$d" && -f "$d/$need_gsl" ]]; then
    found_libdir=$(realpath "$d")
    break
  fi
done

if [[ -z "$found_libdir" ]]; then
  echo "GSL runtime dependency $need_gsl was not found in configured paths." >&2
  echo "Compiler/linker succeeded but shared-library loader cannot resolve $need_gsl." >&2
  echo "Diagnostic: ldd $out/hepfit_matching" >&2
  ldd "$out/hepfit_matching" >&2 || true
  echo "Locate the matching GSL library (for example under CERN LCG view)." >&2
  echo "Then run: GATE_A1P_GSL_LIBDIR=/absolute/path/to/lib bash $0 '$a1m' '$out'" >&2
  exit 1
fi
export LD_LIBRARY_PATH="$found_libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
echo "Resolved $need_gsl via $found_libdir"
ldd "$out/hepfit_matching" > "$out/hepfit_runtime_ldd.log"
if grep -q 'not found' "$out/hepfit_runtime_ldd.log"; then
  echo "Additional shared libraries missing; inspect $out/hepfit_runtime_ldd.log" >&2
  cat "$out/hepfit_runtime_ldd.log" >&2
  exit 1
fi

# Evaluate the *actual* running top in SuperIso at the identical
# muW, using the exact expression found in src/wilson.c:1599.
# No LO inversion and no empirical adjustment of the mass.
gcc -std=gnu11 -O2 -Wall -Wextra -I"$a1m/src" \
  "$script_dir/gateA1p_superiso_top_mass.c" \
  "$a1m/src/libsuperiso.a" -lm \
  -o "$out/superiso_running_top" > "$out/build_superiso_top.log" 2>&1
(cd "$a1m" && "$out/superiso_running_top") | tee "$out/superiso_running_top.txt"

# Derive the HEPfit input ONLY from independent SuperIso running_mass().
read -r mt_muW muW < <(
  python3 - "$out/superiso_running_top.txt" <<'PY'
import pathlib,re,sys
text=pathlib.Path(sys.argv[1]).read_text()
m=re.search(r"SUPERIOMT mtmuW_GeV=([0-9.eE+-]+) muW_GeV=([0-9.eE+-]+)",text)
if not m: raise SystemExit("Running-top values absent")
print(m.group(1),m.group(2))
PY
)
beta=1.394
tanbeta=$(python3 - <<'PY'
import math
print(f"{math.tan(1.394):.17g}")
PY
)
# A new explicit comparison against the old inferred value is recorded.
python3 - "$mt_muW" "$out" <<'PY'
import json,sys,pathlib
mt=float(sys.argv[1])
p=pathlib.Path(sys.argv[2])/"mass_input_provenance.json"
p.write_text(json.dumps({
    "status":"GATE_A1P_RUNNING_TOP_FROM_SUPERISO_FUNCTION_NOT_LO_INVERSION",
    "mt_muW_GeV":mt,
    "previous_LO_inferred_mt_GeV":163.10709645657502,
    "difference_from_prior_inference_GeV":mt-163.10709645657502,
    "full_TypeII_BR_validated":False,
},indent=2)+"\n")
print("Running top mass:",mt)
PY

# Reuse SuperIso matching pilot executable if present; it links against
# A1M and remains unaffected by the original SuperIso vendor tree.
if [[ ! -x "$out/superiso_a1m" ]]; then
  gcc -std=gnu11 -O2 -Wall -Wextra -I"$a1m/src" \
    "$script_dir/gateA1l_zee_superiso_matching_pilot.c" \
    "$a1m/src/libsuperiso.a" -lm -o "$out/superiso_a1m" \
    > "$out/build_superiso.log" 2>&1
fi

pairs=()
for mass in 300 700 1000 2000; do
  # A1L input contract demands m2>m1 even in gamma=0 pure-H1 mode.
  m2=$((mass+1))
  (cd "$a1m" && "$out/superiso_a1m" \
     "$mass" "$m2" 0 "$beta") > "$out/superiso_${mass}.txt"
  (cd "$out" && ./hepfit_matching "$tanbeta" "$mt_muW" \
     "$muW" "$mass") > "$out/hepfit_${mass}.txt"
  pairs+=(--pair "$mass" "$out/superiso_${mass}.txt"
           "$out/hepfit_${mass}.txt")
done

set +e
python3 "$script_dir/gateA1p_compare_hepfit_matching.py" \
  "${pairs[@]}" --beta "$beta" \
  --hepfit-provenance "$out/hepfit_provenance.json" \
  --output "$out/result.json"
status=$?
set -e

{
  sha256sum "$a1m/src/wilson.c" "$a1m/src/libsuperiso.a"
  sha256sum "$out/HEPfit_THDMMatching.cpp" "$out/hepfit_matching.cpp"
  sha256sum "$out/hepfit_matching" "$out/superiso_a1m"
  sha256sum "$out/superiso_running_top"
} > "$out/source_binaries_sha256.txt"
echo "A1P result: $out/result.json"
echo "STATUS: INDEPENDENT_TYPEII_MATCHING_CONDITIONAL_COMPARISON_NOT_BR"
exit "$status"
