"""Historical NNLO table control; never used as a Zee likelihood."""
import json, math
from statistics import NormalDist
from pathlib import Path
from execute import table_reference, sha
HERE=Path(__file__).resolve().parent
TABLE=Path('/tmp/zee-hepfit/HEPfit-322bd73a2dadd94ce94a6d71cb79d616e569120a/THDM/tabs/bsgammatable.dat')
def main():
    # Largest tabulated tanbeta=100 approximates the published cotbeta->0 limit.
    z=NormalDist().inv_cdf(.95); exp=3.43e-4; err=math.hypot(.21,.07)*1e-4
    def br(m): return table_reference(TABLE,2.,math.log10(m))
    def pull(m): return (br(m)-exp)/math.hypot(err,.07*br(m))
    lo,hi=300.,800.
    assert pull(lo)>z>pull(hi)
    for _ in range(60):
        mid=(lo+hi)/2
        if pull(mid)>z: lo=mid
        else: hi=mid
    result={'source':'1503.01789v2 Eq(1),(11); 1702.04571v1 Sec5 identifies historical one-sided prescription',
            'prescription':'Gaussian confidence belt lower edge theory-z95*sqrt(exp_variance+(0.07*theory)^2); table only',
            'measurement':exp,'experimental_sigma':err,'z95':z,'tanbeta':100.,'mass_root_GeV':(lo+hi)/2,
            'published_rounded_bound_GeV':480,'BR_at_480':br(480),'pull_at_480':pull(480),
            'table_sha256':sha(TABLE),'Zee_transfer':False}
    (HERE/'ONE_STATE_CONFIDENCE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
