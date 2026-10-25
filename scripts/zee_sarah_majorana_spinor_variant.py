#!/usr/bin/env python3
"""Create isolated A/B SARAH diagnostic model with Majorana neutrino packaging.

Production remains models/SARAH/ZeeTypeII. In the original baseline,
modify the name and EWSB Fv from {vL,0} to {vL,conj[vL]}. After the
validated packaging correction, change only the unique model name.
The Lagrangian, gauge sector, couplings, Weyl fields,
parameters and particles remain identical. This is a representation
probe, NOT a statement that neutrino Majorana masses were computed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "models" / "SARAH" / "ZeeTypeII"
VARIANT = "ZeeTypeIIMajoranaAudit"
DEST = ROOT / "work" / "sarah_zee" / "sarah_model_variants" / VARIANT
OUT = ROOT / "work" / "sarah_zee"
BASE_MODEL = 'Model`Name = "ZeeTypeII";'
ALT_MODEL = f'Model`Name = "{VARIANT}";'
BASE_FV = "Fv -> {vL,0}"
ALT_FV = "Fv -> {vL,conj[vL]}"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    source_names = ("ZeeTypeII.m", "parameters.m", "particles.m")
    source = {name: (BASE / name).read_bytes() for name in source_names}
    model = source["ZeeTypeII.m"].decode("utf-8")
    for search in (BASE_MODEL,):
        if model.count(search) != 1:
            raise ValueError(f"Source model has {model.count(search)} occurrences of {search!r}")
    production_majorana = model.count(ALT_FV) == 1 and model.count(BASE_FV) == 0
    if not production_majorana and model.count(BASE_FV) != 1:
        raise ValueError('Ambiguous production neutrino spinor declaration')
    amended = model.replace(BASE_MODEL, ALT_MODEL)
    if not production_majorana:
        amended = amended.replace(BASE_FV, ALT_FV)
    restored = amended.replace(ALT_MODEL, BASE_MODEL)
    if not production_majorana:
        restored = restored.replace(ALT_FV, BASE_FV)
    if restored != model:
        raise AssertionError("Diagnostic modified more than approved substitutions")
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / f"{VARIANT}.m").write_text(amended, encoding="utf-8")
    for name in ("parameters.m", "particles.m"):
        (DEST / name).write_bytes(source[name])
        if (DEST / name).read_bytes() != source[name]:
            raise AssertionError(f"Unexpected difference in {name}")
    if (DEST / f"{VARIANT}.m").read_text() != amended:
        raise AssertionError("Variant model does not match expected contents")
    manifest = {
        "status": "DIAGNOSTIC_MAJORANA_SPINOR_VARIANT_CREATED_NOT_MNU_VALIDATED",
        "production_untouched": True,
        "changed_lines_exactly": (["Model name"] if production_majorana else
                                 ["Model name", "EWSB DiracSpinors Fv declaration"]),
        "production_majorana": production_majorana,
        "baseline_sha256": {name: sha256(payload) for name, payload in source.items()},
        "diagnostic_model_sha256": sha256(amended.encode()),
        "diagnostic_directory": str(DEST),
        "majorana_variant_name": VARIANT,
        "no_majorana_mass_added": True,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e3_majorana_variant_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print("ZEE_E3_MAJORANA_VARIANT_WRITTEN", DEST)
    print("ZEE_E3_MAJORANA_VARIANT_STATUS", manifest["status"])
    print("ZEE_E3_MAJORANA_MODEL_SOURCE_UNCHANGED True")
    print("ZEE_E3_MAJORANA_MASS_FROM_SPINOR_DECLARATION False")

if __name__ == "__main__":
    main()
