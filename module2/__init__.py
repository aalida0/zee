"""General Zee neutrino sector 1.0.0; no global Zee acceptance."""
from .core import forward, loop_kernel, null_cone, solve_fixed_f, yukawa_rotation
from .observables import takagi, observables

__version__ = '1.0.0'

def evaluate(data):
    """Evaluate one versioned Module 2 JSON object using the public API."""
    from .interface import evaluate as _evaluate
    return _evaluate(data)
