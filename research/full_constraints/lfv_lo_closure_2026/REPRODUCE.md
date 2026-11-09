# Reproduction

From the repository root, with numpy, scipy, gfortran and g++ available:

```sh
PYTHONPATH=. python3 research/full_constraints/lfv_lo_closure_2026/adapter.py
PYTHONPATH=.:research/full_constraints/lfv_lo_closure_2026 python3 research/full_constraints/lfv_lo_closure_2026/nuclear_control.py
PYTHONPATH=.:research/full_constraints/lfv_lo_closure_2026 python3 -m unittest research/full_constraints/lfv_lo_closure_2026/test_adapter.py research/full_constraints/lfv_lo_closure_2026/test_closure.py -v
git diff --check
```

The first command reuses existing `NUMERICAL.json` and checks the hashes of the pinned generated source files before compiling a temporary extracted block. The second checks the pinned nuclear source files and compiles temporary controls; it requires the absolute paths in the frozen `lfv/SOURCE_TO_CODE_SOURCES.json` to be available. Temporary build files live inside this directory and are removed automatically. No prior provenance or two-loop calculation is rerun. `BENCHMARK_LFV.csv` blank physical rates mean null, not zero.
