"""Build the D6 report exclusively from validated native runs and pinned D4 BRs."""
import json
import math
from pathlib import Path
from .d6_production import ROOT, LOCAL, PROCESSES, gate
from .d6_baseline import audit
from .d6_generator_validate import validate_all
from .run_capture import sha


def build():
    d5=gate();baseline=audit(d5);native=validate_all();runs=native['rates']
    matrix=json.loads((LOCAL/'d6_matrix_checks.json').read_text())
    mixed=[]
    for spec in ['mH1_m50p0','source','mH1_p50p0']:
        f=next(r for r in runs if r['kind']=='F' and r['spectrum']==spec)
        z=next(r for r in runs if r['kind']=='Z' and r['spectrum']==spec)
        source=next(s for s in d5['spectra'] if s['spectrum']==spec)
        br=next(b for b in d5['tree_BR_composition'] if b['spectrum']==spec and b['family']=='baseline')
        mixed.append({'spectrum':spec,'mH1_GeV':source['physical']['mH1'],'mH2_GeV':700.,
          'sigma_full_LO_pb':f['sigma_LO_pb'],'full_integration_error_pb':f['integration_error_pb'],
          'sigma_Zonly_LO_pb':z['sigma_LO_pb'],'Zonly_integration_error_pb':z['integration_error_pb'],
          'D5_Zonly_source_pb':source['P1']['sigma_LO_pb'],'D5_Zonly_integration_error_pb':source['P1']['integration_error_pb'],
          'full_over_matched_Z':f['sigma_LO_pb']/z['sigma_LO_pb'],
          'full_minus_matched_Z_pb':f['sigma_LO_pb']-z['sigma_LO_pb'],
          'full_over_D5_Z':f['sigma_LO_pb']/source['P1']['sigma_LO_pb'],
          'full_minus_D5_Z_pb':f['sigma_LO_pb']-source['P1']['sigma_LO_pb'],
          'difference_policy':'Signed difference includes interference; not an omitted-diagram cross section. Covariance of integration errors not estimated.',
          'D4_benchmark_id':br['benchmark_id'],'D4_tree_BR2_H1Z':br['BR2_H1Z'],'D4_tree_BR1_tb':br['BR1_tb'],
          'D4_two_H1_BR_product':br['two_H1_product'],
          'conditional_full_sigma_times_D4_tree_BR_pb':f['sigma_LO_pb']*br['two_H1_product'],
          'conditional_integration_error_only_pb':f['integration_error_pb']*br['two_H1_product'],
          'full_receipt_sha256':f['receipt_sha256'],'Z_receipt_sha256':z['receipt_sha256']})
    assoc=[r for r in runs if r['kind']=='A' and r['yukawa_scheme']=='frozen700'];central=next(r for r in assoc if r['muR_GeV']==r['muF_GeV']==700.)
    assoc.sort(key=lambda x:(x['muR_GeV'],x['muF_GeV']))
    lo=min(r['sigma_LO_pb'] for r in assoc);hi=max(r['sigma_LO_pb'] for r in assoc)
    br=next(b for b in d5['tree_BR_composition'] if b['spectrum']=='source' and b['family']=='baseline')
    scale={'definition':'standard 7-point LO scale sensitivity; muR,muF in {350,700,1400} GeV, ratios 1/4 and 4 excluded',
      'yukawa_scheme':'D5 one-loop running-at-700 Yukawa masses frozen at every scale; only hard alpha_s and PDF scale change',
      'evolved_Yukawa_scheme':'Separately evaluated correlated 3-point diagnostic, not part of this frozen-mass 7-point envelope',
      'central_pb':central['sigma_LO_pb'],'min_pb':lo,'max_pb':hi,
      'min_over_central':lo/central['sigma_LO_pb'],'max_over_central':hi/central['sigma_LO_pb'],
      'relative_lower':lo/central['sigma_LO_pb']-1,'relative_upper':hi/central['sigma_LO_pb']-1,
      'points':[{'muR_GeV':r['muR_GeV'],'muF_GeV':r['muF_GeV'],'sigma_LO_pb':r['sigma_LO_pb'],'integration_error_pb':r['integration_error_pb'],'over_central':r['sigma_LO_pb']/central['sigma_LO_pb'],'receipt_sha256':r['receipt_sha256']} for r in assoc],
      'D4_benchmark_id':br['benchmark_id'],'D4_single_H1_BR_product':br['single_H1_product'],
      'conditional_central_sigma_times_D4_tree_BR_pb':central['sigma_LO_pb']*br['single_H1_product'],
      'conditional_min_sigma_times_D4_tree_BR_pb':lo*br['single_H1_product'],
      'conditional_max_sigma_times_D4_tree_BR_pb':hi*br['single_H1_product'],
      'interpretation':'LO sensitivity only; not calibrated NLO uncertainty or a confidence interval'}
    evolved=[r for r in runs if r['yukawa_scheme']=='evolved_muR']+[central]
    emin=min(x['sigma_LO_pb'] for x in evolved);emax=max(x['sigma_LO_pb'] for x in evolved)
    scale['evolved_Yukawa_correlated_3point']={'definition':'correlated-3-point LO sensitivity with D4 one-loop Yukawa masses evolved to muR; central run is exactly shared with frozen700 scheme','points':[{'muR_GeV':x['muR_GeV'],'muF_GeV':x['muF_GeV'],'sigma_LO_pb':x['sigma_LO_pb'],'integration_error_pb':x['integration_error_pb'],'over_central':x['sigma_LO_pb']/central['sigma_LO_pb'],'receipt_sha256':x['receipt_sha256']} for x in sorted(evolved,key=lambda x:x['muR_GeV'])],'min_pb':emin,'max_pb':emax,'relative_lower':emin/central['sigma_LO_pb']-1,'relative_upper':emax/central['sigma_LO_pb']-1,'mass_evolution':'Frozen Module7 D4 running_mass/yukawa_masses using alpha_s(MZ)=0.118; independent of LO PDF alpha_s=0.130 scheme; no silent scheme replacement'}
    graph_summary=[]
    for g in matrix['graphs']:
        graph_summary.append({'external_pdgs':g['external_pdgs'],'diagram_count':len(g['diagrams']),
          'internal_pdgs':[d['vertices'][0]['legs'][-1]['id'] for d in g['diagrams']],
          'orders':'QCD=0 QED=2 HIG=0 HIW=0 at amplitude level'})
    capture_failures=[]
    for tag,launcher in [('d6v2_F_mH1_m50p0_700_700','d6_capture.py'),('d6e_A_source_350_350','d6_evolved.py')]:
        folder=LOCAL/'d6_receipts'/tag
        if not folder.exists():continue
        capture_failures.append({'tag':tag,'status':'POST_EXECUTION_CAPTURE_FAILED_NOT_PROMOTED','reason':'Path loop variable shadowed CompletedProcess before receipt serialization; fixed with a separate completed variable, fresh run used instead','native_exit_code':None,'retained_artifact_sha256':{name:sha(folder/name) for name in ['execution.log','results.dat','run_card.dat','param_card.dat','proc_card_mg5.dat','sources.json']},'failed_capture_implementation_sha256':sha(LOCAL/(launcher+'.failed_capture_source'))})
    out={'schema_version':'d6-real-tree-production-1.0.0','date':'2026-10-28','D5_base':'e15e9badb8be8be848b1ec8737977086f5ba8e20',
      'statuses':['D6_FULL_MIXED_PAIR_PRODUCTION_PASS','D6_LO_SCALE_SENSITIVITY_PASS','D6_D5_REFERENCE_PASS','NOVELTY_UNPROVEN'],
      'GLOBAL_ZEE_ACCEPTANCE':None,'global_zee_acceptance':None,
      'settings':d5['settings']|{'scale_PDF_policy':'D6 seven-point frozen-Yukawa scale sensitivity plus separate correlated-3-point evolved-Yukawa diagnostic; PDF member0 only'},
      'PDF_uncertainty':'PDF_UNCERTAINTY_UNKNOWN','PDF_members_present':[p.name for p in (LOCAL/'pdf/NNPDF30_lo_as_0130').glob('*.dat')],
      'mixed_pair':mixed,'associated_5FS_scale_sensitivity':scale,'baseline_reference_arithmetic':baseline,
      'actual_process_syntax':PROCESSES,'native_validation':native,
      'diagram_classes':{'neutral_s_channel':[22,23,25,35,36],'quark_exchange':[1,2,3,4,5,6],
        'explanation':'Generated photon graph has numerically zero mixed coupling (native residual <=5.56e-17). Z is the only appreciable gauge graph. hh1/hh2/Ah2 and CKM quark exchange retained, including flavor-changing initial pairs. Six diagrams for unequal initial flavors, eight for identical flavors. No gg loop-induced production or QCD overlap.'},
      'generated_graph_summary':graph_summary,
      'fixed_partonic_flavor_checks':[r for r in matrix['flavor_checks'] if r['spectrum']=='source' and r['cos_theta']==.23 and r['external_pdgs'][2]==-9000037],
      'matrix_check_count':len(matrix['flavor_checks']),'matrix_endpoint_controls':matrix['endpoint_controls'],
      'publication_decision':'STOP mixed-pair headline work at these benchmarks: full tree production comparable to Z-only and far below 5FS associated production. No substantive novelty established beyond 2021 cascade/tbH and 2025 DY/mixing prior art. Prioritize a separately declared broad mass/flavor scan after D6.',
      'prior_art':{'status':'NOVELTY_UNPROVEN','checked':'2026-10-28','sources':['https://arxiv.org/abs/2106.08332','https://arxiv.org/html/2501.09796v1','https://arxiv.org/abs/1701.05345v2'],
        'queries':['"Zee model" "mixed" "pair production" charged scalar','"charged Higgs" "non-diagonal" "pair production" Zee'],'scope':'Targeted primary-source check and frozen PRIOR_ART review; no exhaustive proof of absence'},
      'unpromoted_capture_failures':capture_failures,
      'blockers':{'required_D6_production':[], 'physical_Zee_prediction':['LFV Wgamma incomplete','full 2026 B->Xs gamma incomplete','vacuum certification UNKNOWN','complete NuFIT likelihood incomplete','global Zee acceptance UNKNOWN','D4 BR higher-order uncertainty unquantified','PDF replica uncertainty unavailable','NLO and 4FS matching not evaluated','backgrounds and detector efficiencies absent']},
      'limitations':['Integration errors are numerical only. Signed full-minus-Z is not a positive new subprocess. Never add full and Z-only.',
        'D4 BRs are uncorrected on-shell tree two-body factors, no Z/top/W branching fractions or physical detector yields.',
        'No 4FS result or 4FS+5FS sum. No discovery/exclusion/95% CL statement.',
        'H2=700 fixed only for this production comparison; heavier masses remain allowed in a future broad scan, with NO+IO solutions and explicit missing gates.'],
      'tests':{'command':"python -m unittest discover -s tests -p 'test_module8_d6_*.py' -v",'log_sha256':sha(LOCAL/'d6_tests.log')},
      'input_provenance_sha256':sha(ROOT/'validation/module8/d6_input_provenance.json'),
      'source_sha256':{str(p.relative_to(ROOT)):sha(p) for pattern in ['module8/d6_*.py','tests/test_module8_d6_*.py'] for p in ROOT.glob(pattern)}}
    from module7.d4_inputs import yukawa_masses
    for point in scale['evolved_Yukawa_correlated_3point']['points']:
        mass=yukawa_masses(point['muR_GeV']);point['mt_Y_GeV']=mass[2];point['mb_Y_GeV']=mass[5]
    return out


def markdown(r):
    lines=['# D6 production robustness — 2026-10-28','',
      '**D6_FULL_MIXED_PAIR_PRODUCTION_PASS; D6_LO_SCALE_SENSITIVITY_PASS; D6_D5_REFERENCE_PASS.**',
      '**NOVELTY_UNPROVEN; GLOBAL_ZEE_ACCEPTANCE=null.**','',
      f"Fifteen promoted genuine MG5 3.6.7 integrations (plus {len(r['native_validation']['superseded_executions'])} superseded full-pair executions and {len(r['unpromoted_capture_failures'])} unpromoted outputs after capture failures): three full mixed-pair spectra, three matched Z-only controls, seven frozen-Yukawa 5FS associated-production scale points and two additional evolved-Yukawa points (sharing the identical central run). Errors throughout are numerical integration only. D5 evidence and all frozen files are unchanged.",'',
      '## Full tree mixed pair versus matched Z-only','',
      'Both final charges and both beam orders are explicitly generated exactly once. 13.6 TeV pp; NNPDF30_lo_as_0130 member 0, LHAID 263000, 5FS; mH2=700, beta=1.394, gamma=1.089; muR=muF=700 GeV. All physical parameters, complex CKM, running-at-700 Yukawas, massless incoming quarks, mt=172.4, zero H1/H2/top external widths and internal defaults are matched to D5. No hard-process cuts.','',
      '| mH1 GeV | Full LO pb | Matched Z-only LO pb | D5 Z-only pb | Full/Z matched | Full − Z matched pb |','|---:|---:|---:|---:|---:|---:|']
    for x in r['mixed_pair']:
        lines.append(f"| {x['mH1_GeV']:g} | {x['sigma_full_LO_pb']:.8g} ± {x['full_integration_error_pb']:.5g} | {x['sigma_Zonly_LO_pb']:.8g} ± {x['Zonly_integration_error_pb']:.5g} | {x['D5_Zonly_source_pb']:.8g} ± {x['D5_Zonly_integration_error_pb']:.5g} | {x['full_over_matched_Z']:.6f} | {x['full_minus_matched_Z_pb']:.6g} |")
    lines+=['','The signed differences include interference and Monte Carlo fluctuations. They are not positive cross sections of omitted diagrams. No covariance has been measured between the integrations. The JSON also gives ratios/differences directly to the original D5 source rates. All independent Z controls agree with D5 within actual combined integration precision; the new associated central rate reproduces D5 exactly at native printed precision. Never add full P1 to its Z-only subset.','',
      '## Inspected diagrams and independent amplitudes','',
      'Each identical-flavor full graph set contains eight diagrams: s-channel photon, Z, hh1 (25), hh2 (35), Ah2 (36), and three quark-exchange diagrams. Unequal initial flavors contain six graphs: three neutral scalars and three quark exchanges. Actual generated configs.inc, matrix sources, HELAS graph vertices and PDG IDs were inspected; the versioned graph summary includes every flavor and both final charges. The mixed photon coefficient is zero analytically, with native roundoff below 5.56e-17. No appreciable extra gauge graph is present. Neutral-scalar and t-channel Yukawa graphs are retained without a forced Z propagator. All generated tree graphs have amplitude orders QED=2, QCD=HIG=HIW=0; effective loop vertices and gg loop-induced production are excluded. QED=2 is an MG upper bound, and inspection confirms every included graph actually has two powers.','',
      'The independent Python/ALOHA evaluator executed 234 fixed-kinematics comparisons: all 13 initial-flavor combinations, both charged final states, three angles and three spectra at sqrt(shat)=2 TeV. Separate Z, quark-exchange and neutral-scalar evaluations expose signed interference. At source masses, cos(theta)=0.23, b bbar → H2+ H1− gives m²(full)=9.45133071667e-5, m²(Z)=1.35186133674e-4, m²(Y)=5.08388638638e-6 and total cross-term remainder −4.57567803581e-5. The u ubar effect is below 1e-5 fraction at that point; the bottom channel has the largest effect. These dimensionless spin/color-averaged matrix values are diagnostics, not hadronic rates. The flavor-changing channels are tiny. The integrated full rates stay comparable to Z-only.','',
      'At gamma=0 and pi/2, the independent Z-only control vanishes (≤3.1e-36 in m²). The full b bbar amplitude remains m²=2.24202421191e-6 in these fixed-potential, fixed-mass mixing controls. These controls do not reconstruct viable scalar points and do not establish that the full endpoint rate vanishes.','',
      '## Associated H2 scale sensitivity','',
      'Standard seven-point LO sensitivity around 700 GeV: muR/muF ratios 1/4 and 4 removed. Yukawa masses are frozen at the D5 running-at-700 values mt,Y=148.0414556305571 and mb,Y=2.69162343131315 GeV. Only hard alpha_s and factorization/PDF scale dependence is varied. A separate correlated-three-point evolved-Yukawa diagnostic is reported below, with the identical central run shared between schemes. Both charges and both incoming orders are included; the source mH1=300 card is used throughout.','',
      '| muR GeV | muF GeV | sigma LO pb | / central |','|---:|---:|---:|---:|']
    s=r['associated_5FS_scale_sensitivity']
    for x in s['points']:lines.append(f"| {x['muR_GeV']:g} | {x['muF_GeV']:g} | {x['sigma_LO_pb']:.8g} ± {x['integration_error_pb']:.5g} | {x['over_central']:.6f} |")
    lines+=['',f"Actual minimum/maximum: **{s['min_pb']:.8g}–{s['max_pb']:.8g} pb**, central {s['central_pb']:.8g} pb; **{100*s['relative_lower']:.3f}% / +{100*s['relative_upper']:.3f}%**. This is LO sensitivity, not a calibrated NLO error or statistical confidence interval. Only PDF member 0000 exists: **PDF_UNCERTAINTY_UNKNOWN**. Integration errors remain separate.",'',
      'Evolved-Yukawa correlated-3-point diagnostic: '+ '; '.join(f"({x['muR_GeV']:g},{x['muF_GeV']:g}) GeV: {x['sigma_LO_pb']:.8g} ± {x['integration_error_pb']:.5g} pb" for x in s['evolved_Yukawa_correlated_3point']['points'])+'.', '',
      f"Its separate range is {s['evolved_Yukawa_correlated_3point']['min_pb']:.8g}–{s['evolved_Yukawa_correlated_3point']['max_pb']:.8g} pb ({100*s['evolved_Yukawa_correlated_3point']['relative_lower']:.3f}% / +{100*s['evolved_Yukawa_correlated_3point']['relative_upper']:.3f}%). This includes the extra Yukawa mass-scheme effect and is not a seven-point envelope. D4 mass evolution retains alpha_s(MZ)=0.118; production alpha_s continues to come from the LO PDF.",'',
      '## Source locks, validation and conditional decays','',
      'The exact D5 base is e15e9badb8be8be848b1ec8737977086f5ba8e20. Its six original runs were revalidated read-only in the D5 workspace before copying minimal sources, native cards/UFO, central PDF and installed LHAPDF runtime into D6 ignored local/. No D5 event/process directory was reused for execution. All new outputs are under d6_F, d6_Z, d6_A and d6_receipts. The pinned D5 JSON, frozen code/model sources, mapped LHA cards, source archives and PDFs are SHA-checked.','',
      'Fresh independent native evaluation repeats all 5,904 signed comparisons across 36 native cards. The official MG5 release archive is pinned to the D5 SHA; 827 relevant Python/Fortran/C++/include files across madgraph/aloha/models/Template are compared byte-for-byte against the actual D6 runtime tree with zero differences. This selection differs from the historical D5 846-file check; it is an actual new comparison, not a recycled count. LHAPDF 6.5.6 shared-library and central-grid hashes match D5. The official source and UFO are unmodified. Only installed lhapdf-config paths were relocated into D6; this is recorded in versioned input provenance.','',
      'New D6 receipts bind launcher source, command, seed 4154, mapped cards, executable/matrix manifests, original/normalized cards, actual event banners, logs, results and source/PDF archives. The validator checks actual native version, charges/orders, beam energy, no applicable cuts, finite numerical errors, native log/banner/result agreement, all LHA values and active scales. MG resets the disk seed to zero after running; the banner must preserve 4154. Compiled vector.inc is generated as scalar WARP_SIZE=NB_WARP=VECSIZE_MEMMAX=1 and is checked explicitly; run_card.inc/param_card.inc are generated constants checked through banner cards. MG helicity recycling rewrites matrix1_optim.f when masses change; the first two shifted full-pair executions are retained but superseded, and new d6v3 reruns archive every compiled source per run. Optimized source snapshots are hashed and checked independently of later active runs; immutable original interaction code is rehashed against pre-execution manifests. A snapshot-capture loop variable initially shadowed the completed subprocess object; those two outputs are retained with null native exit codes and are not promoted. Fresh captures use the corrected code. The initial source full-pair manifest contains the immutable original matrix/templates before helicity recycling. Final whitespace checks removed one extra EOF newline from each new capture launcher after execution. The exact executed bytes are archived by SHA, and validation permits precisely that one-newline difference; the versioned input provenance records both hashes. D5 source-file hash invariants are not applied to new D6 scripts.','',
      'The baseline audit was corrected to reject changed reference scales/mixing/masses and mismatched linked BR/error entries. It remains reference arithmetic only. Native tests include recomputed-hash falsifiers for missing beam order, seed, nonfinite results, empty source manifests and changed top width, plus scale/scheme and failed-execution checks.','',
      '| mH1 GeV | D4 BR2×BR1² | Full P1 × tree BR pb |','|---:|---:|---:|']
    for x in r['mixed_pair']:lines.append(f"| {x['mH1_GeV']:g} | {x['D4_two_H1_BR_product']:.12g} | {x['conditional_full_sigma_times_D4_tree_BR_pb']:.9g} ± {x['conditional_integration_error_only_pb']:.5g} |")
    lines+=['',f"Source P2 has D4 BR2×BR1={s['D4_single_H1_BR_product']:.12g}, conditional central rate {s['conditional_central_sigma_times_D4_tree_BR_pb']:.10g} pb and frozen-Yukawa scale range {s['conditional_min_sigma_times_D4_tree_BR_pb']:.10g}–{s['conditional_max_sigma_times_D4_tree_BR_pb']:.10g} pb. Products attach the exact D4 benchmark IDs and ledger SHA through D5; no additional charge factor is used. D4 BRs are uncorrected on-shell tree two-body values with unquantified higher-order corrections. No Z/top/W decays, detector acceptance or physical yields are inferred.",'',
      '## Publication stop/go and remaining gates','',
      '**STOP mixed pair as a first-paper headline at these reference benchmarks.** Full tree rates are comparable to Z-only and much smaller than associated production. This does not establish a substantively new mechanism beyond the [2021 Zee cascade/tbH study](https://arxiv.org/abs/2106.08332) and [2025 charged-scalar DY/mixing study](https://arxiv.org/html/2501.09796v1). The [2017 general-Zee flavor scan](https://arxiv.org/abs/1701.05345v2) also precedes general flavor correlations. The targeted searches listed in the JSON do not prove bibliographic absence; NOVELTY_UNPROVEN remains.','',
      'Required D6 production blockers: **none**. Physical prediction gates remain incomplete: LFV Wgamma, full 2026 B→Xs gamma, vacuum certification, complete NuFIT likelihood, PDF replica uncertainty, higher-order production/decay corrections and detector backgrounds/efficiencies. GLOBAL_ZEE_ACCEPTANCE=null. No detector reach, discoverability, exclusion or 95% CL claim. No 4FS execution or 4FS+5FS sum.','',
      'Next physics priority is a separately declared broad scan of H1/H2 (including heavier masses), neutrals, beta and gamma, real scalar/tree EWPO screening, NO+IO genuine neutrino solutions, uncertainties and flavor gating. A missing critical gate keeps point acceptance UNKNOWN. H2=700 here isolates production uncertainties and does not exhaust the search space. This future scan is outside D6.','',
      '## Reproduction','',
      'Use isolated copies of the SHA-verified D5 native inputs and official runtime under D6 local/. Keep D5 read-only. Fresh-generation/run commands refuse existing outputs.','',
      '```sh',"python -m unittest discover -s tests -p 'test_module8_d6_baseline.py' -v",'python -m module8.d6_baseline --d5-evidence validation/module8/d5_production.json --output validation/module8/local/d6_baseline.json','python -m module8.d6_production generate','# Run F at source; shifted F spectra use the snapshot capture below:','python -m module8.d6_production run --kind F --spectrum source',
      'python -m module8.d6_production run --kind Z --spectrum source',
      'python -m module8.d6_production run --kind Z --spectrum mH1_m50p0',
      'python -m module8.d6_production run --kind Z --spectrum mH1_p50p0','# Run A at (700,700),(350,350),(350,700),(700,350),(700,1400),(1400,700),(1400,1400):','python -m module8.d6_production run --kind A --mur 700 --muf 700',
      'python -m module8.d6_production run --kind A --mur 350 --muf 350',
      'python -m module8.d6_production run --kind A --mur 350 --muf 700',
      'python -m module8.d6_production run --kind A --mur 700 --muf 350',
      'python -m module8.d6_production run --kind A --mur 700 --muf 1400',
      'python -m module8.d6_production run --kind A --mur 1400 --muf 700',
      'python -m module8.d6_production run --kind A --mur 1400 --muf 1400',"python -c \"from module8.d6_capture import execute; execute('F','mH1_m50p0'); execute('F','mH1_p50p0')\"",
      "python -c \"from module8.d6_evolved import execute; execute('A','source',350.,350.); execute('A','source',1400.,1400.)\"",'python -m module8.d6_matrix_checks','python -m module8.d6_generator_validate',"python -m unittest discover -s tests -p 'test_module8_d6_*.py' -v",'python -m module8.d6_rate_report','git diff --check','```','',
      'Compact production evidence, per-run hashes, settings, exact D5 controls, scale points and source links are in [d6_production.json](../validation/module8/d6_production.json). Raw native artifacts remain ignored under validation/module8/local/.']
    return '\n'.join(lines)+'\n'


def main():
    r=build();(ROOT/'validation/module8/d6_production.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    (ROOT/'module8/D6_PRODUCTION_ROBUSTNESS.md').write_text(markdown(r));print(', '.join(r['statuses']))
if __name__=='__main__':main()
