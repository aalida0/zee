"""No-scan final orchestration tests: saved records and mock kernels only."""
import copy
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from module14 import scan
from module14.collect import collect
from module14.final_config import PHYSICS_SCOPE, validate, validate_manifest, worker_settings
from module14.final_workflow import preflight, require_preflight, source_files
from module14.final_export import export
from module14.final_plot import plot
from module14.fixtures.replay import saved, materialize
from module14.conditional_scan.workflow import join, load, production
from module14.public_reuse import probe


def mock_config():
    c = load('module14/final_config_template.json')
    c.update(source_commit='1'*40, count=2, seed=20261103, shard_size=1)
    c['arms'][0].update(name='wide_uniform', weight=1)
    c['arms'].append(copy.deepcopy(c['arms'][0])); c['arms'][1]['name']='moderate_uniform'
    return c


class ConfigTests(unittest.TestCase):
    def test_frozen_physics_overrides_rejected_before_runtime(self):
        for name in ('spheno', 'spheno_full_loop', 'higgs_hard_veto', 'lfv_hard_veto',
                     'bsgamma_hard_veto', 'vacuum_unknown_is_fail'):
            for location in ('stages', 'runtime', None):
                c=mock_config(); target=c if location is None else c[location]
                target[name]=True
                with self.subTest(name=name, location=location), self.assertRaises(ValueError):
                    validate(c)
        c=mock_config()
        with tempfile.TemporaryDirectory() as tmp, patch('module14.final_workflow.check_source',return_value=c['source_commit']):
            r=preflight(c,'local',tmp)
            self.assertEqual(r['physics_scope'],PHYSICS_SCOPE)
            self.assertEqual(r['physics_scope']['spheno_full_loop'],'UNAVAILABLE')
            r['physics_scope']['hard_filters'].append('spheno_full_loop')
            r['report_sha256']=scan.digest({k:v for k,v in r.items() if k!='report_sha256'})
            with self.assertRaises(ValueError):require_preflight(c,r)

    def test_template_deliberately_incomplete_and_strict_config(self):
        with self.assertRaises(ValueError): validate(load('module14/final_config_template.json'))
        c = mock_config(); self.assertEqual(validate(c), c)
        variants = []
        for key, value in [('extra', 0), ('count', True), ('seed', -1), ('shard_size', 3), ('families', 0), ('perturbativity_limit', float('nan')), ('source_commit', 'main')]:
            d=copy.deepcopy(c); d[key]=value; variants.append(d)
        for key, bounds in [('gamma',[-2,2]), ('tanbeta',[0,5]), ('mH1_fraction',[.4,1]), ('mH2',[10,20]), ('mh2_splitting',[-10000,0]), ('k1',[1,0])]:
            d=copy.deepcopy(c);d['arms'][0]['ranges'][key]=bounds;variants.append(d)
        d=copy.deepcopy(c);d['arms'][1]['name']='wide_uniform';variants.append(d)
        d=copy.deepcopy(c);d['stages']['lfv']=False;d['stages']['lfv_tree']=True;variants.append(d)
        d=copy.deepcopy(c);d['stages']['higgs']=True;variants.append(d)
        d=copy.deepcopy(c);d['runtime']['cpus']=2;variants.append(d)
        d=copy.deepcopy(c);d['runtime']['packages']['numpy']='latest';variants.append(d)
        d=copy.deepcopy(c);d['template_sha256']='0'*64;variants.append(d)
        for d in variants:
            with self.subTest(d=d), self.assertRaises(ValueError): validate(d)

    def test_preflight_filesystem_runtime_and_failure_injection(self):
        c=mock_config()
        with tempfile.TemporaryDirectory() as tmp, patch('module14.final_workflow.check_source', return_value=c['source_commit']):
            r=preflight(c,'local',tmp)
            self.assertEqual(r['atomic_link'],'PASS');self.assertIsNone(r['global_acceptance'])
            self.assertEqual(r['stages']['higgs'],'NOT_EVALUATED')
            require_preflight(c,r)
            changed=copy.deepcopy(r);changed['resources']['cpus']=7
            with self.assertRaises(ValueError):require_preflight(c,changed)
            changed=copy.deepcopy(c);changed['seed']+=1
            with self.assertRaises(ValueError):require_preflight(changed,r)
            with patch('module14.final_workflow.platform.python_version',return_value='3.11.0'), self.assertRaises(ValueError):preflight(c,'local',tmp)
            with patch('module14.final_workflow.os.link',side_effect=OSError('no links')), self.assertRaises(OSError):preflight(c,'local',tmp)
            with patch('module14.final_workflow.shutil.which',return_value=None), self.assertRaises(ValueError):preflight(c,'condor',tmp)
            with patch('module14.final_workflow.shutil.disk_usage',return_value=type('Disk',(),{'free':0})()), self.assertRaises(ValueError):preflight(c,'local',tmp)

    def test_probe_is_readonly_and_never_a_physics_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=probe('general_2hdm',tmp)
            self.assertEqual(r['source_status'],'UNAVAILABLE_OR_CHANGED')
            self.assertFalse(r['operative_constraint']);self.assertEqual(r['zee_physics_status'],'UNVALIDATED')

    def test_required_binary_and_dataset_pins_fail_closed(self):
        c=mock_config();c['stages']['bsgamma']=True
        c['runtime']['binaries']={'d9b_probe':{'path':'/tmp/d14-nonexistent-fixture-binary','sha256':'0'*64}}
        with tempfile.TemporaryDirectory() as tmp,patch('module14.final_workflow.check_source',return_value=c['source_commit']):
            with self.assertRaisesRegex(ValueError,'executable'):preflight(c,'local',tmp)
            c=mock_config();c['stages']['higgs']=True;c['runtime']['packages']['HiggsTools']='1.1.3'
            c['runtime']['higgs_data']={n:{'path':str(Path(tmp)/n),'sha256':'0'*64} for n in ('HB','HS')}
            # If optional HiggsTools itself is absent, the preflight must
            # reject the runtime before inspecting absent HB/HS datasets.
            # A populated production environment reaches the dataset gate.
            with self.assertRaisesRegex(ValueError,'HiggsTools data|Missing pinned runtime package: HiggsTools'):
                preflight(c,'local',tmp)


class FrozenReplayTests(unittest.TestCase):
    def test_original_receipt_full_replay_and_repartition(self):
        with tempfile.TemporaryDirectory() as tmp:
            config, manifest, parts=materialize(Path(tmp)/'split',shard_size=25)
            report=collect(manifest,config,parts)
            self.assertEqual(report['status'],'COMPLETE');self.assertEqual(report['manifest_points'],100)
            original=saved(); out=Path(tmp)/'original.jsonl'; rec=Path(tmp)/'original.receipt.json'
            out.write_bytes(original['pilot_output.jsonl']);rec.write_bytes(original['pilot_receipt.json'])
            original_report=collect(manifest,config,[(manifest,out,rec)])
            self.assertEqual(report['cutflow'],original_report['cutflow'])
            args=(manifest,config,parts,load('module14/conditional_scan/matching_card.json'),'LOCAL_UNSPECIFIED','LOCAL_UNSPECIFIED')
            with patch('module14.scan.generate',side_effect=AssertionError('new proposal')), patch('module14.scan.scalar_gates',side_effect=AssertionError('new physics')):
                a=join(*args);b=join(manifest,config,list(reversed(parts)),*args[3:])
            self.assertEqual(a,b)
            for name, dataset in [('a',a),('b',b)]:export(dataset,Path(tmp)/name)
            self.assertEqual({p.name:p.read_bytes() for p in (Path(tmp)/'a').iterdir()}, {p.name:p.read_bytes() for p in (Path(tmp)/'b').iterdir()})
            plot(Path(tmp)/'a',Path(tmp)/'a.svg');plot(Path(tmp)/'b',Path(tmp)/'b.svg')
            self.assertEqual((Path(tmp)/'a.svg').read_bytes(),(Path(tmp)/'b.svg').read_bytes())

    def test_corruption_family_binding_nonfinite_and_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            config,manifest,parts=materialize(Path(tmp),{50,91})
            shard,out,receipt=parts[0]; original=out.read_text();base=load(receipt)
            mutations=[]
            d=json.loads(original.splitlines()[0]);d['widths'][0]['module2_input_sha256']='0'*64;mutations.append(d)
            d=json.loads(original.splitlines()[0]);d['neutrino'].reverse();mutations.append(d)
            d=json.loads(original.splitlines()[0]);d['gates']['vacuum']['assessment']='UNRECOGNIZED';mutations.append(d)
            d=json.loads(original.splitlines()[0]);d['widths'][0]['mothers']['H1']['br_tb']=float('inf');mutations.append(d)
            d=json.loads(original.splitlines()[0]);d['lfv'].pop();mutations.append(d)
            for d in mutations:
                out.write_text(json.dumps(d)+'\n'+original.splitlines()[1]+'\n')
                rec=copy.deepcopy(base);rec['output_sha256']=scan.file_sha(out);receipt.write_text(scan.encode(rec))
                with self.assertRaises(ValueError):collect(manifest,config,parts)
            out.write_text(original);receipt.write_text('{')
            with self.assertRaises(ValueError):collect(manifest,config,parts)


class FinalMockWorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.config=mock_config();self.config['shard_size']=2
        # Existing exact coordinates/Yukawas. Only synthetic receipt/ID metadata
        # is changed to exercise the final contract; no RNG or kernel is called.
        raw=saved(); manifest=[json.loads(s) for s in raw['pilot_manifest.jsonl'].splitlines()]
        results={r['id']:r for r in map(json.loads,raw['pilot_output.jsonl'].splitlines())}
        self.rows=[];self.results=[]
        for new,old in enumerate((50,91)):
            row=copy.deepcopy(next(r for r in manifest if r['id']==old));row.update(id=new,config_sha256=scan.digest(self.config));self.rows.append(row)
            result=copy.deepcopy(results[old]);result.update(id=new,config_sha256=scan.digest(self.config))
            for n in result['neutrino']:n['seed_sha256']=scan.digest(['d14-neutrino-v1',self.config['seed'],new,n['ordering'],n['family']])
            self.results.append(result)
        self.manifest=self.root/'manifest.jsonl';self.manifest.write_text(''.join(scan.encode(r)+'\n' for r in self.rows))
        validate_manifest(self.manifest,self.config)
        with patch('module14.final_workflow.check_source',return_value=self.config['source_commit']):self.report=preflight(self.config,'local',self.root)
        self.reportpath=self.root/'preflight.json';self.reportpath.write_text(scan.encode(self.report))
        self.output=self.root/'output.jsonl';self.receipt=self.root/'receipt.json'

    def run_mock(self,resume=False):
        outputs=self.results
        class Decays:
            def __init__(self,*args):pass
            def evaluate(self,n):return copy.deepcopy(next(w for r in outputs for w in r['widths'] if w['module2_input_sha256']==n['input_sha256']))
        def family(row,seed,ordering,index,limit):return copy.deepcopy(next(n for n in outputs[row['id']]['neutrino'] if n['ordering']==ordering and n['family']==index))
        def lfv(n,*args):return copy.deepcopy(next(w for r in outputs for w in r['lfv'] if w['module2_input_sha256']==n['input_sha256']))
        with patch.dict(os.environ,{'ZEE_D14_SOURCE_COMMIT':self.config['source_commit'],'ZEE_D14_BUNDLE_SHA256':'b'*64,'ZEE_D14_MANIFEST_SHA256':scan.file_sha(self.manifest)}), \
             patch('module14.scan.scalar_gates',side_effect=lambda r:copy.deepcopy(outputs[r['id']]['gates'])), \
             patch('module14.scan.evaluate_family',side_effect=family),patch('module14.decays.DecayCalculation',Decays), \
             patch('module14.lfv.evaluate_family',side_effect=lfv),patch('module14.scan.neutrino_input',side_effect=AssertionError('RNG forbidden')):
            return scan.run(self.manifest,self.output,self.receipt,self.config,resume=resume,preflight_report=self.reportpath,**{'limit' if k=='perturbativity_limit' else k:v for k,v in worker_settings(self.config).items()})

    def test_final_mock_pipeline_resume_export_and_failures(self):
        self.run_mock();self.assertEqual([json.loads(s) for s in self.output.read_text().splitlines()],self.results)
        self.run_mock(resume=True)
        parts=[(self.manifest,self.output,self.receipt)]
        kwargs=dict(source_commit=self.config['source_commit'],source_bundle_sha256='b'*64,preflight_report=self.report)
        self.assertEqual(collect(self.manifest,self.config,parts,**kwargs)['status'],'COMPLETE')
        dataset=join(self.manifest,self.config,parts,load('module14/conditional_scan/matching_card.json'),**kwargs)
        self.assertEqual(export(dataset,self.root/'export')['rows'],8)
        for r in map(json.loads,(self.root/'export/families.jsonl').read_text().splitlines()):
            self.assertIsNone(r['cascade_tb_13_pb']);self.assertIsNone(r['global_acceptance'])
        original=load(self.receipt)
        for field,value in [('lfv_enabled',False),('worker_sha256','0'*64),('final_preflight_sha256','0'*64),('source_bundle_sha256','c'*64),('manifest_sha256','0'*64)]:
            rec=copy.deepcopy(original);rec[field]=value;self.receipt.write_text(scan.encode(rec))
            with self.assertRaises(ValueError):collect(self.manifest,self.config,parts,**kwargs)
        self.receipt.write_text(scan.encode(original));self.receipt.unlink()
        with self.assertRaises(FileExistsError):self.run_mock(resume=True)

    def test_source_bound_two_energy_product_and_contract_falsifiers(self):
        self.run_mock();parts=[(self.manifest,self.output,self.receipt)]
        dataset=join(self.manifest,self.config,parts,load('module14/conditional_scan/matching_card.json'),self.config['source_commit'],'b'*64,preflight_report=self.report)
        contracts={str(e):{'energy_TeV':e,'process':'pp_tbH2','charge_definition':'both','order':'LO','pdf':'SYNTHETIC_FIXTURE','scale_scheme':'fixed H2 mass'} for e in (13,14)}
        directory=self.root/'production';directory.mkdir();(directory/'evidence.txt').write_text('Mock only; not a measured rate')
        row=dataset['rows'][0];n=row['neutrino']
        for e in ('13','14'):
            card={**contracts[e],'model':'ZeeTypeII','state':'H2','sigma_pb':1.,'scalar_sha256':row['scalar_sha256'],'yukawa_sha256':{k:scan.digest(n[k]) for k in ('F','D','Ye','Ye2')},'module2_input_sha256':n['input_sha256'],'documentation':'Mock fixture','uncertainty':'unknown','artifacts_sha256':{'evidence.txt':scan.file_sha(directory/'evidence.txt')}}
            path=directory/(n['input_sha256']+'.'+e+'TeV.json');path.write_text(scan.encode(card))
        export(dataset,self.root/'enriched',directory,contracts)
        rows=list(map(json.loads,(self.root/'enriched/families.jsonl').read_text().splitlines()));r=next(r for r in rows if r['module2_input_sha256']==n['input_sha256'])
        self.assertEqual(r['cascade_tb_13_pb'],r['BR_H2_H1Z']*r['BR_H1_tb']);self.assertEqual(r['rank_14'],1)
        # Adverse optional diagnostics must not veto an otherwise rankable family.
        row['lfv']={'status':'FAIL','comparison_status':'DIAGNOSTIC_ONLY'}
        row['higgstools']={'status':'FAIL','comparison_status':'DIAGNOSTIC_ONLY'}
        row['flavor']['bsg_nominal_classification']='FAIL'
        export(dataset,self.root/'adverse-diagnostics',directory,contracts)
        adverse=next(json.loads(line) for line in (self.root/'adverse-diagnostics/families.jsonl').read_text().splitlines()
                     if json.loads(line)['module2_input_sha256']==n['input_sha256'])
        for field in ('rank_13','rank_14','cascade_tb_13_pb','cascade_tb_14_pb','global_acceptance'):
            self.assertEqual(adverse[field],r[field])
        path=directory/(n['input_sha256']+'.13TeV.json');original=load(path)
        for field,value in [('energy_TeV',14),('pdf','wrong'),('scale_scheme','wrong'),('process','wrong'),('order','NLO'),('charge_definition','plus'),('sigma_pb',0),('module2_input_sha256','0'*64)]:
            card=dict(original);card[field]=value;path.write_text(scan.encode(card))
            with self.assertRaises(ValueError):production(path,row['input_card'],n,contracts['13'])

    def test_computational_error_cannot_be_final_complete(self):
        n=self.results[0]['neutrino'][0];n.update(status='ERROR',closure_status='ERROR')
        self.run_mock()
        parts=[(self.manifest,self.output,self.receipt)]
        kwargs=dict(source_commit=self.config['source_commit'],source_bundle_sha256='b'*64,preflight_report=self.report)
        result=collect(self.manifest,self.config,parts,**kwargs)
        self.assertEqual(result['status'],'ERROR');self.assertGreater(result['computational_errors'],0)
        with self.assertRaises(ValueError):join(self.manifest,self.config,parts,load('module14/conditional_scan/matching_card.json'),**kwargs)

    def test_prepare_final_mock_pack_and_original_manifest_lock(self):
        import sys
        import tarfile
        from module14.condor import prepare
        configpath=self.root/'config.json';configpath.write_text(scan.encode(self.config))
        shard=self.root/'shard_000000.jsonl';shard.write_bytes(self.manifest.read_bytes())
        generation={'schema':'d14-generation-1','config_sha256':scan.digest(self.config),'source_commit':self.config['source_commit'],
                    'template_sha256':self.config['template_sha256'],'manifest_sha256':scan.file_sha(self.manifest),
                    'shards_sha256':{shard.name:scan.file_sha(shard)}}
        generationpath=self.root/'generation.json';generationpath.write_text(scan.encode(generation))
        report=copy.deepcopy(self.report);report['backend']='condor';report['report_sha256']=scan.digest({k:v for k,v in report.items() if k!='report_sha256'})
        self.reportpath.write_text(scan.encode(report))
        real_run=prepare.subprocess.run
        def archive(command,**kwargs):
            if command[:2] != ['git','archive']:return real_run(command,**kwargs)
            destination=Path(command[command.index('-o')+1])
            with tarfile.open(destination,'w:gz',pax_headers={'comment':self.config['source_commit']}) as tar:
                for name in ('worker.sh','d14.sub'):tar.add(Path(__file__).resolve().parents[1]/'module14/condor'/name,arcname='module14/condor/'+name)
        arguments=['prepare','--commit',self.config['source_commit'],'--config',str(configpath),'--manifest',str(self.manifest),
                   '--generation-receipt',str(generationpath),'--preflight-report',str(self.reportpath),'--acknowledge-conditional-physics',
                   '--shard',str(shard),'--output',str(self.root/'batch')]
        real_check_output=prepare.subprocess.check_output
        def git_read(command,**kwargs):
            return self.config['source_commit'] if command[:3]==['git','rev-parse','--verify'] else real_check_output(command,**kwargs)
        with patch.object(sys,'argv',arguments),patch('module14.condor.prepare.subprocess.check_output',side_effect=git_read), \
             patch('module14.condor.prepare.subprocess.run',side_effect=archive),patch('module14.final_workflow.check_source',return_value=self.config['source_commit']):
            prepare.main()
            pack=load(self.root/'batch/pack.json')
            self.assertEqual(pack['manifest_sha256'],scan.file_sha(self.manifest))
            self.assertIn('preflight.json',(self.root/'batch/d14.sub').read_text())
            self.assertEqual(load(self.root/'batch/job_settings.json'),worker_settings(self.config))
            generation['manifest_sha256']='0'*64;generationpath.write_text(scan.encode(generation))
            with self.assertRaisesRegex(ValueError,'generation receipt'):prepare.main()



class PackagingTests(unittest.TestCase):
    def test_job_checks_pack_and_timeout_without_launching_worker(self):
        from module14.condor import job
        import subprocess
        import sys
        c=mock_config()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shard=root/'shard_000000.jsonl';shard.write_text('mock immutable row\n')
            files={'config.json':scan.encode(c),'job_settings.json':scan.encode(worker_settings(c)),
                   'source_commit.txt':c['source_commit'],'scan_bundle.tar.gz':'mock archive','preflight.json':'mock preflight'}
            for name,data in files.items():(root/name).write_text(data)
            hashes={name:scan.file_sha(root/name) for name in files};hashes['shards/'+shard.name]=scan.file_sha(shard)
            (root/'pack.json').write_text(scan.encode({'schema':'d14-pack-1','files_sha256':hashes,'manifest_sha256':scan.file_sha(shard)}))
            previous=Path.cwd()
            try:
                os.chdir(root)
                with patch.object(sys,'argv',['job',str(shard)]),patch('module14.condor.job.subprocess.call',return_value=0) as call:
                    self.assertEqual(job.main(),0);self.assertIn('--preflight-report',call.call_args.args[0])
                    (root/'config.json').write_text(scan.encode(dict(c,seed=99)))
                    with self.assertRaises(ValueError):job.main()
                    (root/'config.json').write_text(files['config.json'])
                with patch.object(sys,'argv',['job',str(shard)]),patch('module14.condor.job.subprocess.call',side_effect=subprocess.TimeoutExpired('mock worker',1)):
                    self.assertEqual(job.main(),124)
                self.assertFalse((root/'receipt.json').exists())
            finally:os.chdir(previous)

    def test_wrapper_rejects_unsafe_archive_before_any_worker(self):
        import io
        import subprocess
        import tarfile
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('shard_000000.jsonl','config.json','job_settings.json'):(root/name).write_text('mock')
            (root/'source_commit.txt').write_text('1'*40+'\n')
            archive=root/'scan_bundle.tar.gz'
            with tarfile.open(archive,'w:gz',pax_headers={'comment':'1'*40}) as tar:
                member=tarfile.TarInfo('../escape');member.size=4;tar.addfile(member,io.BytesIO(b'mock'))
            (root/'bundle.sha256').write_text(scan.file_sha(archive)+'  scan_bundle.tar.gz\n')
            result=subprocess.run(['bash',str(Path(__file__).resolve().parents[1]/'module14/condor/worker.sh'),'shard_000000.jsonl'],cwd=root,capture_output=True,text=True)
            self.assertEqual(result.returncode,65);self.assertIn('Unsafe archive',result.stderr)
            self.assertFalse((root/'source').exists());self.assertFalse((root/'receipt.json').exists())

    def test_source_lock_dirty_and_bundle_corruption(self):
        from module14.final_workflow import check_source
        import tarfile
        c=mock_config()
        with patch('module14.final_workflow.subprocess.check_output',side_effect=[c['source_commit']+'\n',' M module14/scan.py\n']),self.assertRaises(ValueError):check_source(c)
        with tempfile.TemporaryDirectory() as tmp,patch('module14.final_workflow.check_source',return_value=c['source_commit']),patch('module14.final_workflow.source_files',return_value={}):
            archive=Path(tmp)/'bundle.tar.gz'
            with tarfile.open(archive,'w:gz',pax_headers={'comment':'2'*40}) as tar:tar.addfile(tarfile.TarInfo('mock'))
            with self.assertRaises(ValueError):preflight(c,'local',tmp,archive)
            with tarfile.open(archive,'w:gz',pax_headers={'comment':c['source_commit']}) as tar:tar.addfile(tarfile.TarInfo('mock'))
            self.assertEqual(preflight(c,'local',tmp,archive)['bundle_sha256'],scan.file_sha(archive))

if __name__ == '__main__':unittest.main()
