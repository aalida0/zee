#!/usr/bin/env python3
"""Regress F21c rescue from F21b real failure, no physics rescan."""
import argparse,csv,hashlib,io,json,math,sys,tarfile,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_paper1_F21c_resume_saved_scalar_archive import (
    original_scalar_archive,select_stratified,REQUIRED_FIELDS)

def fixture(folder,*,bad_key=False,bad_sha=False):
    inputs={}
    for name in ("f18","f19","f19b","f19c","f19d","f20_csv","f20_summary"):
        p=folder/(name+".txt")
        p.write_text(name+" original source marker")
        inputs[name]=p
    p=dict(mH1=360.,mH2=980.,mh2=940.,ma=960.,
           beta=1.39,alpha=1.39,gamma=1.1,m12sq=1.e5,
           lc=2.,k1=1.,k2=.8,k12=.1)
    records=[]
    for i in range(4):
        r={"id":f"F21_s3_{i:07d}",
           "candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED",
           "flavor_and_HiggsTools_applied":False,
           "full_Zee_allowed_or_excluded":None,
           "shard":3,
           "tanbeta":math.tan(p["beta"]),
           "max_unitarity":7.7,
           "chi2_Gfitter":.5,"chi2_PDG":.7,
           "production_weighted_nonleptonic_cascade_upper_proxy":.47-.01*i,
           "LO_flavor_shift_x1e4_NOT_CL":.33+.01*i,
           "LO_flavor_BR_x1e4_NOT_CL":3.87+.01*i,
           "LO_flavor_C7_NOT_CL":-.03,
           "LO_flavor_C8_NOT_CL":-.04,
           **{**p,"mH2":p["mH2"]+30*i}}
        if bad_key:r.pop("production_weighted_nonleptonic_cascade_upper_proxy")
        records.append(r)
    f=io.StringIO()
    w=csv.DictWriter(f,fieldnames=list(records[0]),extrasaction="ignore")
    w.writeheader();w.writerows(records)
    csv_bytes=f.getvalue().encode()
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest={
        "status":"F21_RUNNING_NOT_ALLOWED","shard":3,
        "requested_independent_stratified_draws":6000,
        "requested_local_custodial_draws":4000,
        "full_model_allowed":None,
        "original_F18_through_F19d_sha256":{
          n:sha(inputs[n]) for n in ("f18","f19","f19b","f19c","f19d")},
        "F20_merged_csv_SHA256":sha(inputs["f20_csv"]),
        "F20_merged_summary_SHA256":(
            "0"*64 if bad_sha else sha(inputs["f20_summary"]))}
    arch=folder/"F21_result_shard_3.tar.gz"
    with tarfile.open(arch,"w:gz") as t:
        for filename,data in (
           ("F21_manifest_start.json",json.dumps(manifest).encode()),
           ("F21_WIDE_all_scalar_LO_screen_NOT_ALLOWED.csv",csv_bytes)):
            name="results/F21_shard_3/"+filename
            info=tarfile.TarInfo(name);info.size=len(data)
            t.addfile(info,io.BytesIO(data))
    return argparse.Namespace(shard=3,global_draws=6000,local_draws=4000,
        original_scalar_archive=arch,quad=64,
        **inputs)

class TestF21cRestoreScalar(unittest.TestCase):
    def test_actual_f21b_bug_is_resolved_on_saved_b4_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            args=fixture(Path(temp))
            records,manifest,raw,archive_sha=original_scalar_archive(
                args,check_actual=False)
            self.assertEqual(len(records),4)
            self.assertTrue(raw.startswith(b"id,"))
            self.assertTrue(raw.endswith(b"\r\n") or raw.endswith(b"\n"))
            chosen=select_stratified(records,3)
            self.assertEqual(len(chosen),3)
            self.assertEqual({x["id"] for x in chosen},
                {"F21_s3_0000000","F21_s3_0000001","F21_s3_0000002"})
            self.assertEqual(len(archive_sha),64)
    def test_fail_closed_missing_original_scalar_column(self):
        with tempfile.TemporaryDirectory() as temp:
            args=fixture(Path(temp),bad_key=True)
            with self.assertRaisesRegex(ValueError,"incomplete numeric scalar source"):
                original_scalar_archive(args,check_actual=False)
    def test_fail_closed_corrupted_original_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            args=fixture(Path(temp),bad_sha=True)
            with self.assertRaisesRegex(ValueError,"archived F20 provenance"):
                original_scalar_archive(args,check_actual=False)

if __name__=="__main__":unittest.main()
