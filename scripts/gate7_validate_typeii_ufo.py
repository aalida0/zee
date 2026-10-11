#!/usr/bin/env python3
"""Check *static UFO vertex inventory* required by Zee-Type-II signal.

Does not establish gauge invariance, the model parameter mapping,
physical BRs or even an MG5 cross-section. After this gate, also run
MG5 process generation, Ward tests, and matched benchmark calculations.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_VERTEX = re.compile(
    r"\b(V_\d+)\s*=\s*Vertex\s*\("
    r"(?:(?!\n\s*V_\d+\s*=\s*Vertex).)*?"
    r"particles\s*=\s*\[([^\]]+)\]",
    re.DOTALL,
)
_PARTICLE = re.compile(r"\bP\.([A-Za-z_][A-Za-z_0-9]*)")


def inspect_vertex_file(text: str) -> dict:
    """Extract particle names from UFO Vertex(...particles=[...]) definitions."""
    vertices = {}
    for name, raw in _VERTEX.findall(text):
        particles = _PARTICLE.findall(raw)
        if not particles:
            raise ValueError(f"No UFO particle names for {name}")
        vertices[name] = particles
    if not vertices:
        raise ValueError("No Vertex definitions parsed; check model syntax")
    heavy = {"H__plus__", "H__minus__"}
    light = {"h__plus__", "h__minus__"}
    signs = [
        ("H__plus__", "h__minus__"),
        ("H__minus__", "h__plus__"),
    ]
    zhh = [
        name for name,p in vertices.items()
        if len(p)==3 and p[0]=="Z"
        and any(h in p for h in heavy)
        and any(h in p for h in light)
        and any(all(x in p for x in pair) for pair in signs)
    ]
    dy_h1 = [
        name for name,p in vertices.items()
        if len(p)==3 and any(x in p for x in light)
        and any(x in p for x in ("t","t__tilde__"))
        and any(x in p for x in ("b","b__tilde__"))
    ]
    dy_h2 = [
        name for name,p in vertices.items()
        if len(p)==3 and any(x in p for x in heavy)
        and any(x in p for x in ("t","t__tilde__"))
        and any(x in p for x in ("b","b__tilde__"))
    ]
    gamma_mixed = [
        name for name,p in vertices.items()
        if len(p)==3 and p[0]=="a"
        and any(x in p for x in heavy)
        and any(x in p for x in light)
    ]
    # Explicitly require that both charge assignments of the relevant 3-vertices exist
    z_sign = all(any(len(p)==3 and p[0]=="Z" and
                     all(x in p for x in pair)
                     for p in vertices.values()) for pair in signs)
    def quark_both_charges(group):
        return all(any(len(p)==3 and q in p and t in p and b in p
                       for p in vertices.values())
                   for q,t,b in group)
    tb_h2_both = quark_both_charges([
        ("H__plus__","t__tilde__","b"),
        ("H__minus__","b__tilde__","t"),
    ])
    tb_h1_both = quark_both_charges([
        ("h__plus__","t__tilde__","b"),
        ("h__minus__","b__tilde__","t"),
    ])
    findings = {
        "n_vertices":len(vertices),
        "Z_Hplus_hminus_vertices":zhh,
        "tb_heavy_charged_vertices":dy_h2,
        "tb_light_charged_vertices":dy_h1,
        "photon_mixed_charged_3point_vertices":gamma_mixed,
        "Z_offdiagonal_both_charges_present":z_sign,
        "tb_heavy_both_charges_present":tb_h2_both,
        "tb_light_both_charges_present":tb_h1_both,
        "no_photon_offdiagonal_3point":not gamma_mixed,
    }
    findings["PASS_static_vertex_inventory"] = bool(
        z_sign and tb_h2_both and tb_h1_both and not gamma_mixed)
    return findings


def validate_folder(path: Path) -> dict:
    vertices = path/"vertices.py"
    particles = path/"particles.py"
    if not vertices.is_file() or not particles.is_file():
        raise FileNotFoundError(f"Missing UFO particles.py or vertices.py in {path}")
    source=particles.read_text()
    for name, pdg in [("H__plus__","227"),("h__plus__","228")]:
        if not re.search(r"\b"+name+r"\s*=\s*Particle\(\s*pdg_code\s*=\s*"+pdg+r"\b",source):
            raise ValueError(f"Missing charged eigenstate {name}, PDG {pdg}")
    out=inspect_vertex_file(vertices.read_text())
    out["ufo_path"]=str(path.resolve())
    out["note"]="Static UFO vertex-inventory gate only. NOT LO amplitude validation or a model benchmark."
    return out


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("ufo",type=Path)
    a.add_argument("--output",type=Path)
    x=a.parse_args()
    result=validate_folder(x.ufo)
    blob=json.dumps(result,indent=2)+"\n"
    print(blob,end="")
    if x.output:
        x.output.parent.mkdir(parents=True,exist_ok=True)
        x.output.write_text(blob)
    if not result["PASS_static_vertex_inventory"]:
        raise SystemExit("FAIL: required Zee-Type-II signal vertices are incomplete")


if __name__=="__main__":
    main()
