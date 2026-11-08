#!/usr/bin/env python3
"""Export partial ledgers; no missing prediction is a zero."""
import json
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
def read(p):return json.loads(p.read_text())
def put(name,obj):(O/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def main():
 snap=read(O/'SECTOR_SNAPSHOT_IN_PROGRESS.json');audit=read(O/'JOIN_AUDIT_IN_PROGRESS.json');h=read(R/'research/full_constraints/higgs/COVERAGE.json');
 put('INPUT_PROVENANCE.json',{'status':'DOCUMENTARY_ASSOCIATIONS_ONLY','source_hashes':audit['source_hashes'],'candidate_count':len(audit['rows']),'documentary_join_count':audit['documentary_join_count'],'raw_production_receipts_verified':0,'rows':audit['rows']})
 put('COVERAGE_BEFORE.json',{'status':'REPLAY_OF_FROZEN_COVERAGE','note':'Historical sector outputs; not a new physics likelihood','higgs_summary':h['summary'],'LFV':'incomplete radiative/three-body/conversion','B':'NLO coherent central exists for D7/F13; full theory sigma unknown','vacuum':'D10 positive sufficient certificates apply only to their exact tree potentials'})
 put('LFV_COMPLETENESS.json',{'scope':'saved partial dipoles; no complete process predictions','dipole_convention':'e m_mu/2; CL and CR in GeV^-2','experiment':{'channel':'mu->e gamma','observed_upper_limit':1.5e-13,'confidence':'90% CL','source':'https://arxiv.org/abs/2504.15711v2'},'missing':['mixed F/current gauge-invariant two-loop aggregate and counterterms','doublet gauge, neutral Zgamma and charged-current groups not mapped to two mixed states','QED running and finite external/neutrino terms','complete three-body and semileptonic Wilson vectors and consistent proton/neutron scalar normalization'],'rows':[{'case':x['case'],'witness':x['witness'],'scalar_sha256':x['scalar_sha256'],**x['LFV']} for x in snap['rows']]})
 put('BSGAMMA_COMPLETENESS.json',{'cut_GeV':1.6,'perturbative_scope':'coherent top-only two-state NLO charged-scalar matching and NLO rate; not NP NNLO','source':'research/full_constraints/bsgamma_hepfit/HEPFIT_RATE_REPORT.md','source_version':'HEPfit 322bd73a2dadd94ce94a6d71cb79d616e569120a','one_state_control':read(O/'INDEPENDENT_CONTROLS.json')['b_control'],'uncertainty':'THEORY_SIGMA_UNKNOWN','missing':['Wilson-dependent resolved-photon covariance','calibrated perturbative remainder','u/c, down Yukawa, finite ms and primed terms','NP electroweak and higher-order materiality'],'rows':[{'case':x['case'],'witness':x['witness'],'scalar_sha256':x['scalar_sha256'],**x['B'],'physical_status':'UNKNOWN'} for x in snap['rows']]})
 cases={}
 for case in h['cases']:
  name=case['id']; searches=[]
  for lim in h['limits']:
   ci=lim['cases'][name];searches.append({'id':lim['id'],'category':lim['category'],'collider':lim['collider'],'process':lim['process'],'source':lim['source_url'],'dataset_sha256':lim['sha256'],'decision':ci['status'],'applicability':ci.get('applicability',ci.get('reason','not specified')),'missing':ci.get('missing',[]),'acceptance':None,'model_theory_uncertainty':None})
  cases[name]={'summary':h['summary'][name],'heavy_neutral_requirements':h['heavy_neutral_requirements'][name],'searches':searches,'status':'UNKNOWN','partial_widths_complete':False,'uncertainty':None}
 put('HIGGS_COMPLETENESS.json',{'dataset_version':h['version'],'library_sha256':h['library_sha256'],'proviso':'mass-envelope candidate applicability; detailed source table inherited and may overcount. h125 leading Zgamma is available on D7/F13 NO, superseding older missing-Zgamma ledger text, without completing total width.','cases':cases})
 print('exported source-linked sector tables for',len(snap['rows']),'candidate rows')
if __name__=='__main__':main()
