#!/usr/bin/env python3
"""Write a *diagnostic* Yang/Wu Zee-Type-II LO SLHA card from Gate-6 scalar point.

Charged lepton Yukawas: Type-II; antisymmetric Zee lepton couplings f_ab=0.
THIS MEANS NO RADIATIVE ZEE NEUTRINO MASSES. NOT A PHYSICAL BENCHMARK.
Never interpret unchanged DECAY entries as physical widths or BRs.
"""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from gate7_map_p2_to_yangwu import map_point

BLOCK_RE = re.compile(r"^\s*block\s+([A-Za-z0-9_]+)(?:\s|$)", re.I)
VALUE_RE = re.compile(
    r"^(\s*)(\d+)(\s+)([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?)(.*)$"
)
ONE_INDEX_BLOCKS = frozenset((
    "ZEEINPUTS", "ZEELAMS", "MASS", "ZEEYUKAWAF", "ZEEYUKAWAY"
))


def replacements(beta=1.394, mH1=300., mH2=700.):
    point = map_point(beta, mH1, mH2)
    values = {
        (name, int(code)): float(value)
        for name, block in point["map"].items()
        for code, value in block.items()
    }
    v = point["input_Gate6"]["v"]
    tanbeta = math.tan(beta)
    for idx in (1, 2, 3):
        values[("ZEEYUKAWAF", idx)] = 0.
    masses = {1: 0.000511, 2: 0.10566, 3: 1.777}
    for i in range(1, 4):
        for j in range(1, 4):
            values[("ZEEYUKAWAY", 3 * (i - 1) + j)] = (
                -tanbeta * math.sqrt(2.) * masses[i] / v if i == j else 0.
            )
    return values


def parse_card_values(card: str) -> dict:
    """Read back tracked single-index SLHA entries, ignoring other block formats."""
    out = {}
    block = None
    for line in card.splitlines():
        match = BLOCK_RE.match(line)
        if match:
            block = match.group(1).upper()
            continue
        if re.match(r"^\s*(?:decay|qnumbers)\b", line, re.I):
            block = None
            continue
        if block not in ONE_INDEX_BLOCKS:
            continue
        clean = line.split("#", 1)[0]
        if not clean.strip():
            continue
        match = VALUE_RE.match(clean)
        if match is None:
            raise ValueError(f"Malformed SLHA line in {block}: {line!r}")
        if match.group(5).strip():
            raise ValueError(f"Unexpected extra numeric tokens in {block}: {line!r}")
        key = (block, int(match.group(2)))
        if key in out:
            raise ValueError(f"Duplicate SLHA entry {key}")
        out[key] = float(match.group(4).replace("D", "E").replace("d", "e"))
    return out


def validate_card_values(card: str, expected: dict):
    found = parse_card_values(card)
    for key, value in expected.items():
        if key not in found:
            raise ValueError(f"Malformed SLHA card: missing {key}")
        if not math.isclose(found[key], value, rel_tol=3e-12, abs_tol=1e-12):
            raise ValueError(
                f"Malformed SLHA card: incorrect {key}: {found[key]} != {value}"
            )
    for pdg in (25, 225, 226, 227, 228):
        if ("MASS", pdg) not in found:
            raise ValueError(f"Malformed SLHA card: MASS[{pdg}] missing")
    return True


def render_card(template: str, values: dict) -> str:
    seen = set()
    block = None
    updated = []
    for original in template.splitlines(keepends=True):
        match = BLOCK_RE.match(original)
        if match:
            block = match.group(1).upper()
            updated.append(original)
            continue
        if re.match(r"^\s*(?:decay|qnumbers)\b", original, re.I):
            block = None
            updated.append(original)
            continue
        # An EOL is NOT part of (.*)$: without preserving it here, adjacent
        # SLHA entries silently join and disappear inside inline comments.
        bare = original.rstrip("\r\n")
        eol = original[len(bare):]
        candidate = VALUE_RE.match(bare) if block in ONE_INDEX_BLOCKS else None
        if candidate:
            indent, index, spacing, old_value, suffix = candidate.groups()
            key = (block, int(index))
            if key in values:
                if key in seen:
                    raise ValueError(f"Duplicate SLHA parameter {key}")
                if suffix and suffix.strip() and not suffix.lstrip().startswith("#"):
                    raise ValueError(f"Non-comment trailing data for {key}: {suffix!r}")
                updated.append(
                    f"{indent}{index}{spacing}{values[key]:.12e}{suffix}{eol}"
                )
                seen.add(key)
                continue
        updated.append(original)
    missing = set(values) - seen
    if missing:
        raise ValueError(f"Template missing required SLHA parameters: {sorted(missing)}")
    result = "".join(updated)
    if len(result.splitlines()) != len(template.splitlines()):
        raise ValueError("Parameter-card line count unexpectedly changed")
    validate_card_values(result, values)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--beta", type=float, default=1.394)
    ap.add_argument("--mH1", type=float, default=300.)
    ap.add_argument("--mH2", type=float, default=700.)
    ap.add_argument(
        "--acknowledge-unfitted-neutrino-sector",
        action="store_true", required=True,
        help="Acknowledge f_ab=0 gives vanishing radiative neutrino masses"
    )
    args = ap.parse_args()
    if args.template.resolve() == args.output.resolve():
        ap.error("Refusing to overwrite original parameter card")
    if args.output.exists():
        ap.error(f"Output already exists: {args.output}")
    expected = replacements(args.beta, args.mH1, args.mH2)
    result = render_card(args.template.read_text(), expected)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    validate_card_values(args.output.read_text(), expected)
    print(
        "PASS: independent SLHA readback of all", len(expected),
        "required parameters including MASS[225]=580.7 GeV"
    )
    print("Wrote diagnostic card:", args.output)
    print("CAUTION: raw DECAY widths are STALE, not physical branching ratios.")
    print("CAUTION: Zee neutrino sector unfitted, f_ab=0.")


if __name__ == "__main__":
    main()
