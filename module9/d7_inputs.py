"""D7 input contract: frozen NO target/family, varied scalar inputs only."""
import copy
import hashlib
from pathlib import Path

from module2.interface import canonical_hash, scalar_input, strict_loads, validate_schema
from module3.interface import validate, foundations

SEED_PATH = Path(__file__).resolve().parents[1] / "module3/example.json"
SEED_SHA256 = "6a55f774041a9d5e06bd6ea30a628bfcf5c840af0ddff30bce5f692a551c2915"
VARIED = ("mH1", "mH2", "mh2", "ma", "beta", "gamma", "alpha", "m12sq")


def seed_input(raw=None):
    raw = SEED_PATH.read_bytes() if raw is None else raw
    if hashlib.sha256(raw).hexdigest() != SEED_SHA256:
        raise ValueError("D7 requires the pinned illustrative NO source bytes")
    return strict_loads(raw.decode())


def validate_point(point):
    validate(point, "input.schema.json")
    inp = point["module2_input"]
    validate_schema(inp, "input.schema.json")
    if inp["mode"] != "inverse" or inp["ordering"] != "NO" or "dataset" in inp:
        raise ValueError("D7 requires NO inverse input with no oscillation dataset")
    wrapper = inp["scalar"]
    if wrapper["kind"] != "module1_input":
        raise ValueError("D7 requires a full SHA-bound Module1 input")
    physical, _ = scalar_input(wrapper)
    identity = point["benchmark_id"]
    if not identity == inp["benchmark_id"] == wrapper["record"]["benchmark_id"]:
        raise ValueError("Module3/2/1 benchmark identity mismatch")
    if not physical["mH2"] > physical["mH1"] + wrapper["record"]["electroweak"]["mZ"]:
        raise ValueError("D7 requires ordered charged masses and an open H1 Z cascade")
    expected = copy.deepcopy(seed_input())
    expected["benchmark_id"] = identity
    expected["module2_input"]["benchmark_id"] = identity
    bound = expected["module2_input"]["scalar"]
    bound["record"]["benchmark_id"] = identity
    bound["record"]["physical"].update({k: physical[k] for k in VARIED})
    bound["sha256"] = canonical_hash(bound["record"])
    if canonical_hash(point) != canonical_hash(expected):
        raise ValueError("D7 target, inverse family or frozen scalar inputs changed")
    foundations()
    return physical
