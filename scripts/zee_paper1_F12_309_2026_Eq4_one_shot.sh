#!/usr/bin/env bash
# F12: all 309 original Zee scalar points, source-pinned genuine
# published 2026 Eq4 LO C7/C8 rate + collider included proxy frontier.
set -euo pipefail
cd /home/aalida/zee
python3 -m unittest discover -s tests \
  -p 'test_zee_paper1_F12_309_modern_Eq4_Bsgamma_frontier.py' -v
f6_dir="$(python3 - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0,"scripts")
from zee_paper1_F10_six_new_two_charged_legacy_bsgamma import discover_f6
print(discover_f6(Path("/home/aalida/zee/work"))[0])
PY
)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="/home/aalida/zee/work/zee_paper1_F12_309_2026_Eq4_frontier_$stamp"
python3 -u scripts/zee_paper1_F12_309_modern_Eq4_Bsgamma_frontier.py \
  --f6-dir "$f6_dir" --output-dir "$out" "$@"
