#!/usr/bin/env python3
"""Fail-closed readback of all Gate-7D Zee-Type-II diagnostic LHA parameters.

Useful when validating a copied card or diagnosing MadWidth errors such as
'mass (225,) not define'. Requires ALL expected indices and values.
"""
import argparse
from pathlib import Path
from gate7_make_diagnostic_param_card import replacements,validate_card_values,parse_card_values
from zee_muon_make_scalar_card import selected_point,MAP_KEYS

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("card",type=Path)
    p.add_argument("--beta",type=float,default=1.394)
    p.add_argument("--mH1",type=float,default=300.)
    p.add_argument("--mH2",type=float,default=700.)
    p.add_argument("--b4-csv",type=Path,
                   help="Input full screened B4 CSV for exact scalar preflight")
    p.add_argument("--candidate-id",
                   help="One candidate ID from --b4-csv")
    a=p.parse_args()
    if not a.card.is_file():
        p.error(f"No such SLHA card: {a.card}")
    if bool(a.b4_csv) != bool(a.candidate_id):
        p.error("--b4-csv and --candidate-id must be supplied together")
    if a.b4_csv:
        point=selected_point(a.b4_csv,a.candidate_id)
        options={k:point[k] for k in MAP_KEYS}
        values=replacements(beta=point["beta"],mH1=point["mH1"],
                            mH2=point["mH2"],**options)
    else:
        values=replacements(a.beta,a.mH1,a.mH2)
    contents=a.card.read_text()
    validate_card_values(contents,values)
    actual=parse_card_values(contents)
    print("PASS: SLHA diagnostic card all",len(values),"required values parsed correctly")
    for code in (25,225,226,227,228):
        print(f"  MASS[{code}] = {actual['MASS',code]:.12g} GeV")
    print("  ZEEINPUTS[4] =",actual["ZEEINPUTS",4])
    print("  Antisymmetric lepton Zee Yukawas f_ab = 0: NOT a physical neutrino benchmark")
    print("  DECAY widths (if present) remain STALE prior to MadWidth.")


if __name__=="__main__":
    main()
