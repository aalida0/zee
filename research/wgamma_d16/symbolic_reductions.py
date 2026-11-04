"""Small exact mixing identities, independent of any loop implementation."""
import sympy as s


def reductions():
    delta, gamma, r2, mh2, mH2 = s.symbols('delta gamma r2 mh2 mH2', real=True)
    L, R = s.symbols('L R', complex=True)
    kappa = [s.cos(delta), s.sin(delta)]
    yukawa = [-s.sin(delta), s.cos(delta)]
    neutral = [s.trigsimp(sum(k*y*x for k, y in zip(kappa, yukawa))) for x in (L, R)]
    # Explicit scalar inverse propagators; no mass degeneracy assumption.
    C = [s.trigsimp(sum(k*y*x*(r2-m2)/(r2-m2)
                       for k, y, m2 in zip(kappa, yukawa, (mh2, mH2)))) for x in (L, R)]
    d, singlet = [s.cos(gamma), -s.sin(gamma)], [s.sin(gamma), s.cos(gamma)]
    charged = dict(doublet_norm=s.trigsimp(sum(a*a for a in d)),
                   singlet_norm=s.trigsimp(sum(a*a for a in singlet)),
                   unweighted_doublet_singlet=s.trigsimp(sum(a*b for a, b in zip(d, singlet))))
    assert neutral == [0, 0] and C == [0, 0]
    assert list(charged.values()) == [1, 1, 0]
    return dict(status='PASS', neutral_chiral_sums=list(map(str, neutral)),
                C_after_inverse_propagator_cancellation=list(map(str, C)),
                charged_unweighted_sums={k: str(v) for k, v in charged.items()},
                limitation='Unweighted charged sums do not justify cancellation of mass-dependent charged kernels')


if __name__ == '__main__':
    import json
    print(json.dumps(reductions(), indent=2))
