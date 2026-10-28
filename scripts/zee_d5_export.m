(* Fresh export only. Frozen model and SARAH installation remain read-only. *)
root=Directory[];
out=FileNameJoin[{root,"validation","module8","local","native"}];
If[DirectoryQ[out],Print["D5_REFUSE_EXISTING_OUTPUT ",out];Exit[2]];
CreateDirectory[out,CreateIntermediateDirectories->True];
report=<|"status"->"D5_UFO_RUNTIME_BLOCKED","math_version"->$Version|>;
save[]:=Export[FileNameJoin[{out,"export.json"}],report,"RawJSON"];
save[];
sarah=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sarah],report["diagnostic"]="SARAH.m missing";save[];Exit[3]];
Get[sarah];
SARAH[OutputDirectory]=FileNameJoin[{out,"sarah"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
report["sarah_version"]=ToString[SA`Version];
report["source_sha256"]=Association[Table[f->FileHash[FileNameJoin[{root,f}],"SHA256","HexString"],
 {f,{"models/SARAH/ZeeTypeII/ZeeTypeII.m","models/SARAH/ZeeTypeII/parameters.m","models/SARAH/ZeeTypeII/particles.m"}}]];
report["sarah_sha256"]=FileHash[sarah,"SHA256","HexString"];
save[];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 report["diagnostic"]="Start failed";save[];Exit[4]];
Print["D5_MAKEUFO_BEGIN"];
CheckAbort[MakeUFO[],report["diagnostic"]="MakeUFO aborted";save[];Exit[5]];
ufo=FileNameJoin[{out,"sarah","ZeeTypeII","EWSB","UFO"}];
report["ufo_directory"]=ufo;
report["required_files_present"]=And@@(FileExistsQ[FileNameJoin[{ufo,#}]]&/@
 {"parameters.py","particles.py","vertices.py","couplings.py","lorentz.py","object_library.py"});
report["status"]=If[TrueQ[report["required_files_present"]],"D5_UFO_EXPORTED_UNCERTIFIED","D5_UFO_RUNTIME_BLOCKED"];
save[];Print[report["status"]];
Exit[If[TrueQ[report["required_files_present"]],0,6]];
