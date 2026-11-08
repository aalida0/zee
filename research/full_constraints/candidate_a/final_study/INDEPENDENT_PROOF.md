# Independent certificate components: preliminary

The standalone `verify_independent.py` reads the saved binary64 scalar coefficients and converts each exactly to a rational. It imports no D10 module or cached pivots. It constructs the symmetric invariant quartic pencil and uses exact SymPy leading principal determinants (Sylvester criterion), rather than the archived LDL implementation. A high-precision numerical root is only a proposed center: exact rational interval bounds on the Jacobian show that the preconditioned fixed-point map sends a closed radius-10^-30 GeV box strictly into itself and is a contraction. Thus the root exists and is unique in that box. The requested location is checked to 10^-8 GeV. Exact interval margins at this root are strictly positive. Rational data are in CERTIFICATES; run the script from any directory to regenerate them.

| input | epsilon | minimum pivot | doublet margin GeV² | singlet margin GeV² |
|---|---:|---:|---:|---:|
| D7 | 1650627/250000 | 0.148668473145 | 71557.9472 | 90326.2920 |
| F13_1330 | 1232051/200000 | 0.104770108173 | 482334.3420 | 249954.6974 |

These are independently checked components of the existing sufficient certificate, **not yet an independent all-fields proof**: the independent full SARAH polynomial derivation, square-completion identity, phase/boundary checks and negative proofs remain unfinished. The JSON's source hash is the value recorded in the original input receipt, not yet independently verified by the checker. Seven falsifier/unit tests pass (negative quartic, large cubic, invalid epsilon, wrong requested vev, tadpole sign, invalid zero-radius box and valid control). The checker compares the entire proof object with independently recomputed exact data, but a deliberate saved-pivot corruption test is still outstanding. No scientific GO or NO_GO follows from this partial replay.

`verify_symbolic_identity.py` separately checks the complete invariant square-completion equality with neutral tadpoles and proves the complex doublet Gram determinant identity symbolically. This confirms the algebra for the written invariant potential; the independent term-by-term connection from the pinned SARAH source and full ten-field derivative comparisons remain to be completed.
