"""Offline regression tests for official KIT TTP12-029 source intake."""
from __future__ import annotations
from io import BytesIO
from urllib.error import HTTPError
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
from unittest.mock import patch
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1q_fetch_kit_source import (
    CATALOGUE,OFFICIAL_DIRECTORY,discover_from_directory,find_named_source,
    require_official_url,resolve_catalogue_source,retrieve
)
from gateA1q_author_reference_intake import SYMBOLS

KIT_SOURCE="https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/c2HDM.m"

def html_listing():
    return """<html><h3>TTP12-030: <a href="other.m">Source</a></h3>
    <h3>TTP12-029: <a href="/Progdata/ttp12/ttp12-029/readme.pdf">README</a>
    <a href="/Progdata/ttp12/ttp12-029/c2HDM.m">Source</a></h3>
    <h3>TTP12-028: <a href="other2.m">Source</a></h3></html>"""

def fixture_bytes():
    return (("(* SYNTHETIC ONLY - NEVER THE ORIGINAL AUTHORS' FILE *)\n"
             +"\n".join(f"{symbol}[0] := 0;" for symbol in SYMBOLS)
             +"\n"+("x=1;"*170)).encode())

class TestA1QSourceDownload(unittest.TestCase):
    def test_catalogue_source_link_is_exact_entry(self):
        self.assertEqual(resolve_catalogue_source(html_listing()),KIT_SOURCE)
    def test_missing_source_link_blocks(self):
        with self.assertRaisesRegex(ValueError,"Source link"):
            resolve_catalogue_source("<h3>TTP12-029: README</h3>"
                "<h3>TTP12-030: <a href='other'>Source</a></h3>")
    def test_other_site_or_http_rejected(self):
        for url in ("https://evil.example.org/c2HDM.m",
                    "http://www.ttp.kit.edu/Progdata/c2HDM.m",
                    "https://www.ttp.kit.edu.evil.example.org/c2HDM.m"):
            with self.assertRaisesRegex(ValueError,"non-HTTPS or non-KIT"):
                require_official_url(url)
    def test_direct_source_plain_m(self):
        data=fixture_bytes()
        got,name,fmt=find_named_source(data,KIT_SOURCE)
        self.assertEqual(got,data)
        self.assertEqual(name,"c2HDM.m")
        self.assertEqual(fmt,"plain Mathematica")
    def test_tar_nested_entry_only_without_extraction(self):
        data=fixture_bytes()
        bio=BytesIO()
        with tarfile.open(fileobj=bio,mode="w:gz") as t:
            member=tarfile.TarInfo("source/TTP12-029/c2HDM.m")
            member.size=len(data)
            t.addfile(member,BytesIO(data))
        got,name,fmt=find_named_source(
            bio.getvalue(),"https://www.ttp.kit.edu/Progdata/ttp12/source.tar.gz")
        self.assertEqual(got,data)
        self.assertIn("source/",name)
        self.assertEqual(fmt,"TAR")
    def test_zip_multiple_sources_block(self):
        bio=BytesIO()
        with zipfile.ZipFile(bio,"w") as z:
            z.writestr("one/c2HDM.m",fixture_bytes())
            z.writestr("two/c2HDM.m",fixture_bytes())
        with self.assertRaisesRegex(ValueError,"exactly one"):
            find_named_source(bio.getvalue(),
                "https://www.ttp.kit.edu/Progdata/ttp12/source.zip")
    def test_directory_source_listing(self):
        listing='<a href="c2HDM.m">c2HDM.m</a>'
        base="https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/"
        self.assertEqual(discover_from_directory(listing,base),KIT_SOURCE)
    def test_synthetic_retrieval_never_claims_nnlo_validation(self):
        data=fixture_bytes()
        def fake_download(url):
            if url==CATALOGUE:
                return html_listing().encode(),CATALOGUE,"text/html"
            if url==KIT_SOURCE:
                return data,KIT_SOURCE,"text/plain"
            raise ValueError("Unexpected URL "+url)
        with tempfile.TemporaryDirectory() as d:
            with patch("gateA1q_fetch_kit_source.download_official",
                       side_effect=fake_download):
                out=retrieve(CATALOGUE,Path(d))
            self.assertEqual(out["c2HDM_m_sha256"],
                             hashlib.sha256(data).hexdigest())
            self.assertFalse(out["NNLO_matching_validated"])
            self.assertFalse(out["physical_BtoXs_gamma_validated"])
            self.assertIsNone(out["Zee_benchmark_excluded"])
            self.assertEqual((Path(d)/"c2HDM.m").read_bytes(),data)
            self.assertEqual(json.loads(
                (Path(d)/"kit_source_provenance.json").read_text()
            )["status"],"GATE_A1Q_KIT_ORIGINAL_SOURCE_FETCHED_NOT_EVALUATED")
    def test_catalogue_403_falls_back_to_verified_kit_directory(self):
        data=fixture_bytes()
        directory_html='<a href="c2HDM.m">c2HDM.m</a>'
        def fake_download(url):
            if url==CATALOGUE:
                raise HTTPError(url,403,"Forbidden",{},None)
            if url==OFFICIAL_DIRECTORY:
                return directory_html.encode(),OFFICIAL_DIRECTORY,"text/html"
            if url==KIT_SOURCE:
                return data,KIT_SOURCE,"text/plain"
            raise ValueError("Unexpected URL "+url)
        with tempfile.TemporaryDirectory() as d:
            with patch("gateA1q_fetch_kit_source.download_official",
                       side_effect=fake_download):
                result=retrieve(CATALOGUE,Path(d))
            self.assertEqual(result["source_resolution_route"],
                "KIT_OFFICIAL_TTP12_029_DIRECTORY_INDEX")
            self.assertIn("403",result["catalogue_fallback_reason"])
            self.assertEqual((Path(d)/"c2HDM.m").read_bytes(),data)
            self.assertFalse(result["NNLO_matching_validated"])

    def test_existing_different_file_not_overwritten(self):
        def fake_download(url):
            if url==CATALOGUE:
                return html_listing().encode(),CATALOGUE,"text/html"
            return fixture_bytes(),KIT_SOURCE,"text/plain"
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"c2HDM.m"
            p.write_text("preexisting unrecognized file")
            with patch("gateA1q_fetch_kit_source.download_official",
                       side_effect=fake_download):
                with self.assertRaisesRegex(ValueError,"refusing to overwrite"):
                    retrieve(CATALOGUE,Path(d))
            self.assertEqual(p.read_text(),"preexisting unrecognized file")

if __name__=="__main__":
    unittest.main()
