#!/usr/bin/env bash
# Gate A1P: INDEPENDENT HEPfit Type-II charged matching, not a BR/exclusion.
# Fetch one source file from HEPfit (GPL), verify immutable Git blob SHA,
# compile exact upstream setWCbsg formulas in an independent local shim,
# and compare them against A1M SuperIso matching at identical parameters.
set -Eeuo pipefail
if (( $# < 1 || $# > 2 )); then
  echo "Usage: bash $0 /path/to/A1M_isolated_superiso [fresh_output_dir]" >&2
  exit 2
fi
a1m=$(realpath "$1")
out=$(realpath -m "${2:-work/gateA1p_hepfit_typeii_v1}")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [[ "$a1m" == "$out" || "$a1m/" == "$out/"* ]]; then
  echo "Reference output must not be written into A1M source tree" >&2
  exit 2
fi
[[ -f "$a1m/src/libsuperiso.a" && -f "$a1m/src/wilson.c" ]] || {
  echo "Missing compiled and isolated A1M SuperIso source" >&2;exit 2;
}
[[ ! -e "$out/hepfit_matching.cpp" ]] || {
  echo "Refuse stale generated HEPfit source: choose a fresh output directory" >&2;exit 2;
}
for command in python3 curl g++ gcc sha256sum; do
  command -v "$command" >/dev/null || {
    echo "Missing command: $command" >&2; exit 2;
  }
done
mkdir -p "$out"
# Direct source audit of the SuperIso running-top prescription. The
# numerical mt used below is a provisional input from A1L LO inversion,
# not claimed independently verified by this source-only report.
python3 "$script_dir/gateA1p_audit_running_top.py" \
  --source "$a1m/src/wilson.c" \
  --output "$out/superiso_running_top_source_audit.json"

source_url="https://raw.githubusercontent.com/silvest/HEPfit/master/THDM/src/THDMMatching.cpp"
curl --fail --location --retry 2 --silent --show-error \
  "$source_url" -o "$out/HEPfit_THDMMatching.cpp"
python3 "$script_dir/gateA1p_prepare_hepfit_matching.py" \
  --hepfit-source "$out/HEPfit_THDMMatching.cpp" \
  --cpp-output "$out/hepfit_matching.cpp" \
  --manifest "$out/hepfit_provenance.json"

# GSL is required by upstream HEPfit's exact gsl_sf_dilog expression.
# Requiring the library avoids silently replacing independent formulas.
cflags=()
libs=(-lgsl -lgslcblas -lm)
if command -v pkg-config >/dev/null 2>&1 &&
   pkg-config --exists gsl; then
  read -ra cflags <<< "$(pkg-config --cflags gsl)"
  read -ra libs <<< "$(pkg-config --libs gsl)"
fi
if ! g++ -std=c++17 -O2 -Wall -Wextra \
     "${cflags[@]}" "$out/hepfit_matching.cpp" \
     -o "$out/hepfit_matching" "${libs[@]}" \
     > "$out/build_hepfit.log" 2>&1; then
  echo "Independent HEPfit C++/GSL build failed. See $out/build_hepfit.log" >&2
  echo "Use an LCG view with GNU C++ and GSL headers/libraries. Do not alter physics formulas." >&2
  exit 1
fi
gcc -std=gnu11 -O2 -Wall -Wextra \
  -I"$a1m/src" "$script_dir/gateA1l_zee_superiso_matching_pilot.c" \
  "$a1m/src/libsuperiso.a" -lm -o "$out/superiso_a1m" \
  > "$out/build_superiso.log" 2>&1

mt_muW="${GATE_A1P_MT_MUW_GEV:-163.10709645657502}"
# This reference was inferred by inverting SuperIso LO C7 at mHp=300.
# We compare DIFFERENT, independently implemented NLO/NNLO formulas
# but have NOT independently verified the exact mt-running convention.
# The output flags this limitation and never declares a physics exclusion.
tanbeta=$(python3 - <<'PY'
import math
print(f"{math.tan(1.394):.17g}")
PY
)
muW="160.7384"
beta="1.394"
masses=(300 700 1000 2000)
pairs=()
for mass in "${masses[@]}"; do
  m2=$((mass+1))
  (cd "$a1m" && "$out/superiso_a1m" \
    "$mass" "$m2" 0 "$beta") \
    > "$out/superiso_${mass}.txt"
  (cd "$out" && ./hepfit_matching "$tanbeta" "$mt_muW" \
     "$muW" "$mass") > "$out/hepfit_${mass}.txt"
  pairs+=(--pair "$mass" "$out/superiso_${mass}.txt" "$out/hepfit_${mass}.txt")
done

set +e
python3 "$script_dir/gateA1p_compare_hepfit_matching.py" \
  "${pairs[@]}" --beta "$beta" \
  --hepfit-provenance "$out/hepfit_provenance.json" \
  --output "$out/result.json"
result=$?
set -e
{
  sha256sum "$a1m/src/wilson.c" "$a1m/src/libsuperiso.a"
  sha256sum "$out/HEPfit_THDMMatching.cpp" "$out/hepfit_matching.cpp"
  sha256sum "$out/hepfit_matching" "$out/superiso_a1m"
} > "$out/source_binaries_sha256.txt"
echo "RESULTS: $out/result.json"
echo "STATUS: A1P_INDEPENDENT_TYPEII_MATCHING_PILOT_NOT_PHYSICAL_BR"
exit "$result"
