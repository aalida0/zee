#!/usr/bin/env python3
"""Priority-1 Zee global scan: small, fail-closed *physics input* contracts.

This is an orchestration/validation layer, not a substitute for a full
two-Higgs NNLO b->s gamma rate, complete general-Zee LFV calculation,
NNLO production cross sections or complete decay calculation.

One line per scalar point (JSONL) is joined by candidate_id to independently
generated, provenance-pinned calculation exports. Missing physics is an
explicit BLOCKED status; NEVER turn it into a zero prediction or an
allowed/excluded classification. Existing E2-F9 calculations stay untouched.
"""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path

IDS=("h","H","A","H1","H2")
REQUIRED=("neutrino","lfv","bsgamma","decays","production")
STAGE={"neutrino":"OSCILLATION_LIKELIHOOD",
       "lfv":"FULL_LFV_AMPLITUDE_AND_RATE",
       "bsgamma":"MATCHED_INCLUSIVE_B_TO_XS_GAMMA",
       "decays":"FIVE_STATE_TOTAL_WIDTHS",
       "production":"VALIDATED_HADRONIC_PRODUCTION"}
STATUS="P1_SOURCE_PINNED_ADAPTERS_NOT_A_COMPLETED_ZEE_PHYSICS_IMPLEMENTATION"

def hashfile(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for part in iter(lambda:f.read(1048576),b""):
            h.update(part)
    return h.hexdigest()

def numeric(x,where,*,positive=False,nonnegative=False):
    if isinstance(x,bool):raise ValueError(where+" Boolean not a number")
    try:v=float(x)
    except (TypeError,ValueError) as e:raise ValueError(where+" not numerical") from e
    if not math.isfinite(v):raise ValueError(where+" not finite")
    if positive and v<=0:raise ValueError(where+" must be positive")
    if nonnegative and v<0:raise ValueError(where+" negative")
    return v

def read_points(p):
    """Works with original B4 scalar CSV: preserves its numeric inputs."""
    with Path(p).open(newline="") as f:
        reader=csv.DictReader(f)
        needed=("id","mH1","mH2","mh2","ma","gamma","tanbeta")
        if not reader.fieldnames or not set(needed).issubset(reader.fieldnames):
            raise ValueError("B4 input requires "+",".join(needed))
        points={}
        for row in reader:
            key=row["id"]
            if not key or key in points:raise ValueError("duplicate/empty B4 ID")
            m1=numeric(row["mH1"],"mH1",positive=True)
            m2=numeric(row["mH2"],"mH2",positive=True)
            if not m1<m2:raise ValueError("charged mass ordering")
            gamma=numeric(row["gamma"],"gamma")
            if not 0<gamma<math.pi/2:raise ValueError("charged mixing interval")
            data={q:numeric(row[q],q,positive=True)
                  for q in ("mh2","ma","tanbeta")}
            if row.get("candidate_status") and "NOT_ALLOWED" not in row["candidate_status"]:
                raise ValueError("Original B4 scalar points cannot be called allowed")
            points[key]={"candidate_id":key,"h":125.0,
                         "H":data["mh2"],"A":data["ma"],
                         "H1":m1,"H2":m2,"gamma":gamma,
                         "tanbeta":data["tanbeta"]}
    if not points:raise ValueError("empty B4 point source")
    return points

def load_export(path,expected_stage,points):
    """Export: {schema_version, stage, provenance, records:[...]}.

    File SHA is pinned externally in the final manifest. Report all
    malformed/missing IDs; do NOT forward some records as full-model passes.
    """
    content=json.loads(Path(path).read_text())
    if content.get("schema_version")!=1 or content.get("stage")!=expected_stage:
        raise ValueError("wrong stage/schema: "+expected_stage)
    if not isinstance(content.get("provenance"),dict) or not content["provenance"].get("source"):
        raise ValueError("missing independent backend provenance")
    records=content.get("records")
    if not isinstance(records,list):raise ValueError("records must be list")
    byid={}
    for row in records:
        if not isinstance(row,dict):raise ValueError("nonobject row")
        key=row.get("candidate_id")
        if key not in points or key in byid:raise ValueError("unknown/duplicate "+str(key))
        byid[key]=row
    return byid,content["provenance"]

def validate_neutrino(rec):
    """In-scope numerical closure; full oscillation likelihood external."""
    if rec.get("full_two_ordering_oscillation_likelihood_computed") is not True:
        return "BLOCKED_FULL_OSCILLATION_LIKELIHOOD"
    fit=rec.get("oscillation_fit",{})
    ordering=fit.get("ordering")
    if ordering not in ("NO","IO"):return "BLOCKED_NO_OR_IO_NOT_SPECIFIED"
    numeric(rec.get("mass_matrix_closure_eV"),"neutrino closure",nonnegative=True)
    if float(rec["mass_matrix_closure_eV"])>=1e-9:
        return "FAIL_NUMERICAL_MASS_MATRIX_CLOSURE"
    numeric(fit.get("chi2"),"neutrino chi2",nonnegative=True)
    if not fit.get("dataset") or not fit.get("source_version"):
        return "BLOCKED_NEUTRINO_FIT_DATASET"
    return "EVALUATED_FULL_OSCILLATION_INPUT"

def validate_lfv(rec):
    """Require a coherent full amplitude, NOT D1/D4 partial score."""
    required={"mu_to_e_gamma","tau_to_e_gamma","tau_to_mu_gamma",
              "mu_to_3e","mu_e_conversion"}
    if rec.get("all_one_and_two_loop_amplitudes_interfered") is not True:
        return "BLOCKED_FULL_COHERENT_LFV_AMPLITUDES"
    if rec.get("conversion_nuclear_overlap_and_capture_included") is not True:
        return "BLOCKED_MU_E_CONVERSION"
    limits=rec.get("rates_and_limits",{})
    if not isinstance(limits,dict) or not required.issubset(limits):
        return "BLOCKED_LFV_CHANNEL_COVERAGE"
    for channel,values in limits.items():
        if not isinstance(values,dict):raise ValueError("LFV channel row malformed")
        numeric(values.get("prediction"),channel+" rate",nonnegative=True)
        numeric(values.get("experimental_90CL_limit"),channel+" limit",positive=True)
    if not rec.get("source_validation_reference"):
        return "BLOCKED_INDEPENDENT_LFV_VALIDATION"
    return "EVALUATED_COMPLETE_LFV_INPUT"

def validate_bsgamma(rec):
    """No linearized 2026 SM+old-SuperIso shift accepted as full BSM."""
    if rec.get("scheme_matched_two_charged_inclusive_rate") is not True:
        return "BLOCKED_MODERN_TWO_CHARGED_MATCHING"
    if rec.get("operator_basis_and_matrix_element_closure") is not True:
        return "BLOCKED_BSGAMMA_OPERATOR_SCHEME"
    if rec.get("SM_and_TypeII_670_independent_controls_pass") is not True:
        return "BLOCKED_SAME_SCHEME_SM_TYPEII_CONTROLS"
    if rec.get("calibrated_BSM_uncertainty_likelihood") is not True:
        return "BLOCKED_NP_THEORY_COVARIANCE"
    br=numeric(rec.get("branching_ratio"),"bsgamma BR",nonnegative=True)
    if br>=1:raise ValueError("bsgamma BR above unity")
    numeric(rec.get("theory_sigma"),"bsgamma theory sigma",nonnegative=True)
    if abs(numeric(rec.get("Egamma_cut_GeV"),"gamma cut")-1.6)>1e-8:
        return "BLOCKED_WRONG_PHOTON_ENERGY_CUT"
    if not rec.get("perturbative_order") or not rec.get("validation_document"):
        return "BLOCKED_BSGAMMA_PRECISION_DOCUMENTATION"
    return "EVALUATED_MODERN_INCLUSIVE_RATE_INPUT"

def validate_decays(rec,masses):
    """Five-state total widths. Channels must exhaust each total.

    No implicit 'missing decays = zero'. Reports closed only with
    explicit independent origin + physical channel coverage assertion.
    """
    if rec.get("all_physical_decay_channels_enumerated") is not True:
        return "BLOCKED_DECAY_CHANNEL_COMPLETENESS"
    if rec.get("off_shell_and_QCD_treatment_validated") is not True:
        return "BLOCKED_OFFSHELL_QCD_DECAY_PREDICTIONS"
    if not rec.get("independent_width_validation_reference"):
        return "BLOCKED_INDEPENDENT_WIDTH_VALIDATION"
    particles=rec.get("particles",{})
    if set(particles)!=set(IDS):return "BLOCKED_FIVE_STATE_WIDTH_COVERAGE"
    for pid in IDS:
        item=particles[pid]
        if not isinstance(item,dict):raise ValueError("width particle nonobject")
        if not math.isclose(numeric(item.get("mass_GeV"),pid+" mass",positive=True),
                            masses[pid],rel_tol=1e-7,abs_tol=1e-5):
            raise ValueError("full width mass disagreement "+pid)
        total=numeric(item.get("total_width_GeV"),pid+" width",positive=True)
        channels=item.get("partial_widths_GeV")
        if not isinstance(channels,dict) or not channels:
            return "BLOCKED_EMPTY_DECAY_CHANNELS"
        part=sum(numeric(v,pid+" "+k,nonnegative=True)
                 for k,v in channels.items())
        if not math.isclose(part,total,rel_tol=1e-4,abs_tol=1e-9):
            return "BLOCKED_DECAY_TOTAL_CLOSURE"
    return "EVALUATED_FIVE_STATE_DECAY_INPUT"

def validate_production(rec,masses):
    """Physical pb cross sections with identified collider/process sources."""
    if rec.get("all_relevant_hadronic_channels_enumerated") is not True:
        return "BLOCKED_HADRONIC_CHANNEL_COVERAGE"
    if rec.get("interference_K_factors_PDF_uncertainties_validated") is not True:
        return "BLOCKED_PRODUCTION_PRECISION"
    if not rec.get("generator_tune_and_validation_reference"):
        return "BLOCKED_INDEPENDENT_PRODUCTION_VALIDATION"
    channels=rec.get("particles",{})
    if set(channels)!=set(IDS):return "BLOCKED_FIVE_STATE_PRODUCTION"
    for pid in IDS:
        row=channels[pid]
        if not isinstance(row,dict) or not row:
            return "BLOCKED_EMPTY_PRODUCTION"
        for process,d in row.items():
            if not isinstance(d,dict) or not process:raise ValueError("bad production mode")
            numeric(d.get("sigma_pb"),pid+" "+process,nonnegative=True)
            numeric(d.get("uncertainty_pb"),pid+" sigma error",nonnegative=True)
            if d.get("collider") not in ("LHC13","LHC13p6","LHC14"):
                return "BLOCKED_COLLIDER_OR_ENERGY"
    return "EVALUATED_FIVE_STATE_PRODUCTION_INPUT"

VALIDATORS={"neutrino":lambda r,p:validate_neutrino(r),
            "lfv":lambda r,p:validate_lfv(r),
            "bsgamma":lambda r,p:validate_bsgamma(r),
            "decays":validate_decays,
            "production":validate_production}

def evaluate(points,exports):
    """Every model receives complete stage status, never a fabricated pass."""
    out=[]
    for key,p in points.items():
        statuses={}
        for stage in REQUIRED:
            rec=exports.get(stage,{}).get(key)
            statuses[stage]=("BLOCKED_NO_BACKEND_INPUT" if rec is None else
                            VALIDATORS[stage](rec,p))
        complete=all(status.startswith("EVALUATED_")
                     for status in statuses.values())
        out.append({"candidate_id":key,"stages":statuses,
                    "all_priority1_backend_inputs_complete":complete,
                    "experimental_Zee_allowed_or_excluded":None,
                    "complete_global_likelihood_implemented":False})
    return out
