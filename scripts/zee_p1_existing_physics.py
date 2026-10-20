#!/usr/bin/env python3
"""Minimal real-physics entry points, explicitly bounded by existing coverage.

Run pre-existing Zee scalar reconstruction and complete *implemented*
charged LO channel inventory. No physical HiggsBounds result is fabricated.
The neutrino helper invokes the existing exact B2 mass-matrix closure.
"""
from __future__ import annotations
import math
from typing import Mapping

def scalar_preflight(point):
 from gateB4_adaptive_zee_scalar_scan import scalar_screen,ewpo_screen
 required=("mH1","mH2","mh2","ma","alpha","beta","gamma",
           "m12sq","lc","k1","k2","k12")
 if any(k not in point for k in required):
  raise ValueError("Missing scalar-potential parameter")
 if any(not math.isfinite(float(point[k])) for k in required):
  raise ValueError("Nonfinite scalar-potential parameter")
 theory=scalar_screen(point)
 if theory is None:
  return {"status":"SCALAR_BFB_OR_UNITARITY_SCREEN_FAILED",
          "full_Zee_excluded":None}
 ew=ewpo_screen(point,64)
 if ew is None:
  return {"status":"SCALAR_EWPO_ELLIPSOID_SCREEN_FAILED",
          "full_Zee_excluded":None}
 return {"status":"SCALAR_BFB_UNITARITY_EWPO_SCREEN_PASSED_NOT_ALLOWED",
         "max_abs_tree_unitarity":theory["max_abs_unitarity_eigenvalue"],
         "full_Zee_excluded":None}

def charged_included_widths(point):
 from gate6_width_inventory import inventory
 values=inventory(**{
  "beta":point["beta"],"mH1":point["mH1"],"mH2":point["mH2"],
  "alpha":point["alpha"],"gamma":point["gamma"],
  "m12sq":point["m12sq"],"mh2":point["mh2"],"ma":point["ma"],
  "lc":point["lc"],"k1":point["k1"],"k2":point["k2"],"k12":point["k12"]})
 return {
  "status":"CHARGED_INCLUDED_CHANNEL_LO_ONLY_NOT_COMPLETE",
  "included_channels_GeV":values["partial_widths_GeV"],
  "full_model_HiggsBounds_input_ready":False,
  "physical_total_width_validated":False,
 }

def exact_neutrino_seed(point,seed=20261020):
 import numpy as np
 from gateA1b_hierarchical_no_seed import (
   target_neutrino_matrix,antisymmetric_f_with_null_condition)
 from gateB2_zee_neutrino_family_scan import solve_point
 target,_=target_neutrino_matrix()
 f,_=antisymmetric_f_with_null_condition(target)
 rng=np.random.default_rng(seed)
 result=solve_point(point,target,f,rng,0.)
 if result is None:raise ValueError("No perturbative exact-neutrino seed")
 if result["neutrino_matrix_closure_eV"]>=1.e-9:
  raise ValueError("Neutrino closure failed")
 return {
  "status":"SINGLE_EXACT_NEUTRINO_TARGET_LFV_PARTIAL_NOT_ALLOWED",
  "result":result,
  "oscillation_likelihood_complete":False,
  "full_Zee_allowed":None,
 }
