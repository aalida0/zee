"""Build compact D5 evidence from genuine local execution artifacts."""
import json
import re
from pathlib import Path
from .real_run_validation import validate_all, ROOT, LOCAL, sha


def main():
    real=validate_all();d4=json.loads((ROOT/'validation/module7/d4_decay_table.json').read_text())
    ufo=json.loads((LOCAL/'ufo_audit.json').read_text());matrix=json.loads((LOCAL/'mg_matrix_checks.json').read_text())
    analytical=json.loads((LOCAL/'partonic_checks.json').read_text())
    names={'P1':'H1H2_mixed_DY_Z_only','P2':'tbH2_5FS'}
    rows={(r['spectrum'],r['process']):r for r in real['rates']};chains=[]
    for entry in d4['conditional_lepton_families']:
        b2=entry['mothers']['H2']['branching_fraction'];b1=entry['mothers']['H1']['branching_fractions']['t anti-b']
        rates={}
        for process in ('P1','P2'):
            row=rows[(entry['spectrum_name'],process)];factor=b2*b1**(2 if process=='P1' else 1)
            rates[names[process]]={'tree_BR_product':factor,
                 'conditional_sigma_times_tree_BR_pb':row['sigma_LO_pb']*factor,
                 'integration_error_only_pb':row['integration_error_pb']*factor}
        chains.append({'benchmark_id':entry['benchmark_id'],'spectrum':entry['spectrum_name'],'family':entry['family_name'],
                       'BR2_H1Z':b2,'BR1_tb':b1,'single_H1_product':b2*b1,'two_H1_product':b2*b1*b1,'rates':rates})
    ranges={key:[min(c[key] for c in chains),max(c[key] for c in chains)] for key in ('single_H1_product','two_H1_product')}
    tests=(LOCAL/'tests.log').read_text();count=int(re.search(r'Ran (\d+) tests',tests)[1])
    if not tests.rstrip().endswith('OK'):raise ValueError('Scoped tests not PASS')
    arithmetic=(LOCAL/'arithmetic_tests.log').read_text()
    if not arithmetic.rstrip().endswith('OK'):raise ValueError('Required arithmetic suite not PASS')
    arithmetic_count=int(re.search(r'Ran (\d+) tests',arithmetic)[1])
    spectra=[]
    for spectrum in ('mH1_m50p0','source','mH1_p50p0'):
        physical=d4['spectrum_tables'][spectrum]['physical']
        spectra.append({'spectrum':spectrum,'physical':physical,
           'P1':rows[(spectrum,'P1')],'P2':rows[(spectrum,'P2')],'P3':real['optional_4FS']})
    residuals={k:max(c['residuals'].get(k,0.) for c in ufo['cases']) for k in ufo['cases'][0]['residuals']}
    native={'status':ufo['status'],'comparisons':ufo['comparisons'],'cases':ufo['native_card_count'],
       'maximum_absolute_residuals':residuals,'raw_evidence_sha256':sha(LOCAL/'ufo_audit.json'),
       'export':ufo['export'],'ufo_sha256':ufo['ufo_sha256'],'lha_mapping':ufo['lha_mapping'],
       'frozen_mass_terms':ufo['frozen_mass_terms'],'source_sha256':ufo['source_sha256'],
       'per_case':[{'id':c['id'],'comparisons':c['comparisons'],'residuals':c['residuals'],
                    'card_sha256':c['card_sha256'],'scalar_closure':{k:v for k,v in c['scalar_closure'].items() if k not in ('mixing_rows','full_hessian_eigenvalues_GeV2')}} for c in ufo['cases']]}
    report={'schema_version':'d5-real-two-process-1.0.0','date':'2026-10-28','D4_exact_base':'d0a276950dfbe0417c6cd22731b7f62f3285d789',
        'statuses':['D5_UFO_VERTEX_PASS','D5_EXECUTED_PARTON_LO_RATE_PASS','D5_CHAIN_LO_ARITHMETIC_PASS','D5_NOVELTY_NOT_ESTABLISHED'],
        'label':real['label'],'native_model':native,'real_execution_validation':real,
        'runtime':{'MG5':'3.6.7','MG5_tag_commit':'0e6c945573c8bab6246b9a172c219a7754125f51',
          'source_urls':['https://github.com/mg5amcnlo/mg5amcnlo/tree/v3.6.7','https://launchpad.net/mg5amcnlo/3.0/3.6.x/+download/MG5_aMC_v3.6.7.tar.gz','https://lhapdf.hepforge.org/downloads/?f=LHAPDF-6.5.6.tar.gz'],
          'initial_probe_sha256':sha(LOCAL/'runtime.json'),'LHAPDF':'6.5.6','Wolfram':'15.0.1','SARAH':'4.15.4',
          'compiler':'GNU Fortran 11.4.0 Ubuntu 22.04.3','official_release_source_comparison':json.loads((LOCAL/'release_comparison.json').read_text()),
          'archive_banner_note':'GitHub tag archive lacks .git and retains create_release.py, triggering a generic unknown-development banner. All 846 relevant Python/Fortran/C++/include source files match the official Launchpad release byte for byte; warning retained in logs.',
          'LHAPDF_source_archive_sha256':sha(LOCAL/'LHAPDF-6.5.6.tar.gz')},
        'settings':{'sqrt_s_TeV':13.6,'beam_energies_GeV':[6800.,6800.],
          'pdf_set':'NNPDF30_lo_as_0130','pdf_member':0,'lhaid':263000,'PDF_NumFlavors':5,
          'PDF_metadata_url':'https://lhapdfsets.web.cern.ch/current/NNPDF30_lo_as_0130/NNPDF30_lo_as_0130.info',
          'alpha_s_production':'LHAPDF interpolated LO running, AlphaS_OrderQCD=0, AlphaS_MZ=0.130 at PDF MZ=91.199997 GeV',
          'alpha_s_PDF_at_700':analytical['results'][0]['alpha_s_PDF_700'],
          'renormalization_scale_GeV':700.,'factorization_scales_GeV':[700.,700.],
          'scale_PDF_policy':'central member and fixed scales only; variations/uncertainties not evaluated; quoted errors are integration only',
          'quark_kinematics_GeV':{'u':0.,'d':0.,'s':0.,'c':0.,'b':0.,'t':172.4},
          'Yukawa_scheme':'D4 separate one-loop MS quark masses at Q=700 GeV using alpha_s(MZ=91.1876)=0.118, continuous thresholds 4.183/172.4; full complex CKM from exact D4 convention',
          'mt_Y_GeV':148.0414556305571,'mb_Y_GeV':2.69162343131315,
          'beta_rad':1.394,'gamma_rad':1.089,'widths':'H1,H2,top stable on-shell external; WZ=2.4952 GeV; other internal defaults in hashed cards; no decay chains generated',
          'MW_LHE_card_compatibility':'MASS 24=80.379 added as a computed dependent entry; UFO MW remains internal; no frozen model modification',
          'cuts':'no hard-process kinematic cuts, no detector/shower/fiducial selection'},
        'spectra':spectra,'tree_BR_composition':chains,'tree_BR_product_ranges':ranges,
        'independent_MG_matrix_checks':matrix,'independent_Z_convolution':analytical,
        'conditional_final_states':{
           'P1':'H2+ H1- + conjugate -> H1+ H1- Z -> t anti-t b anti-b Z',
           'P2':'g b -> t H2- -> t anti-t b Z; g anti-b -> anti-t H2+ -> anti-t t anti-b Z; incoming PDF bottom remnant is not an explicit final-state spectator',
           'P3':'optional 4FS t anti-b H2- + conjugate -> t anti-t b anti-b Z; not evaluated, never summed with 5FS'},
        'prior_art':{'status':'D5_NOVELTY_NOT_ESTABLISHED','review':'module8/PRIOR_ART.md',
          'references':['https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2','https://arxiv.org/abs/1701.05345v2','https://arxiv.org/html/2501.09796v1'],
          'decision':'2021 already covers tbH production and cascade hierarchy. Mixed unequal-pair novelty unverified. New constrained neutrino/LFV flavor-collider correlations required; twelve D4 families do not substantiate measurable flavor discrimination.'},
        'tests':{'passed':count,'log_sha256':sha(LOCAL/'tests.log'),
          'required_arithmetic_passed':arithmetic_count,'arithmetic_log_sha256':sha(LOCAL/'arithmetic_tests.log'),
          'scope':'arithmetic and gate falsifiers; native/generator evidence separately executed'},
        '2026_LINEARIZED_FLAVOR_FILTER_READY':False,'COMPLETE_LFV':False,'global_zee_acceptance':None,
        'vacuum_status':'UNKNOWN for all D2 scalar points','physical_B_to_Xs_gamma_2026':'INCOMPLETE',
        'fiducial_acceptance':None,'experimental_exclusion':None,
        'limitations':['LO hard stable-particle reference benchmarks only; no NLO accuracy or theory error assigned',
          'P1 restricted to conserved massless-quark Z-current contribution: no mixed photon coupling; full model neutral-scalar s-channel and Yukawa quark-exchange diagrams excluded',
          'D4 BRs are on-shell tree two-body; not physical NLO widths. Z/top/W BRs not included',
          'No 4FS/5FS sum or matching, no LHC reach/acceptance/background/likelihood, no global Zee viability']}
    table='\n'.join(f"| {s['physical']['mH1']:.0f} | {s['P1']['sigma_LO_pb']:.8g} ± {s['P1']['integration_error_pb']:.5g} | {s['P2']['sigma_LO_pb']:.8g} ± {s['P2']['integration_error_pb']:.5g} |" for s in spectra)
    from .real_run_validation import EXPECTED
    process_syntax='\n'.join(['define q = u1 u2 d1 d2 d3','define qb = u1bar u2bar d1bar d2bar d3bar',
                             '# P1 (separate output directory)',*EXPECTED['P1'],
                             '# P2 (separate output directory)',*EXPECTED['P2']])
    report['actual_process_syntax']=EXPECTED
    doc=f'''# D5 production audit — 2026-10-28

**D5_UFO_VERTEX_PASS; D5_EXECUTED_PARTON_LO_RATE_PASS; D5_CHAIN_LO_ARITHMETIC_PASS.**
These certify the stated LO parton-level reference benchmarks and conditional
arithmetic. **D5_NOVELTY_NOT_ESTABLISHED** remains. Full LFV and the 2026
linearized flavor filter are false; global Zee acceptance is null. All D2 vacuum
results remain UNKNOWN and physical 2026 B→Xsγ is incomplete.

## Executed rates

Both charged final states and both incoming beam orders are included exactly once.
Errors below are actual MG5 integration errors, not scale/PDF/theory uncertainties.
mH2=700 GeV, beta=1.394, gamma=1.089; 13.6 TeV pp, stable external scalars/top.

| mH1 [GeV] | P1 Z-only mixed pair [pb] | P2 gb associated, 5FS [pb] |
|---:|---:|---:|
{table}

P3 is optional and **not executed**: a separate massive-bottom 4F PDF/card setup
was not configured. Its entries remain null with this reason. 4FS and 5FS overlap;
never add them. The real-data schema is explicitly `d5-real-two-process-1.0.0`,
separate from the synthetic three-process arithmetic schema. No dummy 4FS rates.
Identical P2 results are expected: only the unused H1 mass changes, with the
same hard gb amplitude, all other inputs and random seed.

Actual audited UFO process syntax (P1 and P2 have separate generated directories):

```text
{process_syntax}
```

## Native model, mapping and independent checks

`math -script scripts/zee_d5_export.m` performed a fresh SARAH 4.15.4 export using
Wolfram 15.0.1 and the unchanged ZeeTypeII source, model SHA256
`{ufo['export']['source_sha256']['models/SARAH/ZeeTypeII/ZeeTypeII.m']}`.
All export files/cards/logs are ignored under validation/module8/local/.
The pre-existing SARAH installation output was not used as a certified model.

`python -m module8.ufo_audit` evaluated all exported parameters/couplings and
performed **{ufo['comparisons']} signed numerical comparisons across {ufo['native_card_count']} cards**:
all twelve D2 families at both D4 Yukawa scales, plus complex non-aligned and
signed/endpoint mixing controls. Every external LHA address is mapped explicitly,
serialized at 17-digit round-trip precision and reloaded before evaluation.
The source and two shifted spectra pass Module1 Hessian, tadpole and signed
mixing closure. No sample card or guessed external mass/potential input is used.
M112/M222/MCS2/M12Sq are absent from the UFO interaction parameter list; Module1
reconstructs them and checks the physical spectrum rather than inventing LHA inputs.

Native charged fields are Hm2/Hm3 with charge -1 and Hm2c/Hm3c with charge +1;
the scalar PDG signs must not be used to guess their physical charge. MG lowercases
these names. Both signed CKM orientations and all quark/lepton flavor pairs and
charge conjugates are compared with independent D3/D4 amplitudes. UFO FFS chains
use spinor indices (2,1); SARAH's exporter explicitly reverses PL/PR in that basis
(madgraph.m lines 126–127). Vector SSV coefficients use their actual ordered
H-,H+,V momentum difference, with the exporter vector sign convention. Photon
universality gives R Q Rᵀ=Q: its mixed coupling is exactly zero analytically;
numerical off-diagonal residual is {residuals['photon']:.3g}. The Z mixed coefficient
has the source -sin(2gamma)/2 normalization. Maximum signed quark/lepton residuals
are {residuals['quarks']:.3g}/{residuals['complex_leptons']:.3g}; physical-parameter
residual is {residuals['physical_parameters']:.3g} GeV.

`python -m module8.mg_matrix_checks` independently executed Python/ALOHA amplitudes.
The qqbar Z amplitude agrees with the analytical spin/color normalization.
The gb amplitude agrees with a separate explicit two-diagram Dirac trace and
gluon Ward identity. The two P2 charges agree at the same partonic momenta. Fixed-mass
mixing controls reproduce sin²(2gamma) for P1 and sin²(gamma) for P2, including
negative gamma and zero/endpoints. Physical thresholds are mH1+700 and
172.4+700 GeV. Controls vary the production basis and do not assert viable scalar points.

`python -m module8.partonic_checks` independently integrates the analytical Z-only
partonic result against the actual PDF grid, both incoming beam orders and both
final charges. 100×100 and 180×180 Gaussian quadratures agree closely; every MG
P1 rate agrees within five actual integration errors (individual deviations are in
JSON). These independent numbers are checks, not substituted generator results.

## Generator scheme and authenticity

MG5 3.6.7 from the official tagged commit
`0e6c945573c8bab6246b9a172c219a7754125f51`; LHAPDF 6.5.6 compiled locally;
GNU Fortran 11.4.0. No unknown binaries or alternate Zee model were sourced.
The GitHub archive's missing .git metadata triggers its generic development banner;
all **846** relevant source files were independently compared byte for byte with
the official Launchpad 3.6.7 release: zero differences. The warning remains in logs.

PDF: [NNPDF30_lo_as_0130](https://lhapdfsets.web.cern.ch/current/NNPDF30_lo_as_0130/NNPDF30_lo_as_0130.info),
member 0, ID **263000**, five flavors, LO alpha_s from the PDF interpolation,
alpha_s(PDF MZ=91.199997)=0.130; alpha_s(700)={report['settings']['alpha_s_PDF_at_700']:.12g}.
muR=muF1=muF2=700 GeV fixed; scale/PDF variations not evaluated. Light and bottom
kinematic masses are zero; mt=172.4 GeV. Independent Yukawa masses are D4's
one-loop MS evolution to 700 with alpha_s(91.1876)=0.118:
mt,Y=148.0414556305571, mb,Y=2.69162343131315 GeV. Exact D4 complex unitary CKM
and full general-Zee leptons are retained. No Yukawa mass is silently replaced
by a pole or flavor matching input. H1/H2/top widths are zero for the hard
process; Z width is 2.4952 GeV. Other native defaults are bound in the cards.

Madevent requires a numerical MASS 24 entry even though MWm is internal in this
UFO: the checked dependent value 80.379 was added to local cards only. A pilot
with only q-qbar or g-b beam ordering had no automatic mirror process, so final
cards explicitly include both beam orders. Preliminary six-flavor-PDF diagnostics
were superseded by all six five-flavor runs. Neither pilot set is promoted here.

P1 is the separately justified Z-only contribution for conserved massless quark
currents. The full model also allows Yukawa quark exchange and neutral-scalar
s-channel diagrams, excluded here; no mixed photon diagram contributes. This is
not a claim for the full-model inclusive unequal-pair cross section.

`module8.run_capture` launches the real generated executable, captures original
and normalized cards, native results, event banners/output, logs, source/matrix
manifests, full D4 bytes, UFO audit, PDF grid and generator archives with SHA256.
`module8.real_run_validation` independently verifies these artifacts, actual
energy/scales/PDF, zero external widths, both charges/beam orders, banner agreement,
finite integration statistics and the independent amplitude/convolution gates.
It rehashes the retained launcher, generator archive and immutable generated
matrix/source files against the captured inputs. Generated run_card.inc and
param_card.inc constants change between spectra and are checked through active
banner cards; integration .dat files are historical manifest entries only.
Madevent resets the on-disk seed to zero after execution; the validator requires
actual banner seed 4154 against the original card. Hashes bind the full D4 ledger,
not just the displayed BR rows. No arithmetic test can grant generator PASS.
Native results have finite printed precision; BR multiplication adds no physics precision.

## Conditional decays and publication decision

Across the exact twelve D4 families, BR2(H1Z)×BR1(tb) ranges
**{ranges['single_H1_product'][0]:.12g}–{ranges['single_H1_product'][1]:.12g}**;
BR2(H1Z)×BR1(tb)² ranges
**{ranges['two_H1_product'][0]:.12g}–{ranges['two_H1_product'][1]:.12g}**.
P1 gives t anti-t b anti-b Z and contains two H1 decays. P2 gives t anti-t b Z
or t anti-t anti-b Z and retains the associated top; the PDF bottom remnant is
not a resolved final-state spectator. Optional 4FS would add an explicit spectator
bottom. No Z/top/W BR, detector acceptance, shower, background or exclusion enters.
D4 BRs are on-shell tree two-body values, not NLO physical decay probabilities.
Conditional rate errors rescale integration errors only and assign no BR theory
uncertainty. They use the fixed D4 daughter-scale Yukawa inputs for decay and the
700 GeV Yukawa inputs for hard production; no extra charge factor is applied.

[The literature decision](PRIOR_ART.md) records the 2021 tbH/cascade precedent,
the 2017 general-Zee flavor scan, and the 2025 charged-scalar DY/mixing analysis.
These LO rates do not establish signal novelty or measurable discrimination of
D4's minute family differences. A useful first paper requires new constrained
neutrino/LFV flavor–collider correlations. No discovery or exclusion claim follows.

## Reproduction and scoped verification

Use a fresh clone on feature/zee-d5-parton-production from the verified D4 base.
Install only the named official sources into ignored local/, download the named
central PDF .info/member-0000 files and pdfsets.index, and compile pdf_bridge.cc
against that local LHAPDF. Native export refuses existing output directories.
The process generator writes executable cards into local/ using audited names.
The original captures used the GitHub tag source; the helper uses its verified
equivalent official release. Both archives must retain their recorded names
MG5_v3.6.7.tar.gz and MG5_release_v3.6.7.tar.gz. The independent MG checker imports
the extracted GitHub directory mg5amcnlo-mg5amcnlo-0e6c945 under local/.
These are reproduction steps for fresh outputs; validation of retained runs starts
with real_run_validation and does not regenerate their directories.

```sh
math -script scripts/zee_d5_export.m
python -m module8.ufo_audit
python -m module8.generate_processes
python -m module8.run_capture P1 source d5_v2_source
python -m module8.run_capture P2 source d5_v2_source
# Execute the source matrix/convolution checks before the shifted spectra.
python -m module8.mg_matrix_checks
python -m module8.partonic_checks
python -m module8.run_capture P1 mH1_m50p0 d5_v2_low
python -m module8.run_capture P2 mH1_m50p0 d5_v2_low
python -m module8.run_capture P1 mH1_p50p0 d5_v2_high
python -m module8.run_capture P2 mH1_p50p0 d5_v2_high
python -m module8.real_run_validation
python -m unittest discover -s tests -p 'test_module8_production_composition.py' -v
python -m unittest discover -s tests -p 'test_module8_*.py' -v
python -m module8.build_report
git diff --check
```

**{count} scoped tests pass**, including **{arithmetic_count} required arithmetic tests** plus new
energy/PDF/scale/cut/LHA-duplicate and analytical-threshold/mixing falsifiers.
An executable-source mutation test confirms that a valid historical manifest
cannot conceal a modified retained matrix source.
Arithmetic fixes reject 14 TeV inputs, duplicated spectrum/family tuples with
unique IDs, and nonzero errors on zero central rates. Raw logs and huge generator
outputs stay ignored. Compact evidence and all source hashes are in
[the D5 ledger](../validation/module8/d5_production.json).
'''
    auditpath=ROOT/'module8/D5_PRODUCTION_AUDIT.md';auditpath.write_text(doc)
    paths=list((ROOT/'module8').glob('*'))+list((ROOT/'tests').glob('test_module8_*.py'))+[ROOT/'scripts/zee_d5_export.m',ROOT/'validation/module7/d4_decay_table.json',ROOT/'validation/module7/native_vertex.json',ROOT/'validation/module7/d4_native_validation.json',ROOT/'module1/scalar_constraints.py',ROOT/'module1/foundation.json']
    report['source_sha256']={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths) if p.is_file()}
    (ROOT/'validation/module8/d5_production.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'statuses':report['statuses'],'BR_ranges':ranges,'tests':count}))

if __name__=='__main__':main()
