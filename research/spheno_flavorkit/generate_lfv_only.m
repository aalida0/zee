(* Run with math -script; all model and output paths are private to local/. *)
root = Directory[];
local = FileNameJoin[{root,"research","spheno_flavorkit","local"}];
sarah = Environment["SARAH_ROOT"];
If[!StringQ[sarah] || sarah == "$Failed" || !FileExistsQ[FileNameJoin[{sarah,"SARAH.m"}]], Print["BLOCKED: SARAH_ROOT missing"]; Exit[2]];
Get[FileNameJoin[{sarah,"SARAH.m"}]];
SARAH[OutputDirectory] = FileNameJoin[{local,"output"}];
CreateDirectory[SARAH[OutputDirectory],CreateIntermediateDirectories->True];
SARAH[InputDirectories] = Prepend[SARAH[InputDirectories],FileNameJoin[{local,"models"}]];
Print["PILOT_START_BEGIN"];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded] || TrueQ[SARAH`AbortStart],Print["PILOT_START_FAIL"];Exit[3]];
Print["PILOT_START_PASS"];
Print["PILOT_MAKESPHENO_BEGIN"];
SARAH`MakeSPheno[IncludeFlavorKit -> True, IncludeLoopDecays -> False, Include2loopMasses -> False, ReadLists -> True];
Print["PILOT_MAKESPHENO_RETURNED: inspect generated files and diagnostics"];
