# LFV practical implementation: work in progress

2026-11-07. Branch `research/zee-full-constraints`, starting HEAD `302bb54ac1a70c07d7f47c8287e1dc5edacde28b`. This is an incomplete dependency-stage record, not a physical LFV result.

In new scratch directory `/tmp/zee-lfv-practical-20261107`, the official `https://feynarts.de/FeynArts-3.12.tar.gz` downloaded and extracted; SHA-256 `190cb5a2ecbbe35136f218d462b03731c6b797ecf65f088affc89ea01ef5784a`. Mathematica `/usr/local/bin/math` independently loaded it after appending the extracted directory to `$Path`, printing `FeynArts 3.12 (27 Mar 2025)` and `MemberQ[$Packages,"FeynArts`"] = True`. The same kernel independently loaded SARAH 4.15.4 from `/home/amine/.Mathematica/Applications`, with package membership true. The date in the package banner differs from the release date quoted in the earlier audit; the banner is recorded verbatim rather than interpreted as a release date.

The official FormCalc 9.10 archive download was still in progress at the time of this record. Its partial file must not be used or hashed as a release. No successful FormCalc load, FlexibleSUSY configure, Zee adapter, generation, Wilson comparison, independent rate comparison, omission bound, or new branching ratio is claimed. The previous configure failed at FeynArts before Zee generation; that failure is not evidence of a Zee incompatibility.

The existing pinned FlexibleSUSY source in `/tmp/lfv-source-work` filters `FeynArts`V` loop fields in selected penguin and box topologies in both `meta/Observables/BrLTo3L/NPointFunctions.m` and `meta/Observables/LToLConversion/NPointFunctions.m` (lines 21–30). The physical impact and coverage by separate photon form factors remain untested. A green build would not by itself establish complete gauge coverage.

All four requested observables on all four cards remain `UNKNOWN` for physical exclusion under the task's materiality standard. Existing partial results are documented in `lfv/LFV_FIXED_CARD_RESULTS.json`; they are not promoted to validated complete rates. No conversion rates from the unpatched FlavorKit routine are used. Full LFV remains blocked; `global_acceptance=null`. No new points or scans were generated.

Next: finish and integrity-check the official FormCalc download, record its complete SHA-256 and independent kernel load, configure the pinned generator in scratch, and perform the single bounded adapter attempt and fixed-card comparison specified in `LFV_PRACTICAL_APPROXIMATION_TASK.md`.
