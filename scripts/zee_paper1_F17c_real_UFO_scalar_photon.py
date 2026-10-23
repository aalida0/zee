#!/usr/bin/env python3
"""F17c: inspect the ORIGINAL SARAH UFO dependency graph and evaluate its photon
couplings at the three source-pinned F13 charged mixing matrices.

AST-only: never import/exec generated UFO code. The expression evaluator has
an explicit arithmetic/function whitelist, and resolves actual UFO Parameter
definitions recursively. No model/card modification, no MadWidth claims.
"""
from __future__ import annotations

import argparse
import ast
import cmath
import hashlib
import json
import math
import re
from pathlib import Path

from zee_paper1_F17_inspect_real_SARAH_UFO import (
    SCALAR_POT, SCALAR_PDGS, TGT, UFO_SUBDIR, SOURCE_COMPLEX,
    cmat, inspect_ufo, parse_objects, consistency,
)
from zee_paper1_F17_verify_complex_json import verify_json

STATUS = "F17C_ACTUAL_UFO_SCALAR_DEPENDENCIES_AND_PHOTON_NUMERIC_NOT_CARD"
S2W_F16 = 0.23122
MZ_F16 = 91.1876
EPS_PHOTON = 3e-9
EPS_CHARGE = 3e-8


def hashfile(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def names_in(expr):
    return {n.id for n in ast.walk(ast.parse(str(expr), mode="eval"))
            if isinstance(n, ast.Name)}


class NumericUFO:
    """Resolve parameters.py expression strings without importing UFO modules."""
    def __init__(self, parameters, overrides):
        self.parameters = parameters
        self.overrides = overrides
        self.cache = {}
        self.visiting = set()

    def param(self, name):
        if name in self.cache:
            return self.cache[name]
        if name not in self.parameters:
            raise ValueError("Unknown UFO parameter " + name)
        if name in self.visiting:
            raise ValueError("Cyclic UFO Parameter dependencies: " + name)
        p = self.parameters[name]
        self.visiting.add(name)
        try:
            if p.get("nature") == "external":
                if name not in self.overrides:
                    raise ValueError("Unspecified REAL source external " + name)
                result = self.overrides[name]
            elif p.get("nature") == "internal":
                result = self.eval(p.get("value"))
            else:
                raise ValueError("Invalid nature in UFO: " + name)
            if not (math.isfinite(complex(result).real)
                    and math.isfinite(complex(result).imag)):
                raise ValueError("Nonfinite UFO numeric " + name)
            self.cache[name] = result
            return result
        finally:
            self.visiting.remove(name)

    def eval(self, expr):
        if isinstance(expr, bool):
            raise ValueError("Boolean numeric expression")
        if isinstance(expr, (int, float, complex)):
            return expr
        if not isinstance(expr, str):
            raise ValueError("Non-string UFO coupling expression " + repr(expr))
        return self._walk(ast.parse(expr, mode="eval").body)

    def _walk(self, n):
        if isinstance(n, ast.Constant) and type(n.value) in (int, float, complex):
            return n.value
        if isinstance(n, ast.Name):
            if n.id == "pi":
                return math.pi
            return self.param(n.id)
        if isinstance(n, ast.UnaryOp) and type(n.op) in (ast.UAdd, ast.USub):
            z = self._walk(n.operand)
            return z if isinstance(n.op, ast.UAdd) else -z
        if isinstance(n, ast.BinOp):
            a, b = self._walk(n.left), self._walk(n.right)
            if isinstance(n.op, ast.Add): return a + b
            if isinstance(n.op, ast.Sub): return a - b
            if isinstance(n.op, ast.Mult): return a * b
            if isinstance(n.op, ast.Div): return a / b
            if isinstance(n.op, ast.Pow): return a ** b
        if isinstance(n, ast.Call) and not n.keywords:
            args = [self._walk(arg) for arg in n.args]
            if isinstance(n.func, ast.Name) and n.func.id == "complex" and len(args) in (1, 2):
                return complex(*args)
            if isinstance(n.func, ast.Name) and n.func.id == "abs" and len(args) == 1:
                return abs(args[0])
            if (isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id in ("cmath", "math")
                    and n.func.attr in ("sin", "cos", "tan", "sqrt", "exp", "log", "asin", "acos")):
                module = cmath if n.func.value.id == "cmath" else math
                return getattr(module, n.func.attr)(*args)
        if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id in ("cmath", "math") and n.attr in ("pi", "e")):
            return getattr(math, n.attr)
        raise ValueError("Unsupported UFO arithmetic AST: " + ast.dump(n)[:250])


def source_ew(row):
    """Exactly the electroweak convention used by F16 SARAH numerical audit."""
    v = float(row["vev_GeV"])
    if not (math.isfinite(v) and v > 0):
        raise ValueError("Invalid exact-source electroweak VEV")
    sw = math.sqrt(S2W_F16)
    cw = math.sqrt(1.0 - S2W_F16)
    g2 = 2.0 * MZ_F16 * cw / v
    g1 = g2 * sw / cw
    e = g2 * sw
    return dict(v=v, v1=v * math.cos(row["beta_rad"]),
                v2=v * math.sin(row["beta_rad"]), e=e, g1=g1,
                g2=g2, TW=math.asin(sw), sw=sw, cw=cw, MZ=MZ_F16,
                MW=MZ_F16 * cw, Gf=1.0 / (math.sqrt(2.0) * v*v),
                aEWinv=4.0 * math.pi / (e*e),
                TanBeta=math.tan(row["beta_rad"]))


def external_values(parameters, row):
    ew = source_ew(row)
    rotation = cmat(row, "MixCharged", (3, 3))
    if max(abs(z.imag) for line in rotation for z in line) > 1e-12:
        raise ValueError("Unexpected complex charged scalar mixing")
    matrix = {"ZP%d%d" % (i+1, j+1): rotation[i][j].real
              for i in range(3) for j in range(3)}
    aliases = {
        **ew, **matrix, "ThetaW": ew["TW"], "SinThetaW": ew["sw"],
        "CosThetaW": ew["cw"], "aEW": 1.0 / ew["aEWinv"],
        "alphaEW": 1.0 / ew["aEWinv"], "alphaS": 0.118,
        "AlphaS": 0.118, "Vev": ew["v"], "vev": ew["v"],
    }
    # These are source-fixed assignments ONLY to real UFO external slots.
    # Internal g1/g2/TW/ZP must be derived from the actual UFO definitions.
    out = {}
    for label, definition in parameters.items():
        if definition.get("nature") != "external":
            continue
        pname = definition.get("name")
        block = str(definition.get("lhablock", "")).upper()
        code = definition.get("lhacode")
        if label in aliases:
            out[label] = aliases[label]
        elif isinstance(pname, str) and pname in aliases:
            out[label] = aliases[pname]
        elif block == "MASS" and code in ([23], (23,)):
            out[label] = ew["MZ"]
        elif block == "MASS" and code in ([24], (24,)):
            out[label] = ew["MW"]
        elif block == "SMINPUTS" and code in ([1], (1,)):
            out[label] = ew["aEWinv"]
        elif block == "SMINPUTS" and code in ([2], (2,)):
            out[label] = ew["Gf"]
        elif block == "SMINPUTS" and code in ([3], (3,)):
            out[label] = 0.118
    return out, ew, matrix


def param_ancestors(parameters, name, visited=None):
    if name not in parameters:
        return {"UNRESOLVED:" + name}
    if visited is None: visited = set()
    if name in visited: raise ValueError("Cyclic UFO scalar dependency " + name)
    p = parameters[name]
    if p.get("nature") == "external":
        return {name}
    if p.get("nature") != "internal":
        return {"UNKNOWN_NATURE:" + name}
    value = p.get("value")
    if not isinstance(value, str):
        return set()
    result = set()
    for symbol in names_in(value):
        if symbol in ("cmath", "math", "complex", "abs", "pi"):
            continue
        result.update(param_ancestors(parameters, symbol, visited | {name}))
    return result


def particle_mass_inventory(root, parameters):
    tree = ast.parse((root / "particles.py").read_text(encoding="utf-8"))
    found = {}
    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or not isinstance(statement.value, ast.Call):
            continue
        kwargs = {x.arg: x.value for x in statement.value.keywords if x.arg}
        pdg = kwargs.get("pdg_code")
        if pdg is None: continue
        try: number = abs(int(ast.literal_eval(pdg)))
        except (ValueError, TypeError): continue
        target = next((key for key, code in SCALAR_PDGS.items() if code == number), None)
        if not target: continue
        mass = kwargs.get("mass")
        if isinstance(mass, ast.Attribute) and isinstance(mass.value, ast.Name):
            symbol = mass.attr
        elif isinstance(mass, ast.Name):
            symbol = mass.id
        else:
            symbol = ast.unparse(mass) if mass else None
        p = parameters.get(symbol)
        found[target] = {
            "PDG": number, "particle": statement.targets[0].id,
            "actual_UFO_mass_symbol": symbol,
            "actual_UFO_mass_parameter": p,
            "mass_external_ancestors": sorted(param_ancestors(parameters, symbol))
                if symbol in parameters else [],
        }
    return found


def scalar_dependencies(parameters, mass_inventory, couplings):
    row = {}
    all_expressions = {
        "parameter:" + label: str(p.get("value", ""))
        for label, p in parameters.items() if p.get("nature") == "internal"
    }
    all_expressions.update({
        "coupling:" + label: str(p)
        for label, p in couplings.items()
    })
    for (_, code), source_name in SCALAR_POT.items():
        # OutputName aliases in models/SARAH/ZeeTypeII/parameters.m
        aliases = {"M12Sq": "M12S", "MCS2": "MC2"}
        names = {source_name, aliases.get(source_name, source_name)}
        exact = [key for key, p in parameters.items()
                 if key in names or p.get("name") in names]
        occurrences = {name: sorted(
            label for label, expr in all_expressions.items()
            if re.search(r"\b" + re.escape(name) + r"\b", expr))
            for name in sorted(names)}
        external = [key for key in exact if parameters[key].get("nature") == "external"]
        internal = [key for key in exact if parameters[key].get("nature") == "internal"]
        row[source_name] = {
            "source_LesHouches": {"block": next(b for (b,c), n in SCALAR_POT.items() if n == source_name),
                "entry": list(code)},
            "UFO_exact_name_matches": exact,
            "external_matches": external,
            "internal_matches": [{"parameter": key,
                "expression": parameters[key].get("value"),
                "external_ancestors": sorted(param_ancestors(parameters, key))}
                for key in internal],
            "exact_token_occurrences": occurrences,
            "classification": ("UFO_EXTERNAL" if external else
                "UFO_INTERNAL" if internal else "NOT_A_UFO_PARAMETER"),
            "mapping_to_source_coefficients_proven": bool(external or internal),
        }
    return row


def get_ufo_couplings(root):
    return {label: fields.get("value") for label, fields
            in parse_objects(root, "couplings.py", "Coupling").items()}


def scalar_photon_vertices(root):
    particles = parse_objects(root, "particles.py", "Particle")
    tree = ast.parse((root / "vertices.py").read_text(encoding="utf-8"))
    result = {"offdiagonal": [], "diagonal_H1": [], "diagonal_H2": []}
    for item in tree.body:
        if not isinstance(item, ast.Assign) or not isinstance(item.value, ast.Call):
            continue
        if not isinstance(item.value.func, ast.Name) or item.value.func.id != "Vertex":
            continue
        kv = {kw.arg: kw.value for kw in item.value.keywords if kw.arg}
        plist = kv.get("particles")
        if not isinstance(plist, (ast.List, ast.Tuple)) or len(plist.elts) != 3: continue
        pdgs = []
        for v in plist.elts:
            if not isinstance(v, ast.Attribute) or v.attr not in particles: break
            pdgs.append(particles[v.attr].get("pdg_code"))
        if len(pdgs) != 3 or sum(pdg == 22 for pdg in pdgs) != 1: continue
        charged = [p for p in pdgs if p != 22]
        if sorted(charged) == [-9000037, 37] or sorted(charged) == [-37, 9000037]:
            kind = "offdiagonal"
        elif sorted(charged) == [-37, 37]:
            kind = "diagonal_H1"
        elif sorted(charged) == [-9000037, 9000037]:
            kind = "diagonal_H2"
        else:
            continue
        refs = kv.get("couplings")
        if not isinstance(refs, ast.Dict): raise ValueError("UFO photon vertex coupling dict missing")
        extracted = []
        for key, val in zip(refs.keys, refs.values):
            if not (isinstance(val, ast.Attribute) and val.attr.startswith("GC_")):
                raise ValueError("Unexpected UFO photon coupling reference " + ast.unparse(val))
            extracted.append({"slot": ast.unparse(key), "coupling": val.attr})
        if not extracted: raise ValueError("Photon vertex with no UFO Coupling")
        result[kind].append({"vertex": item.targets[0].id, "charged_PDGS": charged,
                              "couplings": extracted})
    return result


def photon_numeric(parameters, couplings, photons, row):
    ext, ew, mixing = external_values(parameters, row)
    resolver = NumericUFO(parameters, ext)
    # Require all charged mixing entries actually used by the UFO and source.
    observed = {}
    for name, expected in sorted(mixing.items()):
        if name not in parameters:
            raise ValueError("UFO missing charged-mixing Parameter " + name)
        actual = resolver.param(name)
        if abs(actual - expected) > 1e-11:
            raise ValueError("UFO/source charged-mixing mismatch " + name)
        observed[name] = float(complex(actual).real)
    gauge = {}
    for name in ("g1", "g2", "TW"):
        if name not in parameters:
            raise ValueError("UFO lacks photon electroweak parameter " + name)
        actual = resolver.param(name)
        if abs(actual - ew[name]) > 1e-8 * max(1.0, abs(ew[name])):
            raise ValueError("F16-source/UFO gauge input mismatch " + name +
                             ": actual=" + str(actual) + " expected=" + str(ew[name]))
        gauge[name] = float(complex(actual).real)
    if abs(gauge["g1"] * math.cos(gauge["TW"]) -
           gauge["g2"] * math.sin(gauge["TW"])) > 1e-10:
        raise ValueError("Actual UFO photon electroweak gauge closure failed")
    if any(not photons[k] for k in photons):
        raise ValueError("Physical photon diagonal and offdiagonal vertices incomplete")
    results = {}
    for kind, vertices in photons.items():
        values = []
        for vertex in vertices:
            for slot in vertex["couplings"]:
                name = slot["coupling"]
                if name not in couplings:
                    raise ValueError("UFO photon coupling undefined " + name)
                value = resolver.eval(couplings[name])
                values.append({
                    "vertex": vertex["vertex"], "coupling": name, "slot": slot["slot"],
                    "source_UFO_expression": couplings[name],
                    "real": float(complex(value).real),
                    "imag": float(complex(value).imag),
                    "abs": abs(value),
                    "external_ancestors": sorted(set().union(*(
                        param_ancestors(parameters, n) for n in names_in(couplings[name])
                        if n in parameters))),
                })
        results[kind] = values
    orth = sum(mixing["ZP2%d" % i] * mixing["ZP3%d" % i] for i in (1, 2, 3))
    maxoff = max(v["abs"] for v in results["offdiagonal"])
    maxdiag = max(abs(v["abs"] - ew["e"]) for kind in ("diagonal_H1", "diagonal_H2")
                  for v in results[kind])
    return {
        "candidate_id": row["candidate_id"],
        "source_ew_convention": "F16_MZ_91.1876_sin2thetaW_0.23122_exact_case_v",
        "actual_UFO_gauge_parameters": gauge,
        "expected_positive_e": ew["e"],
        "mixing_orthogonality_row2_row3": orth,
        "evaluated_original_UFO_photon_couplings": results,
        "max_offdiagonal_absolute_coupling": maxoff,
        "max_diagonal_abs_charge_residual": maxdiag,
        "PASS": maxoff < EPS_PHOTON and maxdiag < EPS_CHARGE
                and abs(orth) < 1e-11,
    }


def run(f16_dir, f17_report, output):
    source = Path(f16_dir).expanduser().resolve()
    ufo = source / UFO_SUBDIR
    dest = Path(output).expanduser().resolve()
    if dest.exists(): raise FileExistsError("Refuse overwrite historical F17c report")
    src = verify_json(source / SOURCE_COMPLEX)
    f16 = json.loads((source / "F16_three_exact_F13_Zee_input_reconstruction.json").read_text())
    checked = consistency(f16, src)
    report = json.loads(Path(f17_report).expanduser().read_text())
    if Path(report["actual_SARAH_export_UFO_interface"]["ufo_dir"]).resolve() != ufo.resolve():
        raise ValueError("F17 report does not reference original F16 UFO")
    before = inspect_ufo(ufo)
    recorded = report["actual_SARAH_export_UFO_interface"]["ufo_python_source_SHA256"]
    for name, signature in recorded.items():
        if before["ufo_python_source_SHA256"].get(name) != signature:
            raise ValueError("F17-pinned UFO Python source changed: " + name)
    params = parse_objects(ufo, "parameters.py", "Parameter")
    couplings = get_ufo_couplings(ufo)
    masses = particle_mass_inventory(ufo, params)
    photon_vertices = scalar_photon_vertices(ufo)
    scalar = scalar_dependencies(params, masses, couplings)
    rows = []
    errors = {}
    for row in src["matrices"]:
        try:
            rows.append(photon_numeric(params, couplings, photon_vertices, row))
        except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
            errors[row["candidate_id"]] = str(exc)
    output_data = {
        "status": STATUS, "original_UFO_directory": str(ufo),
        "original_UFO_parameters_SHA256": hashfile(ufo / "parameters.py"),
        "original_UFO_couplings_SHA256": hashfile(ufo / "couplings.py"),
        "original_UFO_vertices_SHA256": hashfile(ufo / "vertices.py"),
        "exact_three_source_F17_json_SHA256": hashfile(source / SOURCE_COMPLEX),
        "exact_three_source_F16_json_SHA256": hashfile(source / "F16_three_exact_F13_Zee_input_reconstruction.json"),
        "original_F17_report": str(f17_report),
        "source_F16_F17_complex_checks": checked,
        "scalar_coefficient_UFO_representation": scalar,
        "physical_scalar_mass_UFO_parameterization": masses,
        "ufo_photon_vertices": photon_vertices,
        "photon_three_actual_UFO_expressions_evaluated": rows,
        "photon_unresolved_errors": errors,
        "all_three_photon_checks_pass": len(rows) == 3 and not errors and all(r["PASS"] for r in rows),
        "four_missing_scalar_coefficients_resolved_into_exact_physical_card": False,
        "complete_physical_card_validated": False,
        "madwidth_ready": False,
        "note": "UFO parameter inventory and dependency ancestors DO NOT prove inverse scalar-potential mapping. A non-external scalar term cannot be assigned an invented SLHA slot.",
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    for key in ("M112", "M222", "M12Sq", "MCS2"):
        detail = scalar[key]
        print("F17C_SCALAR", key, detail["classification"],
              "MATCHES", detail["UFO_exact_name_matches"])
    for name, info in masses.items():
        print("F17C_MASS_INPUT", name, info["PDG"], info["actual_UFO_mass_symbol"],
              info["mass_external_ancestors"])
    for row in rows:
        print("F17C_PHOTON", row["candidate_id"],
              "MAX_OFF", "%.12g" % row["max_offdiagonal_absolute_coupling"],
              "DIAG_E_RESIDUAL", "%.12g" % row["max_diagonal_abs_charge_residual"],
              "PASS", row["PASS"])
    for key, error in errors.items(): print("F17C_PHOTON_ERROR", key, error)
    print("F17C_STATUS", STATUS, "NUMERICAL_3_OF_3", output_data["all_three_photon_checks_pass"],
          "CARD_READY", False)
    print("F17C_REPORT", dest)
    return output_data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--f16-dir", type=Path, required=True)
    ap.add_argument("--f17-report", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    result = run(a.f16_dir, a.f17_report, a.output)
    if not result["all_three_photon_checks_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
