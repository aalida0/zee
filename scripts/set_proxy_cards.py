#!/usr/bin/env python3
"""Configure an MG5 2HDM *production-only* proxy; NOT a full Zee-model UFO.

The previous version silently removed newlines from edited card entries. This
version preserves comments and line endings, checks every expected entry before
writing, and refuses to operate on a process stored under /data.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys

PARAM_VALUES = {
    ("mass", 25): 125.0,
    ("mass", 35): 580.7,
    ("mass", 36): 633.7,
    ("mass", 37): 700.0,
    ("frblock", 1): 5.7294462974594245,
    ("frblock", 2): 1.0,
}
RUN_VALUES = {
    "ebeam1": "7000",
    "ebeam2": "7000",
    "nevents": "1200",
    "ickkw": "0",
    "maxjetflavor": "4",
    "pdlabel": "nn23lo1",  # Initial rate screening ONLY; not a 4FS precision PDF.
}


def split_eol(raw: str) -> tuple[str, str]:
    body = raw.rstrip("\r\n")
    return body, raw[len(body) :]


def update_param_card(text: str) -> str:
    out: list[str] = []
    seen: set[tuple[str, int]] = set()
    block = ""
    bottom_mass: float | None = None
    for raw in text.splitlines(keepends=True):
        body, eol = split_eol(raw)
        header = re.match(r"^\s*BLOCK\s+(\w+)\b", body, flags=re.I)
        if header:
            block = header.group(1).lower()
        elif re.match(r"^\s*DECAY\b", body, flags=re.I):
            block = ""
        item = re.match(r"^(\s*)(\d+)(\s+)(\S+)(.*)$", body)
        if item and block:
            key = (block, int(item.group(2)))
            if key == ("mass", 5):
                try:
                    bottom_mass = float(item.group(4).replace("D", "E").replace("d", "e"))
                except ValueError:
                    raise ValueError("MASS 5 cannot be parsed as a number") from None
            if key in PARAM_VALUES:
                if key in seen:
                    raise ValueError(f"Duplicate parameter-card entry {key}")
                seen.add(key)
                body = (
                    f"{item.group(1)}{item.group(2)}{item.group(3)}"
                    f"{PARAM_VALUES[key]:.12e}{item.group(5)}"
                )
        out.append(body + eol)
    missing = PARAM_VALUES.keys() - seen
    if missing:
        raise ValueError(f"Missing parameter-card entries: {sorted(missing)}")
    if bottom_mass is None or bottom_mass <= 0:
        raise ValueError("Expected positive MASS 5 for the massive-b 4FS UFO")
    result = "".join(out)
    if result.count("\n") != text.count("\n"):
        raise AssertionError("Parameter-card line count changed")
    return result


def update_run_card(text: str, sqrt_s_tev: float = 14.0) -> str:
    """Keep original MG5 card schema, but allow 14, 80, or 100 TeV beams."""
    if not math.isfinite(sqrt_s_tev) or sqrt_s_tev <= 0:
        raise ValueError("sqrt_s_tev must be finite and positive")
    updates = dict(RUN_VALUES)
    updates["ebeam1"] = f"{sqrt_s_tev*500.0:.12g}"
    updates["ebeam2"] = f"{sqrt_s_tev*500.0:.12g}"
    out: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines(keepends=True):
        body, eol = split_eol(raw)
        item = re.match(r"^(\s*)([^!=#]*?)(\s*=\s*)([A-Za-z_]\w*)(\b.*)$", body)
        if item:
            key = item.group(4).lower()
            if key in updates:
                if key in seen:
                    raise ValueError(f"Duplicate run-card entry {key}")
                seen.add(key)
                body = (
                    f"{item.group(1)}{updates[key]}{item.group(3)}"
                    f"{item.group(4)}{item.group(5)}"
                )
        out.append(body + eol)
    mandatory = {"ebeam1", "ebeam2", "nevents", "pdlabel", "maxjetflavor"}
    missing = mandatory - seen
    if missing:
        raise ValueError(f"Missing run-card entries: {sorted(missing)}")
    result = "".join(out)
    if result.count("\n") != text.count("\n"):
        raise AssertionError("Run-card line count changed")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("process_directory", type=pathlib.Path)
    parser.add_argument("--sqrt-s-tev", type=float, default=14.0)
    args = parser.parse_args()
    root = args.process_directory.resolve()
    if root == pathlib.Path("/data") or pathlib.Path("/data") in root.parents:
        sys.exit("ABORT: Do not run MG5 from /data; relocate repository to $HOME/zee")
    pc = root / "Cards" / "param_card.dat"
    rc = root / "Cards" / "run_card.dat"
    if not pc.is_file() or not rc.is_file():
        sys.exit("ABORT: Missing MG5 parameter/run card")
    try:
        param_text = update_param_card(pc.read_text())
        run_text = update_run_card(rc.read_text(), sqrt_s_tev=args.sqrt_s_tev)
    except (ValueError, AssertionError) as exc:
        sys.exit(f"ABORT: {exc}; regenerate a clean MG5 process before retrying")
    # Both cards were checked before either was modified.
    pc.write_text(param_text)
    rc.write_text(run_text)
    print("PASS: six MASS/FRBlock inputs updated; all parameter-card newlines retained")
    print("PASS: run card updated; original newlines retained")
    print("NOTE: initial internal nn23lo1 PDF is a rate-screening choice, not a 4FS precision prediction")
    print("NOTE: h+/h- in the proxy are antiparticles of ONE charged-Higgs species")


if __name__ == "__main__":
    main()
