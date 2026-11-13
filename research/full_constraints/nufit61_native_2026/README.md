# NuFIT 6.1 authentic-archive validation (2026-11-13)

## Scope and provenance

NuFIT 6.1 release notes: https://www.nu-fit.org/sites/default/files/v61.release-notes.pdf  
NuFIT results: https://www.nu-fit.org/?q=node%2F309

The four official-format `.txt.xz` archives were **provided by the user** and inspected locally.
Each SHA-256 below identifies those exact input bytes. Their official upstream checksum
was not independently authenticated. Raw 3.9-MB archives are intentionally **not** committed;
keep them outside the repository and point the verifier to their local directory.

| Archive | SHA-256 | min Δχ² |
|---|---|---:|
| `v61.release-TBoff-NO.txt.xz` | `58b113927c13f55925558e1ef0a598b357a237cde5c466b9f660cc08569970f6` | 0 |
| `v61.release-TBoff-IO.txt.xz` | `6e14ce52503d053ce4d8d0171ffecae24c2dd3dc41be99c3c5c952f321331f16` | 1.485872 |
| `v61.release-TByes-NO.txt.xz` | `c74bd6df84297a8429cd3b9e1239751cd0762756f1ec0c2a31248d78570b26e4` | 0 |
| `v61.release-TByes-IO.txt.xz` | `d92fbd1886a85738080a394a6af513ec1ac49d5e474a6517cada0c2c6f3b96b2` | 5.908214 |

**Independent local validation: PASS** for all 4 archives, 22/22 complete Cartesian
projections per archive, 1,450,245 numerical rows per archive, no repeated grid
coordinates or nonfinite entries, correct 3D shape (101,165,73), equal DCP
phase-boundary endpoints, and consistent global ordering offsets across all projections.

The production `module2.nufit` already supports NuFIT 6.1 and preserves its Δχ²
offsets. **Its real-archive backend test is provided but has not yet been executed**
by the local independent validation above. Use the command below.

## Reproduce on local Zee checkout

Place the **unmodified** four uploaded archives together under `/path/to/archives/`,
then run from the repository root:

```bash
git switch research/nufit61-native-20261113
python3 -m research.full_constraints.nufit61_native_2026.verify \
    --archive-dir /path/to/archives \
    --backend \
    --output /tmp/nufit61_verified.json
```

Add `--full-3d` for a memory-intensive test of the production Module2 3D
reader on all four archives. This can use substantial RAM and repeated
decompression; it is optional, unlike the independent 3D grid inspection.

NuFIT native axes are `T12,T13,T23=sin²(theta)`,
`DMS=log10(Δm21²/eV²)`, `DMA=Δm3ℓ²/(10⁻³ eV²)`,
and `DCP=degrees` (archived phase range −180° to +180°).
The NO atmospheric splitting uses Δm31² and IO uses Δm32².
The existing Module2 `compare()` handles these conversions.

**Do not:** add overlapping profiled projections, interpret a set of projections
as a joint six-parameter likelihood, remove the IO offset, replace the frozen
NO/IO cards silently, or assign `global_zee_acceptance=PASS`. This integration
does not close B physics, LFV, Higgs, or vacuum constraints.

## Scientific next step

After `--backend` passes, rerun only the saved NO/IO neutrino comparison or
reconstruction inputs with an explicitly selected native NuFIT 6.1 dataset.
Use one chosen projection for each diagnostic and retain the old NuFIT 6.0
outputs for reproducibility. Do not trigger the large final scan.
