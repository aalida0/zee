# B→Xsγ independent backend pilot

Bounded investigation on `research/zee-bsgamma-rate-validation`.
**DIAGNOSTIC_ONLY; full Zee rate accuracy and 2026 exclusion readiness UNKNOWN.**
See [RESULT.md](RESULT.md), [BACKENDS.md](BACKENDS.md), [results.json](results.json)
and [inventory.json](inventory.json). Modules 0–14 are read-only.

From repository root, on Linux x86_64 with Python **3.10.12**:

```bash
mkdir -p research/bsgamma_rate_validation/local
python3 -m venv research/bsgamma_rate_validation/local/venv
research/bsgamma_rate_validation/local/venv/bin/pip install -r research/bsgamma_rate_validation/requirements.lock
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/pilot.py
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s research/bsgamma_rate_validation -p 'test_*.py' -v
git diff --check
```

All runtime packages, including transitive dependencies, are version-locked.
`particle==0.25.4` is necessary: the newer unconstrained release lacks the
`particle2022.csv` loaded by flavio 2.7.1. No package source was patched.
EOS uses the PyPI manylinux CPython 3.10 wheel, release **1.0.21**. Upstream
**v1.1** is newer and was inspected at source level only; its GitHub release has
no binary assets and it was not installed/built in this bounded pilot.
Do not equate the executed EOS wheel with the current upstream release.

`pilot.py` imports the existing `scripts/zee_module5_bmu_nlo.py` unchanged.
The input card records matching top/alpha_s from flavio defaults at 160 GeV,
plus the complete overrides for EOS's upstream regression. Default parameter
sets are authenticated by hashes in the results; releases supply their data.
The flavio default parameter hash is checked before executing the pilot.
Numerical digits describe reproducibility, not theoretical precision.

The pilot deliberately selects C7/C8 for flavio and records the omitted C4.
The rate function **rejects** a C4 key. LO and LO+NLO denote matching inputs;
they are not perturbative-order settings for the backend rate. The latter
combination is a matching sensitivity diagnostic with leading-log NP running.
Never use these records as full NLO Zee predictions or D14 acceptance filters.

The independent `provenance.py` refreshes source-byte hashes and interface
failures. It additionally requires the source files under `local/` listed in
`inventory.json`: download each `external_sources` URL to `local/<key>` first.
No third-party source/binary is committed. Licenses inspected: flavio/wilson
MIT, EOS GPL-2.0, HEPfit GPL-3.0-or-later. This work calls installed packages;
no rate routine is copied. Numerical regression input cards retain attribution
to their upstream source. Preserve upstream terms if distributing packages.

The 64-draw seeded SM uncertainty call tests the public uncertainty interface.
It is not a precision uncertainty estimate or a Zee covariance model. The
committed central predictions and focused tests do not require network access.
