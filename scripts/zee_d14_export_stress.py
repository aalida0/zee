#!/usr/bin/env python3
"""Bounded-RSS export of synthetic repetitions of ONE saved family, no kernels."""
import argparse
from pathlib import Path
import resource
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from module14.conditional_scan.workflow import join, load
from module14.disk_rows import DiskRows
from module14.final_export import export
from module14.fixtures.replay import materialize
from module14.scan import encode, file_sha, digest


def run(count, limit):
    with tempfile.TemporaryDirectory(prefix='d14-stress-') as tmp:
        config,manifest,parts=materialize(Path(tmp)/'inputs',{50,91})
        data=join(manifest,config,parts,load('module14/conditional_scan/matching_card.json'),
                  'LOCAL_UNSPECIFIED','LOCAL_UNSPECIFIED',streaming=True)
        old=data['rows'];template=old[0];rows=DiskRows()
        try:
            for i in range(count):
                # Only mock identity metadata changes. Scalar and Yukawas are
                # the exact same immutable original family at every iteration.
                row=dict(template,id=i)
                rows.append(row)
            data['rows']=rows
            # Synthetic source-bound sidecars exercise both ranking partitions.
            # These test rates are never real production inputs or retained.
            prod=Path(tmp)/'mock-production';prod.mkdir()
            artifact=prod/'SYNTHETIC.txt';artifact.write_text('Mock rate only; no production calculation')
            contracts={}
            n=template['neutrino']
            for energy in ('13','14'):
                contract={'energy_TeV':int(energy),'process':'SYNTHETIC','charge_definition':'SYNTHETIC',
                          'order':'SYNTHETIC','pdf':'SYNTHETIC','scale_scheme':'SYNTHETIC'}
                contracts[energy]=contract
                card={**contract,'model':'ZeeTypeII','state':'H2','sigma_pb':1.,
                      'scalar_sha256':template['scalar_sha256'],'module2_input_sha256':n['input_sha256'],
                      'yukawa_sha256':{k:digest(n[k]) for k in ('F','D','Ye','Ye2')},
                      'documentation':'Synthetic repeated-record memory test','uncertainty':'SYNTHETIC',
                      'artifacts_sha256':{artifact.name:file_sha(artifact)}}
                (prod/(n['input_sha256']+f'.{energy}TeV.json')).write_text(encode(card))
            receipt=export(data,Path(tmp)/'export',prod,contracts)
            import json
            with (Path(tmp)/'export/families.jsonl').open() as f:
                for index,line in enumerate(f,1):
                    row=json.loads(line)
                    if row['rank_13']!=index or row['rank_14']!=index:
                        raise ValueError('Synthetic tie ordering/ranking regression')
            peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if peak>limit*1024:raise ValueError(f'RSS {peak} KiB exceeds {limit} MiB')
            return {'mock_rows':count,'max_rss_KiB':peak,'limit_MiB':limit,
                    'export_rows':receipt['rows'],'mock_ranked_channels':2,'status':'PASS','physics_evaluations':0,
                    'code_sha256':{n:file_sha(n) for n in ('module14/disk_rows.py','module14/final_export.py','module14/conditional_scan/workflow.py','scripts/zee_d14_export_stress.py')}}
        finally:
            old.close();rows.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rows',type=int,required=True);p.add_argument('--limit-mib',type=int,default=256)
    a=p.parse_args();print(encode(run(a.rows,a.limit_mib)))
