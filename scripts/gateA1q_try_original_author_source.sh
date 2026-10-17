#!/usr/bin/env bash
# A1Q: retrieve original author c2HDM.m, if possible, then fingerprint it.
# This script never modifies SuperIso, HEPfit or any matching results.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
out="work/gateA1q_original_nnlo_theory_v1"
mkdir -p "$out"
sourcefile="$out/c2HDM.m"
statusfile="$out/source_retrieval_status.txt"

# The URL below follows the published official TTP12-029 README path,
# but the direct Mathematica download route has not been externally
# confirmed. Failure must NOT be replaced by a mirrored or fake source.
url="https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/c2HDM.m"
if [[ ! -f "$sourcefile" ]]; then
  echo "Attempting official TTP12-029 archive candidate: $url"
  tmp="$sourcefile.part"
  if curl --fail --location --silent --show-error \
      --connect-timeout 15 --max-time 90 \
      --output "$tmp" "$url"; then
    if python3 - "$tmp" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
raw=p.read_bytes()
if len(raw)<1000 or len(raw)>20_000_000:
    raise SystemExit("Not a plausible original Mathematica text size")
text=raw.decode("utf-8")
if "<html" in text.lower() or "cH[" not in text:
    raise SystemExit("Not a c2HDM.m Mathematica source")
PY
    then
      mv "$tmp" "$sourcefile"
      printf '%s\n' "CANDIDATE_FETCHED_OFFICIAL_URL=$url" > "$statusfile"
    else
      rm -f "$tmp"
      printf '%s\n' "BLOCKED_RETRIEVED_BYTES_FAILED_SOURCE_CHECK=$url" > "$statusfile"
    fi
  else
    rm -f "$tmp"
    printf '%s\n' "BLOCKED_DIRECT_AUTHOR_MATHEMATICA_URL_NOT_VERIFIED_OR_UNAVAILABLE=$url" > "$statusfile"
  fi
fi

python3 scripts/gateA1q_original_theory_preflight.py \
  --original-mathematica-source "$sourcefile" \
  --superiso-source work/gateA1m_isolated_nlo_v1/isolated_superiso/src/wilson.c \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --hepfit-source work/gateA1p_hepfit_typeii_v1/HEPfit_THDMMatching.cpp \
  --hepfit-provenance work/gateA1p_hepfit_typeii_v1/hepfit_provenance.json \
  --output "$out/theory_preflight.json"
printf '%s\n' "REF_AUTHOR_README=https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/readme.pdf"
printf '%s\n' "IMPORTANT: PRE-FLIGHT IS NOT ORIGINAL-FORMULA VALIDATION."
