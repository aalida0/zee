# Gate A1J — reproducible SuperIso 5.0 AF bootstrap

**Scope:** toolchain setup and an SM smoke test only. No physical Zee BR(B→Xs gamma), exclusion, or Type-II two-charged matching is claimed.

Official download: https://superiso.in2p3.fr/download/. The page lists **SuperIso 5.0 (23 November 2025)**, with `predict.c` and `scan_coeffs.c`. Download the flavour-only **SuperIso**, **not SuperIso Relic**. The direct archive link is presented as a form/input and was not independently verified, so **do not invent or hard-code a tarball URL**. See the older SuperIso manual for `make`/`make sm`: https://superiso.in2p3.fr/superiso4.1.pdf. The standard `thdm.x` interface can require **2HDMC**; first inspect v5's actual Makefile.

## 1. Download and extract official sources

On the ATLAS AF:

```bash
mkdir -p /home/aalida/opt/zee_tools
```

Download the SuperIso v5.0 archive from the official page in your laptop browser. From a terminal **on the laptop**, copy the file (substitute its actual filename):

```bash
scp ~/Downloads/<OFFICIAL_ARCHIVE_FILENAME> \
  aalida@login01.af.uchicago.edu:/home/aalida/opt/zee_tools/superiso-source.tar.gz
```

Alternatively, when the AF can access the official site and you have copied the *actual archive link*, use `curl -fL "<OFFICIAL_ARCHIVE_LINK>" -o /home/aalida/opt/zee_tools/superiso-source.tar.gz`. Do not mistake an HTML page for the archive.

Back on the AF:

```bash
cd /home/aalida/opt/zee_tools
file superiso-source.tar.gz
sha256sum superiso-source.tar.gz
tar -tzf superiso-source.tar.gz | head -n 12
# Confirm archive contents and paths are sensible and from the vendor.
tar -xzf superiso-source.tar.gz
find /home/aalida/opt/zee_tools -maxdepth 3 -name Makefile -print
```

Identify the extracted directory containing both `Makefile` and `src/`. Its exact name is not assumed.

## 2. Build and run the SM control

```bash
cd /home/aalida/zee
git fetch origin gateA1j-superiso-af-bootstrap
git switch gateA1j-superiso-af-bootstrap

python3 -m unittest discover -s tests \
  -p 'test_gateA1j_build_superiso.py' -v

bash scripts/gateA1j_build_superiso.sh \
  /home/aalida/opt/zee_tools/<EXTRACTED_DIRECTORY> \
  work/gateA1j_superiso_build 2
```

The wrapper invokes `make -j 2`, `make sm`, and `./sm.x`, and **optionally** attempts to build `scan_coeffs` and `predict`. Source files are not patched, no external site is contacted, and no root privileges are required. Optional target failures are reported without masking a successful SM baseline.

It records:

- `work/gateA1j_superiso_build/result.json`: build and SM-run statuses.
- `sm_output.log`: actual Standard Model observables, **not** Zee predictions.
- `make_library.log`, `make_sm.log`, `make_scan_coeffs.log`, `make_predict.log`.
- `source_sha256.txt`, `toolchain.txt`: source and compiler provenance.

Inspect the logs:

```bash
cat work/gateA1j_superiso_build/result.json
grep -i -E 'b.*s.*gamma|b.*x.*gamma|BR.*s|BR.*gamma' \
  work/gateA1j_superiso_build/sm_output.log | head -n 30
```

If the core build fails, copy `result.json` and the last 50 lines of the first failing `make_*.log`. First ensure the SM output convention (including the photon-energy cut) is documented.

## 3. Next: model-level matching, not averaging BRs

SuperIso's standard 2HDM driver assumes **one** charged-Higgs mass and may require a separate 2HDMC installation. Our Zee model has *two* charged mass eigenstates, with distinct doublet projections and perturbative Wilson matching. Validate the SuperIso **SM**, then its **single-charged Type-II** limits, before adding both charged states at the LO/NLO/NNLO matching and RG-evolution level.

Never average two single-2HDM final branching ratios or substitute an effective mass obtained by matching LO `C7` alone. The model-level evaluation must use a consistent scheme and current experimental/theory uncertainties.

**Gate A1J success means SuperIso is built and its SM driver runs—not that the Zee benchmark has passed (B\to X_s\gamma).**
