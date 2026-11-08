# Numerical versus rigorous methods

On each of the 93 declared potential cards, `finite_start.py` performed 512 deterministic nested starts (NumPy default_rng seed 0…511, all cards use same seeds). It minimizes the source-matched tree potential over the gauge-reduced phase-minimized orbit: three nonnegative norm roots, doublet overlap angle and relative neutral phase. The charged-singlet phase is minimized analytically. This represents every orbit including zero-norm and determinant boundaries, but the optimizer searches a finite norm-root box [0,12] in units of v and is not exhaustive. The 2021 paper's gradient-descent implementation was not reproduced; ours is a separately described baseline. Results and times are in FINITE_START.jsonl. Re-running it resumes already completed cards: delete or move that output only when deliberately starting a fresh run.

| family | points | exact stable | exact deeper | unknown | numerical deeper 32/128/512 | elapsed all 512 |
|---|---:|---:|---:|---:|---:|---:|
| P2 | 31 | 0 | 3 | 28 | 3/3/3 | 21.58 s |
| D7 | 31 | 31 | 0 | 0 | 0/0/0 | 11.37 s |
| F13_1330 | 31 | 31 | 0 | 0 | 0/0/0 | 27.36 s |
| total | 93 | 62 | 3 | 28 | 3/3/3 | 60.31 s |

All 93 pass the floating full EW transverse-Hessian positivity, parent BFB and parent unitarity tests. The quartics are identical along each path, so their archived parent quartic gates are reused; EWPO is not reused. Each of the three numerical P2 discoveries is independently verified by the rational fixed-field witness; finite optimizer termination and its local stationary values are not the proof. No verified deeper case was missed by 32 starts in this sample. Of 90 cases with no numerical deeper field, 28/90 remain mathematically UNKNOWN; a user who treats numerical absence as proof would have unwarranted confidence in those 28 cases. This is not an observed false-negative rate: their actual vacuum status is unknown. The 62 exact certificates provide stronger assurance of stability than finite-start non-discovery but do not exclude new locally passing points on these paths. Runtime is host-specific and the three nested budgets are not independent experiments.
