# NuFIT 6.1 scoped neutrino compatibility — validated 13 November 2026

## Physics prescription

Use official 2025 NuFIT 6.1 **IC24/TByes** as primary and **IC23/TBoff** as
robustness alternative. For each neutrino ordering, evaluate **all six original
single-variable 1D profiled Δχ² curves**, requiring each value minus its
ordering-local minimum to be <= **9**. Independently evaluate the published
**3D T23/DMA/DCP profile**, requiring the value minus its ordering-local minimum
to be <= **14.1562525005409** (the nominal χ² three-dof 99.73% quantile).

The intersection is a **pragmatic oscillation-data compatibility screen**,
NOT a calibrated simultaneous six-dimensional confidence region, and the 3D
cut has the usual Wilks/periodic-CP caveat. None of the seven projections is
summed with another. The global IO ordering penalty is always retained in
absolute results but **not** automatically used to veto IO; local comparisons
subtract the archive's IO offset of 5.908214 for IC24 (1.485872 for IC23).
For observations outside the published grid, return SCOPED_UNKNOWN rather than
extrapolate. NO and IO use Δm31² and Δm32² respectively.

The **full Zee one-loop reconstruction**, masses/PMNS, and Yukawas are computed
by unchanged `module2.interface.evaluate` in the source-locked replay. The
oscillation filter alone does not establish neutrino mass generation.
The lightest mass and Majorana phases are user-specified nuisance assumptions,
not oscillation constraints. Cosmology and 0νββ are **not** incorporated; the
user should present those as separately scoped observables if adopted.

## Real-grid execution actually performed

The independent production Module2 archive reader previously passed 32 real-grid
checks on the four original user-uploaded archives. The NEW cached production
filter was also executed locally against the uploaded original IC24 and IC23
archives (matching the hashes recorded in verify.py). The real-grid NO/IO
summary targets were independently reconstructed from the pinned D11B secondary
oscillation numbers; their full model card hashes were previously verified by
the user via `saved_targets.py` (four PASS outputs). The new script
`replay_frozen.py` reruns the full Module2 model and hashes and is provided for
one additional local source-locked receipt; **that new four-card replay has
not been executed in the development container**.

| Mode | Ordering | Max of 6 local 1D Δχ² | Local 3D Δχ² | Absolute 3D Δχ² | Scoped filter |
|---|---|---:|---:|---:|---|
| IC24 primary | NO | 0.007756825317 | 0.004925922925 | 0.004925922925 | SCOPED_PASS |
| IC24 primary | IO | 0.007934626057 | 0.008665105952 | 5.916879105952 | SCOPED_PASS |
| IC23 alternative | NO | 0.446578788000 | 0.461046890573 | 0.461046890573 | SCOPED_PASS |
| IC23 alternative | IO | 0.406197600000 | 0.455474747456 | 1.941346747456 | SCOPED_PASS |

The D7 and F13 frozen cards use identical oscillation targets within each
ordering; the four reported model targets therefore map onto the two unique
NO/IO rows per dataset. This says nothing about independent scalar/Yukawa
acceptance. Missing LFV, B, Higgs, quark FCNC and vacuum gates remain separate.

## Exact replays on user's Zee checkout

```bash
cd ~/zee
git fetch origin
git switch research/nufit61-native-20261113
git pull --ff-only origin research/nufit61-native-20261113

# Synthetic tests + actual archive test (four unittest checks):
NUFIT61_ARCHIVE_DIR="$PWD/NuFIT" \
  python3 -m unittest research.full_constraints.nufit61_native_2026.test_scoped_compatibility -v

# Recompute all four original one-loop Zee Yukawa reconstructions, compare
# SHA256 outputs to frozen receipts, then apply seven native NuFIT profiles.
python3 -m research.full_constraints.nufit61_native_2026.replay_frozen \
    --archive-dir NuFIT --selection IC24 \
    --output /tmp/nufit61_frozen_final.json

# Optional alternate atmospheric-data prescription:
python3 -m research.full_constraints.nufit61_native_2026.replay_frozen \
    --archive-dir NuFIT --selection IC23 \
    --output /tmp/nufit61_frozen_IC23.json
```

For future scanner integration, **instantiate exactly once per ordering**:

```python
from research.full_constraints.nufit61_native_2026.scoped_compatibility import NuFIT61Compatibility
no_filter = NuFIT61Compatibility('NuFIT','NO','IC24')
io_filter = NuFIT61Compatibility('NuFIT','IO','IC24')
result = (no_filter if obs['ordering']=='NO' else io_filter).evaluate(obs)
assert result['global_zee_acceptance'] is None
```

Do not edit frozen scan or source receipts until all other model-wide gates have
been validated. The filter only labels `SCOPED_PASS/FAIL/UNKNOWN` under the
explicitly published approximation.
