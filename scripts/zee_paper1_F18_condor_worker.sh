#!/usr/bin/env bash
# One F18 benchmark per Condor job; self-contained transferred input sandbox.
# All CPU-intensive madevent work is in HTCondor scratch, not shared /home.
set -Eeuo pipefail
case_name="${1:-}"
case "$case_name" in
  F13_heavy_0001330|F13_heavy_0000981|F13_heavy_0001003) ;;
  *) echo "F18_CONDOR_BAD_CANDIDATE $case_name" >&2;exit 2;;
esac
scratch="${_CONDOR_SCRATCH_DIR:-$PWD}"
cd "$scratch"
ncores="${F18_REQUEST_CPUS:-2}"
[[ "$ncores" =~ ^[1-9][0-9]*$ && "$ncores" -le 64 ]] || {
 echo "F18_CONDOR_INVALID_CPUS $ncores" >&2; exit 2; }
export OMP_NUM_THREADS="$ncores"
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1
mkdir -p "export/$case_name"
started_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
pack_results() {
  rc=$?
  trap - EXIT
  set +e
  dest="export/$case_name"
  mkdir -p "$dest"
  printf '%s\n' "$rc" > "$dest/worker_exit_code.txt"
  printf '%s\n' "$started_utc" > "$dest/worker_started_utc.txt"
  date -u +%Y-%m-%dT%H:%M:%SZ > "$dest/worker_finished_utc.txt"
  for leaf in summary.json initial_manifest.json three_benchmarks_summary.csv; do
    [[ ! -f "F18_job_output/$leaf" ]] || cp -p "F18_job_output/$leaf" "$dest/"
  done
  for leaf in two_body.slha two_plus_three_body.slha \
              validated_model_LO_widths.json F18_MadWidth_input_with_derived_MW.slha; do
    [[ ! -f "F18_job_output/$case_name/$leaf" ]] ||
      cp -p "F18_job_output/$case_name/$leaf" "$dest/"
  done
  for stage in stage_2body stage_2plus3body; do
    [[ -d "F18_job_output/$case_name/$stage" ]] || continue
    mkdir -p "$dest/$stage"
    for leaf in madwidth.log compute_widths.mg5 mg5_diagnostic.json MG5_debug; do
      [[ ! -f "F18_job_output/$case_name/$stage/$leaf" ]] ||
        cp -p "F18_job_output/$case_name/$stage/$leaf" "$dest/$stage/"
    done
  done
  # HTCondor returns this one unique result archive to the submit host.
  tar -czf "F18_result_${case_name}.tar.gz" -C export "$case_name"
  echo "F18_CONDOR_RESULT_TARBALL F18_result_${case_name}.tar.gz"
  echo "F18_CONDOR_JOB_EXIT_CODE $rc"
  exit "$rc"
}
trap pack_results EXIT

command -v python3 >/dev/null || { echo "F18_CONDOR_MISSING_PYTHON" >&2;exit 2; }
command -v gfortran >/dev/null || { echo "F18_CONDOR_MISSING_GFORTRAN" >&2;exit 2; }
command -v make >/dev/null || { echo "F18_CONDOR_MISSING_MAKE" >&2;exit 2; }
python3 -c 'import numpy, scipy; print("F18_CONDOR_PYTHON_DEPS_PASS")'
for file in F18_source_bundle.tar.gz F18_scripts_bundle.tar.gz F18_mg5_bundle.tar.gz; do
  [[ -f "$file" ]] || { echo "F18_CONDOR_MISSING_BUNDLE $file" >&2;exit 2; }
done
mkdir -p F16_SOURCE
tar -xzf F18_source_bundle.tar.gz -C F16_SOURCE
tar -xzf F18_scripts_bundle.tar.gz
tar -xzf F18_mg5_bundle.tar.gz
[[ -f "MG5_aMC/bin/mg5_aMC" ]] || {
  echo "F18_CONDOR_MG5_BINARY_MISSING_AFTER_UNPACK" >&2;exit 2; }
chmod u+x "MG5_aMC/bin/mg5_aMC"
mkdir -p F18_job_output
echo "F18_CONDOR_START case=$case_name cores=$ncores host=$(hostname) scratch=$scratch"
python3 -u scripts/zee_paper1_F18_complete_madwidth_campaign.py \
  --f16-dir "$scratch/F16_SOURCE" \
  --f17d-dir "$scratch/F16_SOURCE/F17d_original_UFO_source_matched_TEST_CARDS_20261023T113206Z" \
  --f17e-report "$scratch/F16_SOURCE/F17e_real_UFO_amplitude_gate_20261023T115044Z.json" \
  --f17f-dir "$scratch/F16_SOURCE/F17f_real_UFO_unitary_complex_CKM_20261023T120345Z" \
  --mg5-bin "$scratch/MG5_aMC/bin/mg5_aMC" \
  --only-case "$case_name" \
  --nb-core "$ncores" \
  --output "$scratch/F18_job_output"
echo "F18_CONDOR_BENCHMARK_COMPLETED $case_name"
