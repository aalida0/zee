#!/usr/bin/env bash
# Narrowly permissioned Codex run plus trusted, allowlisted git delivery.
# Codex: workspace-write, network proxy allowlist, on-request approval.
# Wrapper: stages/commits/pushes ONLY physical_closure_2026/ and final report.
# No --yolo / danger-full-access; no system-wide installations.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
BRANCH="research/zee-full-constraints"
TASK="research/full_constraints/PHYSICAL_CONSTRAINT_CLOSURE_EXECUTION_TASK_2026-11-08.md"
DIR="research/full_constraints/physical_closure_2026"
REPORT="research/full_constraints/PHYSICAL_CONSTRAINT_CLOSURE_REPORT_2026-11-08.md"
RESULT="$DIR/RESULT.json"
if [[ "$(git branch --show-current)" != "$BRANCH" ]]; then
  echo "ERROR: check out $BRANCH first." >&2; exit 2
fi
if [[ ! -f "$TASK" ]]; then echo "ERROR: run git pull first: $TASK missing" >&2; exit 2; fi
command -v codex >/dev/null || { echo "ERROR: codex CLI not found" >&2; exit 2; }
command -v python3 >/dev/null || { echo "ERROR: python3 not found" >&2; exit 2; }
git remote get-url origin >/dev/null
mkdir -p "$DIR" "work/physical_closure_2026"

# Source branch must have no pending tracked work: preserve user's work.
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "STOP: pre-existing tracked work detected. Preserve or commit it separately." >&2
  git status -sb
  exit 2
fi

LIMIT="${CODEX_MAX_ROUNDS:-5}"
if ! [[ "$LIMIT" =~ ^[1-9][0-9]*$ ]]; then
  echo "CODEX_MAX_ROUNDS must be a positive integer" >&2; exit 2
fi
LOGDIR="${CODEX_CLOSURE_LOGDIR:-work/physical_closure_2026/launcher_logs}"
mkdir -p "$LOGDIR"

# Allowed download hosts only, confined to sandboxed spawned commands.
# Official sources and package registries. No blanket * allow.
PROXY_DOMAINS='{ "arxiv.org" = "allow", "*.arxiv.org" = "allow", "inspirehep.net" = "allow", "*.inspirehep.net" = "allow", "github.com" = "allow", "*.github.com" = "allow", "githubusercontent.com" = "allow", "*.githubusercontent.com" = "allow", "pypi.org" = "allow", "*.pypi.org" = "allow", "files.pythonhosted.org" = "allow", "doi.org" = "allow", "zenodo.org" = "allow", "*.zenodo.org" = "allow", "hepdata.net" = "allow", "*.hepdata.net" = "allow", "cds.cern.ch" = "allow", "indico.cern.ch" = "allow", "inspirehep.net" = "allow", "journals.aps.org" = "allow", "link.springer.com" = "allow", "*.springer.com" = "allow", "sciencedirect.com" = "allow", "*.sciencedirect.com" = "allow", "*.cern.ch" = "allow" }'

# --ask-for-approval on-request: actions beyond sandbox still require a reviewer.
# Network is enabled but proxied to allowlisted hosts. git/.git stays protected.
CODEX_BASE=(codex
  -c 'sandbox_workspace_write.network_access=true'
  -c 'features.network_proxy.enabled=true'
  -c "features.network_proxy.domains=$PROXY_DOMAINS"
  exec --sandbox workspace-write --ask-for-approval on-request)

is_final() {
 [[ -s "$REPORT" && -s "$RESULT" && -s "$DIR/REPRODUCE.md" ]] || return 1
 python3 - "$RESULT" <<'PY'
import json, sys
try:
    x=json.load(open(sys.argv[1]))
    permitted={'GLOBAL_BENCHMARKS_VERIFIED','NO_VALIDATED_BENCHMARKS_YET','ALL_SAVED_CARDS_VALIDATED_FAIL'}
    assert x.get('status') in permitted
    assert x.get('final_artifacts_ready') is True
    assert all(k in x for k in ('join_count','pass_count','fail_count','unknown_count','sector_gates','source_hashes','tests','remaining_blockers'))
    assert all(isinstance(x[k],int) and x[k]>=0 for k in ('join_count','pass_count','fail_count','unknown_count'))
    assert x['pass_count']+x['fail_count']+x['unknown_count']==x['join_count']
except Exception:
    sys.exit(1)
PY
}

check_scope() {
  # Detect tracked changes outside our two allowlisted paths; do not stage them.
  local changed
  while IFS= read -r changed; do
    [[ -z "$changed" ]] && continue
    case "$changed" in
      "$DIR"/*|"$REPORT") ;;
      *) echo "STOP: out-of-scope tracked change: $changed" >&2; return 1 ;;
    esac
  done < <( { git diff --name-only; git diff --cached --name-only; } | sort -u )
  return 0
}

trusted_commit_push() {
  check_scope || return 6
  git diff --check || return 6
  git add -A -- "$DIR"
  if [[ -f "$REPORT" ]]; then git add -- "$REPORT"; fi
  git diff --cached --check || return 6
  local staged
  staged="$(git diff --cached --name-only)"
  if [[ -n "$staged" ]]; then
    # Reject accidentally staged paths even if they predated the task.
    while IFS= read -r p; do
      case "$p" in "$DIR"/*|"$REPORT") ;; *) echo "STOP: unsafe staged path $p" >&2; return 6;; esac
    done <<< "$staged"
    git diff --cached --stat
    git commit -m "Advance fixed-card Zee physical constraint closure with auditable evidence"
  fi
  # No force pushes, no unrelated branches, no user token interception.
  local remote_head local_head
  local_head="$(git rev-parse HEAD)"
  if ! git push origin "$BRANCH"; then
    echo "STOP: git push failed. Work is saved in local commits; retry manually after fixing Git." >&2
    return 5
  fi
  remote_head="$(git ls-remote origin "refs/heads/$BRANCH" | awk 'NR==1 {print $1}')"
  [[ -n "$remote_head" && "$remote_head" == "$local_head" ]] ||
    { echo "STOP: remote commit mismatch; don't rerun the physics." >&2; return 5; }
  echo "VERIFIED remote $BRANCH $remote_head"
}

# If a previous run produced the final science verdict, deliver it without
# rerunning any Codex physics; unrelated untracked logs do not block completion.
if is_final; then
  trusted_commit_push
  echo "SCIENTIFIC STUDY COMPLETE: $(python3 -c 'import json; print(json.load(open("research/full_constraints/physical_closure_2026/RESULT.json"))["status"])')"
  exit 0
fi

PROMPT="Read AGENTS.md and $TASK. EXECUTE the complete fixed-card closure task; do not rewrite past modules or redo completed LFV/cascade/vacuum pilots. Network commands only to official allowlisted public hosts, save downloads under ignored work/physical_closure_2026. Complete source-specific LFV omitted-amplitude coverage, B uncertainty/one-state controls, Higgs completeness, and a conservative joined-card global gate. Update $DIR/WORK_CHECKPOINT.md and the required reports/tests; mark physical UNKNOWN honestly. Do NOT git commit/push: the externally authorized runner performs safe scoped Git delivery. Do not claim work is done until $RESULT has a defensible final status and supporting artifacts."
for ((n=1;n<=LIMIT;n++)); do
  echo "===== Codex scientific round $n/$LIMIT ====="
  set +e
  if (( n==1 )); then
    "${CODEX_BASE[@]}" "$PROMPT" 2>&1 | tee "$LOGDIR/round_$n.log"
  else
    "${CODEX_BASE[@]}" resume --last \
      "CONTINUE the SAME $TASK from $DIR/WORK_CHECKPOINT.md. Do not stop after a plan or a partial source list. Finish the remaining physics validation and conservative joined-card report, then write $RESULT final_artifacts_ready=true only when evidence and tests exist. Do not commit: wrapper handles scoped commit/push. A justified NO_VALIDATED_BENCHMARKS_YET is a real final result." \
      2>&1 | tee "$LOGDIR/round_$n.log"
  fi
  rc="${PIPESTATUS[0]}"
  set -e
  if [[ "$rc" -ne 0 ]]; then
    echo "STOP: Codex exit $rc; no automatic retry of quota/auth/permissions failures." >&2
    echo "Logs: $LOGDIR/round_$n.log" >&2
    exit "$rc"
  fi
  trusted_commit_push || exit $?
  if is_final; then
    echo "SUCCESS: final physical-constraint closure and verified remote Git commit"
    python3 -c 'import json; print(json.load(open("research/full_constraints/physical_closure_2026/RESULT.json"))["status"])'
    git rev-parse HEAD
    exit 0
  fi
done
echo "INCOMPLETE: $LIMIT rounds reached. Results and checkpoints have been committed/pushed; no false completion." >&2
echo "To resume, run this script again after checking WORK_CHECKPOINT.md. Do not increase rounds blindly." >&2
exit 3
