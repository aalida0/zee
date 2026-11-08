#!/usr/bin/env bash
# Continue a single Codex scientific assignment until a final verdict is
# verified and pushed, or an actual execution blocker/run limit occurs.
set -euo pipefail

TASK="research/full_constraints/CANDIDATE_A_FINAL_END_TO_END_EXECUTION.md"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
BRANCH="$(git branch --show-current)"
if [[ "$BRANCH" != "research/zee-full-constraints" ]]; then
    echo "ERROR: expected research/zee-full-constraints, got $BRANCH" >&2
    exit 2
fi
if [[ ! -f "$TASK" ]]; then
    echo "ERROR: missing $TASK. Run git pull --ff-only first." >&2
    exit 2
fi
command -v codex >/dev/null || { echo "ERROR: Codex CLI missing" >&2; exit 2; }
# Prefer current CLI automatic review of on-request permissions when present;
# it retains the workspace-write sandbox and can authorize Git network access.
EXEC_FLAGS=(--sandbox workspace-write)
if codex exec --help 2>/dev/null | grep -q -- "--approve-for-me"; then
    EXEC_FLAGS=(--approve-for-me)
fi
MAX_ROUNDS="${CODEX_MAX_ROUNDS:-12}"
if ! [[ "$MAX_ROUNDS" =~ ^[1-9][0-9]*$ ]]; then
    echo "CODEX_MAX_ROUNDS must be a positive integer" >&2; exit 2
fi
LOG_DIR="${CODEX_LOG_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/zee-codex-vacuum.XXXXXXXX")}"
mkdir -p "$LOG_DIR"
echo "Codex logs (not tracked): $LOG_DIR"
echo "Task: $TASK | max Codex turns: $MAX_ROUNDS"

VERDICT="research/full_constraints/candidate_a/final_study/VERDICT.json"
REPORT="research/full_constraints/CANDIDATE_A_FINAL_DECISION_2026-11-08.md"
RESUME_PROMPT="Continue executing $TASK from final_study/WORK_CHECKPOINT.md. Do not stop after a partial or inconclusive summary. Finish independent exact proofs, source novelty check, predeclared scalar sample, method comparison and charged observable effects, then produce an honest GO or NO_GO. Execute tests, COMMIT and PUSH, and verify remote SHA. A checkpoint is not completion. Use Python/exact math fallbacks if specialist packages are absent."

blocked_external() {
    [[ -s "$VERDICT" ]] || return 1
    python3 - "$VERDICT" <<'PY'
import json,sys
try:
    x=json.load(open(sys.argv[1]))
    if x.get("verdict") == "BLOCKED_EXTERNAL":
        sys.exit(0)
except Exception:
    pass
sys.exit(1)
PY
}

already_done() {
    [[ -s "$VERDICT" && -s "$REPORT" ]] || return 1
    python3 - "$VERDICT" <<'PY'
import json, sys
try:
    x = json.load(open(sys.argv[1]))
    needed = ("math_independent","prior_art_checked","scenarios_evaluated",
              "positive_certified","negative_certified","unknown",
              "physics_materiality","verdict","confidence_limits")
    assert x.get("verdict") in ("GO_SCALAR_THEORY_PAPER_CANDIDATE","NO_GO_CURRENT_DIRECTION")
    assert all(k in x for k in needed)
except Exception:
    sys.exit(1)
PY
}

remote_verified() {
    [[ -z "$(git status --porcelain)" ]] || return 1
    local sha remote
    sha="$(git rev-parse HEAD)"
    remote="$(git ls-remote origin refs/heads/research/zee-full-constraints | awk 'NR==1 {print $1}')" || return 1
    [[ -n "$remote" && "$sha" == "$remote" ]]
}

if already_done && remote_verified; then
    echo "Already complete, remote verified:"
    python3 -c 'import json; print(json.load(open("research/full_constraints/candidate_a/final_study/VERDICT.json"))["verdict"])'
    git rev-parse HEAD
    exit 0
fi

# Current Codex CLI: --full-auto is deprecated. Workspace-write is required
# to create code and commits. Network/Git push may still need user approval.
for ((i=1;i<=MAX_ROUNDS;i++)); do
    echo "===== Codex round $i/$MAX_ROUNDS ====="
    logfile="$LOG_DIR/codex_round_${i}.log"
    set +e
    if (( i == 1 )); then
        codex exec "${EXEC_FLAGS[@]}" \
            "Read AGENTS.md and $TASK. Execute the ENTIRE scientific task, not a plan. Continue all gates until reviewer-defensible GO or NO_GO. Commit/push real progress checkpoints and the final verified result; use math/software fallbacks if needed. If a runtime context limit forces a checkpoint, write WORK_CHECKPOINT.md so the same session can resume." \
            2>&1 | tee "$logfile"
        code="${PIPESTATUS[0]}"
    else
        codex exec resume --last "$RESUME_PROMPT" 2>&1 | tee "$logfile"
        code="${PIPESTATUS[0]}"
    fi
    set -e
    if [[ "$code" -ne 0 ]]; then
        echo "ERROR: Codex exited $code; see $logfile. Not automatically retrying auth/quota/fatal failures." >&2
        exit "$code"
    fi
    if blocked_external; then
        echo "HARD BLOCKER: Codex reported BLOCKED_EXTERNAL in $VERDICT" >&2
        echo "Inspect the blocker and fix permissions/source availability; no blind retries." >&2
        exit 4
    fi
    if already_done; then
        if remote_verified; then
            echo "SUCCESS: final science verdict and remote SHA verified"
            python3 -c 'import json; print(json.load(open("research/full_constraints/candidate_a/final_study/VERDICT.json"))["verdict"])'
            git rev-parse HEAD
            exit 0
        fi
        echo "A final verdict exists but Git cleanliness/remote verification is unfinished; continuing."
    fi
done
echo "STOP: $MAX_ROUNDS rounds completed without verified final verdict." >&2
echo "This is NOT science completion. Review $LOG_DIR and continue with a higher CODEX_MAX_ROUNDS when appropriate." >&2
exit 3
