#!/usr/bin/env python3
"""Gate A1Q: retrieve original KIT TTP12-029 'Source' artifact safely.

Only hyperlinks discovered from the OFFICIAL KIT TTP12-029 catalogue
are used; no guessed download filename and no physics formulas patched.
This tool does not evaluate Mathematica and cannot validate the BR.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
import re
import tarfile
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError,URLError
from urllib.request import Request, urlopen
import zipfile

CATALOGUE="https://www.ttp.kit.edu/progdata"
OFFICIAL_DIRECTORY="https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/"
OFFICIAL_HOSTS=("www.ttp.kit.edu","ttp.kit.edu")
EXPECTED_NAME="c2HDM.m"
MAX_ARTIFACT_BYTES=30_000_000

class SourceLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tokens=[]
        self.link=None
        self.labels=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            self.link=dict(attrs).get("href")
            self.labels=[]
    def handle_data(self,data):
        if self.link is not None:
            self.labels.append(data)
        elif data.strip():
            self.tokens.append((data.strip(),None))
    def handle_endtag(self,tag):
        if tag=="a" and self.link is not None:
            self.tokens.append((" ".join(self.labels).strip(),self.link))
            self.link=None
            self.labels=[]

def resolve_catalogue_source(html,catalogue=CATALOGUE):
    p=SourceLinks()
    p.feed(html)
    mark=None
    for idx,(label,href) in enumerate(p.tokens):
        if "TTP12-029" in label.upper():
            mark=idx
            break
    if mark is None:
        raise ValueError("Official catalogue lacks TTP12-029 entry")
    for label,href in p.tokens[mark:mark+35]:
        if re.search(r"TTP\d\d-\d{2,3}",label,re.I) and "TTP12-029" not in label.upper():
            break
        if href and re.fullmatch(r"\s*Source\s*",label,re.I):
            u=urljoin(catalogue,href)
            require_official_url(u)
            return u
    raise ValueError("Cannot uniquely resolve TTP12-029 Source link")

def require_official_url(url):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname not in OFFICIAL_HOSTS or p.username or p.password:
        raise ValueError("Refusing non-HTTPS or non-KIT Source URL: "+url)

def download_official(url):
    require_official_url(url)
    req=Request(url,headers={"User-Agent":"GateA1Q-research-provenance/1.0"})
    with urlopen(req,timeout=35) as res:
        resolved=res.geturl()
        require_official_url(resolved)
        raw=res.read(MAX_ARTIFACT_BYTES+1)
        if len(raw)>MAX_ARTIFACT_BYTES:
            raise ValueError("Original source archive exceeds intake size limit")
        kind=res.headers.get("Content-Type","")
    if not raw:
        raise ValueError("Empty original source response")
    return raw,resolved,kind

def find_named_source(raw,url):
    """Never extract archive paths. Only read c2HDM.m bytes in memory."""
    lower=urlparse(url).path.lower()
    if raw[:2]==b"\x1f\x8b" and (lower.endswith(".gz") and
                                   not lower.endswith((".tar.gz",".tgz"))):
        data=gzip.decompress(raw)
        return data,urlparse(url).path.rsplit("/",1)[-1],"gzip"
    if zipfile.is_zipfile(BytesIO(raw)):
        with zipfile.ZipFile(BytesIO(raw)) as archive:
            matches=[info for info in archive.infolist()
                     if not info.is_dir() and Path(info.filename).name==EXPECTED_NAME]
            if len(matches)!=1:
                raise ValueError("Require exactly one c2HDM.m in ZIP")
            if matches[0].file_size>MAX_ARTIFACT_BYTES:
                raise ValueError("Mathematica file too large")
            return archive.read(matches[0]),matches[0].filename,"ZIP"
    try:
        with tarfile.open(fileobj=BytesIO(raw),mode="r:*") as archive:
            matches=[m for m in archive.getmembers()
                     if m.isfile() and Path(m.name).name==EXPECTED_NAME]
            if len(matches)!=1:
                raise ValueError("Require exactly one c2HDM.m in TAR")
            if matches[0].size>MAX_ARTIFACT_BYTES:
                raise ValueError("Mathematica file too large")
            content=archive.extractfile(matches[0])
            if content is None:
                raise ValueError("Cannot extract Mathematica source")
            return content.read(),matches[0].name,"TAR"
    except tarfile.ReadError:
        pass
    if lower.endswith(".m"):
        return raw,EXPECTED_NAME,"plain Mathematica"
    return None,None,"HTML_OR_UNKNOWN"

def discover_from_directory(html,base):
    p=SourceLinks()
    p.feed(html)
    hits=[]
    for label,href in p.tokens:
        if not href:
            continue
        target=urljoin(base,href)
        if (urlparse(target).path.rsplit("/",1)[-1]==EXPECTED_NAME
                and urlparse(target).path.startswith("/Progdata/ttp12/ttp12-029/")):
            require_official_url(target)
            hits.append(target)
    if len(set(hits))!=1:
        raise ValueError("Source listing lacks a unique c2HDM.m download")
    return hits[0]

def retrieve(catalogue,output):
    # The new KIT catalogue may deny scripted access (HTTP 403).
    # Fallback to the known official supplementary directory
    # documented by its public readme URL; inspect its index for the
    # actual c2HDM.m link rather than guessing an archive name.
    fallback_reason=None
    resolution="KIT_CATALOGUE_TTP12_029_SOURCE_LINK"
    try:
        html,final_catalogue,_=download_official(catalogue)
        source=resolve_catalogue_source(html.decode("utf-8"),final_catalogue)
    except (HTTPError,URLError,ValueError,UnicodeDecodeError) as exc:
        fallback_reason=str(exc)
        resolution="KIT_OFFICIAL_TTP12_029_DIRECTORY_INDEX"
        html,final_catalogue,_=download_official(OFFICIAL_DIRECTORY)
        source=discover_from_directory(html.decode("utf-8"),final_catalogue)
    raw,resolved,typ=download_official(source)
    file_raw,archive_entry,format_type=find_named_source(raw,resolved)
    if file_raw is None:
        # KIT Source may lead to Apache autoindex instead of a file.
        target=discover_from_directory(raw.decode("utf-8"),resolved)
        raw,resolved,typ=download_official(target)
        file_raw,archive_entry,format_type=find_named_source(raw,resolved)
        if file_raw is None:
            raise ValueError("Source URL returned neither archive nor c2HDM.m")
    if len(file_raw)>MAX_ARTIFACT_BYTES:
        raise ValueError("Decompressed Mathematica source is too large")
    from gateA1q_author_reference_intake import original_reference_presence
    output.mkdir(parents=True,exist_ok=True)
    dest=output/EXPECTED_NAME
    # Validate expected Mathematica symbols before writing bytes.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        probe=Path(d)/EXPECTED_NAME
        probe.write_bytes(file_raw)
        intake=original_reference_presence(probe)
    if dest.exists() and dest.read_bytes()!=file_raw:
        raise ValueError("Existing c2HDM.m differs; refusing to overwrite")
    dest.write_bytes(file_raw)
    manifest={
        "status":"GATE_A1Q_KIT_ORIGINAL_SOURCE_FETCHED_NOT_EVALUATED",
        "catalogue_url":catalogue,
        "resolved_source_url":resolved,
        "source_resolution_route":resolution,
        "catalogue_fallback_reason":fallback_reason,
        "downloaded_artifact_sha256":hashlib.sha256(raw).hexdigest(),
        "downloaded_artifact_size_bytes":len(raw),
        "format":format_type,
        "source_entry":archive_entry,
        "c2HDM_m_sha256":hashlib.sha256(file_raw).hexdigest(),
        "c2HDM_m_size_bytes":len(file_raw),
        "symbol_coverage":intake["symbol_coverage"],
        "original_source_numerically_evaluated":False,
        "NNLO_matching_validated":False,
        "physical_BtoXs_gamma_validated":False,
        "Zee_benchmark_allowed":None,
        "Zee_benchmark_excluded":None,
    }
    (output/"kit_source_provenance.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--catalogue-url",default=CATALOGUE)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    require_official_url(a.catalogue_url)
    result=retrieve(a.catalogue_url,a.output_dir)
    print("STATUS",result["status"])
    print("AUTHOR_SOURCE_URL",result["resolved_source_url"])
    print("C2HDM_SHA256",result["c2HDM_m_sha256"])
    print("NNLO_MATCHING_VALIDATED",result["NNLO_matching_validated"])
    print("Wrote",a.output_dir/EXPECTED_NAME)

if __name__=="__main__": main()
