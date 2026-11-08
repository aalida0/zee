#!/usr/bin/env bash
# Single bounded source-matched LFV physics run; safe Git delivery outside Codex.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
BRANCH="research/zee-full-constraints"
DIR="research/full_constraints/lfv_transfer_2026"
TASK="$DIR/TASK.md"
RUNNER="$DIR/run_once.sh"
RESULT="$DIR/RESULT.json"
LOGDIR="work/lfv_transfer_2026/logs"
[[ "$(git branch --show-current)" == "$BRANCH" ]] || { echo "STOP: wrong branch" >&2; exit 2; }
[[ -f "$TASK" ]] || { echo "STOP: missing task; git pull first" >&2; exit 2; }
command -v codex >/dev/null || { echo "STOP: codex not found" >&2; exit 2; }
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "STOP: pre-existing tracked user modifications" >&2; git status --short; exit 2
fi
mkdir -p "$LOGDIR"
if ! codex --help 2>&1 | grep -q -- '--approve-for-me'; then
  echo "STOP: this Codex CLI lacks --approve-for-me" >&2; exit 2
fi
if ! codex exec --help 2>&1 | grep -q -- '--sandbox'; then
  echo "STOP: this Codex CLI has different sandbox option syntax" >&2; exit 2
fi

# No unrestricted network. Download only official public research sources.
DOMAINS='{ "arxiv.org" = "allow", "*.arxiv.org" = "allow", "github.com" = "allow", "*.github.com" = "allow", "*.githubusercontent.com" = "allow", "gitlab.com" = "allow", "*.gitlab.com" = "allow", "inspirehep.net" = "allow", "*.inspirehep.net" = "allow", "doi.org" = "allow", "link.springer.com" = "allow", "*.springer.com" = "allow" }'

check_scope() {
  local p
  while IFS= read -r p; do
    [[ -z "$p" ]] && continue
    case "$p" in
      "$DIR"/*)
        if [[ "$p" == "$RUNNER" || "$p" == "$TASK" ]]; then
          echo "STOP: protected runner/task modified: $p" >&2; return 1
        fi ;;
      *) echo "STOP: tracked modification outside LFV output scope: $p" >&2; return 1 ;;
    esac
  done < <( { git diff --name-only; git diff --cached --name-only; } | sort -u )
}

safe_commit_push() {
  check_scope || return 6
  [[ -s "$DIR/EXECUTION_REPORT.md" ]] || { echo "STOP: no execution report" >&2; return 5; }
  # No auto-fix of scientific data; explicit Git error on CRLF/trailing whitespace.
  git add -A -- "$DIR"
  git diff --cached --check || { echo "STOP: staged whitespace error; do not rerun science" >&2; return 5; }
  local p
  while IFS= read -r p; do
    [[ -z "$p" ]] && continue
    if [[ "$p" == "$RUNNER" || "$p" == "$TASK" ]]; then
      echo "STOP: protected file staged: $p" >&2; return 6
    fi
    case "$p" in "$DIR"/*) ;; *) echo "STOP: unsafe staged path: $p" >&2; return 6;; esac
  done < <(git diff --cached --name-only)
  if ! git diff --cached --quiet; then
    git diff --cached --stat
    git commit -m "Validate transferable leading LFV neutral amplitudes on frozen Zee cards"
  fi
  git push origin "$BRANCH" || { echo "STOP: push failed; local result retained" >&2; return 5; }
  local l r
  l="$(git rev-parse HEAD)"
  r="$(git ls-remote origin "refs/heads/$BRANCH" | awk 'NR==1 {print $1}')"
  [[ -n "$r" && "$r" == "$l" ]] || { echo "STOP: remote SHA mismatch" >&2; return 5; }
  echo "VERIFIED REMOTE SHA $l"
}

# Never re-compute science if a past execution already wrote its results.
if [[ -s "$RESULT" && -s "$DIR/EXECUTION_REPORT.md" ]]; then
  echo "Existing scientific result found: attempting scoped Git delivery ONLY."
  safe_commit_push
  exit 0
fi

PROMPT="Read AGENTS.md and $TASK; EXECUTE this single bounded four-card LFV task, not a plan. First pin texture vs scale_0.001 Yukawa-card provenance. Transfer ONLY nonoverlapping standalone post-erratum general-2HDM neutral fermion-Zgamma and hZ classes when directly source-matched. Provide actual independent 2HDM numerical controls, complex C_L/C_R for exact frozen cards, interference and materiality. Mark incomplete sectors UNKNOWN. No new scan or original tensor project; no committing or pushing yourself. Save all outputs under $DIR, downloads under ignored work/lfv_transfer_2026. A genuine blocked result with reproducible reasons is allowed. Stop after this one execution."
echo "ONE CODEX EXECUTION, restricted sandbox, logs: $LOGDIR"
set +e
codex --approve-for-me \
  -c 'sandbox_workspace_write.network_access=true' \
  -c 'features.network_proxy.enabled=true' \
  -c "features.network_proxy.domains=$DOMAINS" \
  exec --sandbox workspace-write "$PROMPT" 2>&1 | tee "$LOGDIR/codex_once.log"
rc="${PIPESTATUS[0]}"
set -e
if [[ "$rc" -ne 0 ]]; then
  echo "STOP: Codex exited $rc; no automatic retry of auth/quota/permissions errors" >&2
  exit "$rc"
fi
safe_commit_push
[[ -s "$RESULT" ]] || { echo "PARTIAL: no RESULT.json; no automatic rerun" >&2; exit 3; }
python3 - "$RESULT" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print("SCIENTIFIC STATUS:", d.get("status","UNDECLARED"))
print("PHYSICAL LFV:",d.get("physical_lfv","UNKNOWN"))
print("FINAL ARTIFACTS READY:",d.get("final_artifacts_ready",False))
PY
