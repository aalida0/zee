#!/usr/bin/env python3
"""Prepare a *source-only* Type-II quark-Yukawa extension of Yang/Wu Zee FeynRules.

Source: https://github.com/YangPhy/Zee-Model (external checkout).
Output: models/Zee_TypeII_FR. Does NOT produce a UFO, NLO counterterms,
or a calibrated Florentino et al. benchmark. Never modify upstream checkout.

Higgs-basis mapping:
   Phi1 =  cos(beta)*H1 - sin(beta)*H2
   Phi2 =  sin(beta)*H1 + cos(beta)*H2
Type II quark terms, relative to the original H1 (vev) Yukawas:
   down: H1 - tan(beta)*H2
   up:   H1bar + cot(beta)*H2bar.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

SOURCE_FILES = ("ZEE.fr", "Particles.fr", "Parameters.fr", "Lagrangian.fr")

REPLACEMENTS = {
    "QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] H1[ii]":
        "QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] (H1[ii] - Tan[beta]*H2[ii])",
    "QLbar[sp, ii, ff1, cc].uR [sp, ff2, cc] H1bar[jj]":
        "QLbar[sp, ii, ff1, cc].uR [sp, ff2, cc] (H1bar[jj] + Cot[beta]*H2bar[jj])",
}


def patch_quark_yukawa(text: str) -> str:
    """Fail closed unless exact, known upstream quark-Yukawa terms are found."""
    # Fail closed if the upstream file was changed or patch applied twice.
    for original in REPLACEMENTS:
        if text.count(original) != 1:
            raise ValueError(
                f"Expected exactly one occurrence of unpatched quark term: {original}"
            )
    edited = text
    for original, replacement in REPLACEMENTS.items():
        edited = edited.replace(original, replacement)
    return edited


def create(source: pathlib.Path, output: pathlib.Path) -> None:
    source = source.resolve()
    output = output.resolve()
    if source == output or source in output.parents:
        raise ValueError("Output must not be inside upstream source checkout")
    if str(output).startswith("/data/"):
        raise ValueError("Do not write model build under /data")
    if output.exists():
        raise FileExistsError(f"Output exists (never overwrite): {output}")
    for name in SOURCE_FILES:
        if not (source/name).is_file():
            raise FileNotFoundError(f"Missing upstream FeynRules source: {source/name}")
    # Validate patch completely BEFORE creating the derived folder.
    original=(source/"Lagrangian.fr").read_text()
    edited=patch_quark_yukawa(original)
    output.mkdir(parents=True)
    for name in SOURCE_FILES:
        shutil.copy2(source/name, output/name)
    (output/"Lagrangian.fr").write_text(edited)
    (output/"TYPEII_PATCH_STATUS.txt").write_text(
       "PROVISIONAL FEYNRULES SOURCE PATCH ONLY — NOT A VERIFIED UFO\n"
       "Base: Yang Ma and Yongcheng Wu, Zee Model FeynRules 1.1.0\n"
       "Changed ONLY Type-II Higgs-basis quark Yukawa terms:\n"
       "down: H1 - Tan[beta] H2\n"
       "up: H1bar + Cot[beta] H2bar\n"
       "Original scalar potential and lepton Yukawas untouched.\n"
       "FeynRules export, parameter-convention match, complete Ward/gauge\n"
       "tests and standalone MG5 amplitudes remain REQUIRED.\n"
       "All QCD UV/R2 counterterms MUST be regenerated using NLOCT.\n"
       "Do not copy CT_vertices.py or CT_couplings.py from old ZEE_NLO.\n"
    )


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=pathlib.Path,
                    default=pathlib.Path("external/Zee-Model"))
    ap.add_argument("--output",type=pathlib.Path,
                    default=pathlib.Path("models/Zee_TypeII_FR"))
    a=ap.parse_args()
    try:
        create(a.source,a.output)
    except (FileNotFoundError,FileExistsError,ValueError) as e:
        sys.exit(f"ABORT: {e}")
    print("PASS: Type-II Higgs-basis Yukawa source patch created:",a.output)
    print("NOT a UFO; before any signal generation, re-export/validate via FeynRules.")
    print("NLO requires fresh UV/R2 counterterms; old ZEE_NLO CT files are invalid.")


if __name__=="__main__":
    main()
