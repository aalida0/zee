"""Record actual installed bytes and concrete public-interface failures."""
import importlib.metadata as md
import json
import platform
import shutil
from pathlib import Path
from pilot import HERE, ROOT, digest, write_json, flavio
from wilson import Wilson


def capture(call):
    try:
        call()
        return {'status':'UNEXPECTED_SUCCESS'}
    except Exception as e:
        return {'status':'REJECTED','exception':type(e).__name__,'message':str(e)}


def main():
    base=Path(flavio.__file__).parent.parent
    patterns=['flavio/physics/bdecays/bxgamma.py','flavio/physics/bdecays/wilsoncoefficients.py',
              'flavio/physics/eft.py','flavio/physics/data/wcsm/wc_sm_dB1_2_55.npy',
              'flavio/data/config.yml','flavio/data/parameters*.yml',
              'flavio-*.dist-info/licenses/*','wilson-*.dist-info/licenses/*',
              'wilson/run/wet/*.py','wilson/translate/wet.py','wilson/wcxf/bases/wet.*.basis.json',
              '_eos*.so']
    installed={str(p.relative_to(base)):digest(p) for pat in patterns for p in base.glob(pat) if p.is_file()}
    external={}
    refs={
        'eos_bsgamma.cc':'https://raw.githubusercontent.com/eos/eos/v1.0.21/eos/rare-b-decays/inclusive-b-to-s-gamma.cc',
        'eos_bsgamma_TEST.cc':'https://raw.githubusercontent.com/eos/eos/v1.0.21/eos/rare-b-decays/inclusive-b-to-s-gamma_TEST.cc',
        'eos_wet.cc':'https://raw.githubusercontent.com/eos/eos/v1.0.21/eos/models/wet.cc',
        'eos_LICENSE':'https://raw.githubusercontent.com/eos/eos/v1.0.21/LICENSE',
        'eos_v1.1_bsgamma.cc':'https://raw.githubusercontent.com/eos/eos/v1.1/eos/rare-b-decays/inclusive-b-to-s-gamma.cc',
        'eos_v1.1_wet.cc':'https://raw.githubusercontent.com/eos/eos/v1.1/eos/models/wet.cc',
    }
    hep=json.loads((HERE/'local/hepfit_head.json').read_text())['sha']
    for name,path in [('matching.cpp','FlavourWilsonCoefficient/src/FlavourWilsonCoefficientMatching.cpp'),
                      ('bsgamma.cpp','Flavour/src/bsgamma.cpp'),('README.md','README.md'),
                      ('LICENSE','doc/LICENSE'),('COPYING','doc/COPYING')]:
        refs['hepfit_'+name]=f'https://raw.githubusercontent.com/silvest/HEPfit/{hep}/{path}'
    for name,url in refs.items():
        p=HERE/'local'/name
        external[name]={'url':url,'sha256':digest(p)}
    def flavio_c4():
        w=flavio.WilsonCoefficients();w.set_initial({'C4_bs':1e-5},160)
    def eos_high_scale():
        Wilson({'b->s::c4':1e-5},160,'WET','EOS').match_run(4.2,'WET','EOS')
    inventory={
        'python':platform.python_version(),'platform':platform.platform(),
        'versions':{d.metadata['Name']:d.version for d in md.distributions()},
        'installed_sha256':installed,'external_sources':external,'HEPfit_commit':hep,
        'latest_upstream_release_tags':{n:json.loads((HERE/'local'/f'{n}_latest_release.json').read_text())['tag_name'] for n in ['eos','flavio']},
        'flavio_C4_initialization':capture(flavio_c4),
        'wilson_EOS_high_scale_running':capture(eos_high_scale),
        'HEPfit_ROOT_config_executable':shutil.which('root-config'),
        'licenses':{'flavio':'MIT','wilson':'MIT','EOS':'GPL-2.0',
                    'HEPfit':'GPL-3.0-or-later'},
        'local_implementation_sha256':{str(p.relative_to(ROOT)):digest(p) for p in
                                      [HERE/'pilot.py',HERE/'test_pilot.py',HERE/'provenance.py',ROOT/'scripts/zee_module5_bmu_nlo.py']},
    }
    write_json(HERE/'inventory.json',inventory)
    print(json.dumps({k:inventory[k] for k in ['latest_upstream_release_tags','flavio_C4_initialization','wilson_EOS_high_scale_running']}))

if __name__=='__main__':main()
