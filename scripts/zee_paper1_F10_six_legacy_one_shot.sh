#!/usr/bin/env bash
# F10: exact six newly screened physical scalar points, source-pinned
# archived historical SuperIso v5. NOT a modern 2026 NNLO exclusion.
set -euo pipefail
cd /home/aalida/zee
python3 -m unittest discover -s tests -p 'test_zee_paper1_F10_six_new_two_charged_legacy_bsgamma.py' -v
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
python3 -u scripts/zee_paper1_F10_six_new_two_charged_legacy_bsgamma.py \
  --scan-dir /home/aalida/zee/work/zee_paper1_florentino_pilot_20261021T111413Z \
  --output-dir "/home/aalida/zee/work/zee_paper1_F10_legacy_six_$stamp" "$@"
