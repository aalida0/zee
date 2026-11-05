# Scoped gauge-completion ledger

**Overall: BLOCKED_ZEE_TWO_LOOP_COMPLETION.** No full Wilson coefficient or
full branching ratio is exposed. The current tensor tests do not replace
full W/Goldstone/ghost/LSZ matching.

| Required class/check | Evidence | State |
|---|---|---|
| Frozen scalar one loop / D15 crossing | existing validated source, reused unchanged | PASS in frozen approximation |
| Corrected full general-2HDM common limit | existing 39 complex comparisons | preserved, not rerun |
| Original authors' HW bug | historic expected failure and original source | preserved |
| Mixed G,h/H/A, Z, photon, AZ, G0 sources | 32 native queries, 64 checks, two spectra | PASS |
| Physical A trilinears | full rotation and native queries; zero physical block, nonzero A-G-H | model-specific zero proved |
| Mixed scalar-current photon Ward / UV | both triangles + AZ, pole sum 1+1−2 | PASS |
| Mixed current off-shell Z/G0 identity | independently integrated nonzero longitudinal remainder | PASS |
| Mixed real-photon Z/G0 projection | unprojected complex null-photon tensors, ξ=.5,1,3,7 | PASS for current subset |
| Mixed masters / complex L,R | independent radial and bounded parameters; both strict limits | current subset PASS |
| Charged basis / phases / reverse / null / decoupling | focused mixed-HZ tests | PASS for current subset |
| Entire mixed potential Z sector | neutral two-point/reducible assignment and A-G-H sector incomplete | OPEN; no full mixed-class acceptance |
| Neutral fermion Zγ | nine species; native current transfer, radial quadrature, signed complex comparison | common-class PASS |
| Complete Zee kinetic W aggregate | new d-dimensional WWW outer Pauli projection, TARCER IBP, exact pole cancellation and independent finite masters | topology-only; full charged/BRST/LSZ sum OPEN |
| Zee potential HW | unequal-mass physical currents and Goldstone parents | NOT CALCULATED |
| Charged-fermion W | general charged mixing, matched complete aggregate | NOT CALCULATED |
| Quadratic FD, mν=0 | fermion-number spurion argument includes gauge/reducible insertions | ZERO in specified Yukawa truncation |
| Quadratic F†F | native W-neutrino subgraph now calculated at general ξ; pole −ξ and finite nonlocal part | full dipole gauge/counterterm sum MISSING |
| Full Zee UV/ST/Ward / ξ, both L,R | required classes missing | NOT EVALUATED |
| Full Zee amplitudes / full BR | null in CLI | UNAVAILABLE |
| Opt-in D14 overlay | master task requires scoped completion first | not produced |

The 70 coherent rows per channel contain no whole-author-result addition.
Unknown contributions remain null; no absent rate is interpreted as zero.
The original `matching.py`, all old evidence, Modules0–14 and D15 are unchanged.
Scalar constraint failures of amplitude fixtures remain separate from these
amplitude validation states. These results imply no phenomenological exclusion.

New integrated parent: [W_OUTER_PARENT_DERIVATION.md](W_OUTER_PARENT_DERIVATION.md), `w_outer_evidence.json`. This advances one ξW=1 topology and its Hermitian reverse; it does not change any full-amplitude gate.

Further calculated pieces: `gww_outer_evidence.json` retains the next native
parent's **nonzero 1/(4ε) subdivergence**, with independent finite
mass-difference checks. `remaining_subgraph_evidence.json` records the
general-Rξ neutrino two-point function and proved charged-scalar-only A-Z/G0
mixing zeros. Full reducible and F†F gates remain open. See
[REMAINING_SUBGRAPH_DERIVATION.md](REMAINING_SUBGRAPH_DERIVATION.md).
