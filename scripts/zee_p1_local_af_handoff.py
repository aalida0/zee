#!/usr/bin/env python3
"""Cross-machine Zee model source bundle: Mathematica locally, compilation on AF.

Pack generated SARAH SPheno Fortran, optional FlexibleSUSY model package,
SARAH model source and/or FeynRules UFO into an immutable, SHA-verified tar.
No package is treated as a validated Zee model or exclusion.
"""
import argparse,hashlib,io,json,tarfile
from pathlib import Path
STATUS="ZEE_GENERATED_SOURCE_TRANSFER_ONLY_NOT_MODEL_VALIDATION"
PARTS=("sarah_model","spheno_source","flexible_package","ufo")
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
def gather(inputs):
 selected=[]
 for label,path in inputs.items():
  if path is None:continue
  path=Path(path).expanduser().resolve(strict=True)
  if label not in PARTS:raise ValueError("Unknown bundle component")
  if label=="flexible_package":
   if not path.is_file() or not path.name.endswith(".tar.gz"):
    raise ValueError("FlexibleSUSY requires its model source tar.gz")
   pairs=[(path,path.name)]
  else:
   if not path.is_dir():raise ValueError(label+" requires a directory")
   if label=="sarah_model" and not(path/"Model.m").is_file():
    raise ValueError("SARAH Model.m not found")
   if label=="ufo" and not all((path/n).is_file() for n in
      ("parameters.py","particles.py","vertices.py")):
    raise ValueError("Incomplete FeynRules-generated UFO")
   if label=="spheno_source" and not any(path.rglob("*.f90")):
    raise ValueError("SPheno generated Fortran source missing")
   pairs=[(p,p.relative_to(path).as_posix())
          for p in sorted(path.rglob("*")) if p.is_file()]
  if not pairs:raise ValueError("Empty model source "+label)
  for file,rel in pairs:
   if file.is_symlink() or ".." in Path(rel).parts:
    raise ValueError("Symlink or unsafe input path")
   selected.append((label+"/"+rel,file))
 if not selected:raise ValueError("No source components supplied")
 return selected
def pack(inputs,out):
 out=Path(out).expanduser().absolute()
 if out.exists():raise ValueError("Cannot overwrite bundle")
 pairs=gather(inputs)
 if any(file==out for _,file in pairs):raise ValueError("Bundle overlaps input")
 manifest={"status":STATUS,"format":1,"model_validated":False,
           "components":sorted({name.split("/")[0] for name,_ in pairs}),
           "files":[{"path":name,"sha256":sha(file),"size":file.stat().st_size}
                    for name,file in pairs]}
 out.parent.mkdir(parents=True,exist_ok=True)
 try:
  with tarfile.open(out,"x:gz") as tar:
   contents=(json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode()
   m=tarfile.TarInfo("zee_handoff_manifest.json")
   m.size=len(contents)
   tar.addfile(m,io.BytesIO(contents))
   for name,path in pairs:
    m=tarfile.TarInfo(name);m.size=path.stat().st_size
    with path.open("rb") as f:tar.addfile(m,f)
 except Exception:
  out.unlink(missing_ok=True);raise
 return {"status":STATUS,"sha256":sha(out),"files":len(pairs)}
def inspect(bundle):
 with tarfile.open(bundle,"r:gz") as tar:
  members=tar.getmembers()
  names=[m.name for m in members]
  if (not members or len(set(names))!=len(names) or
      names[0]!="zee_handoff_manifest.json" or
      any(not m.isfile() or m.name.startswith("/") or
       any(t==".." for t in Path(m.name).parts) for m in members)):
   raise ValueError("Unsafe bundle or missing source manifest")
  manifest=json.load(tar.extractfile(members[0]))
  if (manifest.get("status")!=STATUS or manifest.get("format")!=1
       or manifest.get("model_validated") is not False):
   raise ValueError("Bad source-only transfer contract")
  entries=manifest.get("files",[])
  if len(entries)+1!=len(members):raise ValueError("Count mismatch")
  for entry in entries:
   name=entry["path"]
   if name not in names or tar.getmember(name).size!=entry["size"]:
    raise ValueError("Model file missing or size mismatch")
   hasher=hashlib.sha256()
   with tar.extractfile(name) as stream:
    for chunk in iter(lambda:stream.read(1048576),b""):
     hasher.update(chunk)
   if hasher.hexdigest()!=entry["sha256"]:
    raise ValueError("Corrupt model source: "+name)
  if set(names[1:])!={e["path"] for e in entries}:
   raise ValueError("Undeclared source file in archive")
 return manifest
def unpack(bundle,destination):
 out=Path(destination).expanduser().absolute()
 if out.exists():raise ValueError("Cannot overwrite extracted source")
 if not str(out).startswith("/home/"):
  raise ValueError("AF source/executables must be under /home")
 manifest=inspect(bundle)
 out.mkdir(parents=True,exist_ok=False)
 try:
  with tarfile.open(bundle,"r:gz") as tar:
   for member in tar.getmembers():
    dst=out/member.name
    dst.parent.mkdir(parents=True,exist_ok=True)
    with tar.extractfile(member) as source,dst.open("xb") as target:
     for chunk in iter(lambda:source.read(1048576),b""):
      target.write(chunk)
  for item in manifest["files"]:
   if sha(out/item["path"])!=item["sha256"]:
    raise ValueError("Extracted file checksum mismatch")
 except Exception:
  (out/"EXTRACTION_FAILED_NOT_VALIDATED").write_text("Not ready.\n")
  raise
 return {"status":STATUS,"destination":str(out),
         "files":len(manifest["files"]),"model_validated":False}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 sub=p.add_subparsers(dest="op",required=True)
 a=sub.add_parser("pack")
 a.add_argument("--sarah-model",type=Path)
 a.add_argument("--spheno-source",type=Path)
 a.add_argument("--flexible-package",type=Path)
 a.add_argument("--ufo",type=Path)
 a.add_argument("--out",type=Path,required=True)
 a=sub.add_parser("check");a.add_argument("--bundle",type=Path,required=True)
 a=sub.add_parser("unpack");a.add_argument("--bundle",type=Path,required=True)
 a.add_argument("--dest",type=Path,required=True)
 args=p.parse_args()
 if args.op=="pack":
  result=pack({k:getattr(args,k) for k in PARTS},args.out)
 elif args.op=="check":
  source=inspect(args.bundle)
  result={"status":STATUS,"files":len(source["files"]),
          "sha256":sha(args.bundle),"model_validated":False}
 else:
  result=unpack(args.bundle,args.dest)
 print("ZEE_LOCAL_AF_HANDOFF",json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
