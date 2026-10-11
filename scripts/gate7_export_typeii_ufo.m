(* Gate 7: export modified Yang/Wu Zee Type-II FeynRules source to LO UFO.
   This is a fresh source-derived UFO, NOT an NLO UFO.
   Run with: math -script scripts/gate7_export_typeii_ufo.m
   Requires environment: FEYNRULES_PATH, ZEE_FR_SOURCE, ZEE_UFO_OUTPUT
   Do not overwrite existing outputs. Source: https://github.com/YangPhy/Zee-Model
*)
ClearAll[frPath, modelPath, outPath, envDir, abort, oldDirectory];
abort[msg_String, code_Integer : 2] := (
  Print["GATE7 ERROR: " <> msg]; Exit[code];
);
envDir[name_String] := Module[{v = Environment[name]},
  If[!StringQ[v] || StringLength[v] == 0,
    abort["Set environment variable " <> name]];
  ExpandFileName[v]
];
frPath = envDir["FEYNRULES_PATH"];
modelPath = envDir["ZEE_FR_SOURCE"];
outPath = envDir["ZEE_UFO_OUTPUT"];

If[!FileExistsQ[FileNameJoin[{frPath, "FeynRules.m"}]],
  abort["FeynRules.m not found in " <> frPath]];
If[!FileExistsQ[FileNameJoin[{modelPath, "ZEE.fr"}]],
  abort["ZEE.fr not found in " <> modelPath]];
If[DirectoryQ[outPath] || FileExistsQ[outPath],
  abort["Output exists; refusing to overwrite: " <> outPath]];

Print["GATE7 input FeynRules: " <> frPath];
Print["GATE7 model source: " <> modelPath];
Print["GATE7 LO UFO output: " <> outPath];
oldDirectory = Directory[];
SetDirectory[frPath];
Get["FeynRules.m"];
SetDirectory[modelPath];
LoadModel["ZEE.fr"];
(* Force Feynman gauge to include all gauge-dependent interactions
   for later Ward and UV tests. LO MG5 import uses its own rules. *)
FeynmanGauge = True;
Print["GATE7: FeynRules model loaded. Exporting LZEE..."];
If[!ValueQ[LZEE], abort["LZEE is not defined"]];
WriteUFO[LZEE, Output -> outPath, AddDecays -> False];
If[!FileExistsQ[FileNameJoin[{outPath, "particles.py"}]] ||
   !FileExistsQ[FileNameJoin[{outPath, "vertices.py"}]],
   abort["WriteUFO returned without complete UFO particles/vertices files"]];
SetDirectory[oldDirectory];
Print["GATE7 PASS: LO UFO written: " <> outPath];
Print["GATE7 NOT VERIFIED: Type-II quark amplitudes, scalar potential mapping,"];
Print["GATE7 NOT VERIFIED: full Zee widths, physical point and Ward identities."];
Print["GATE7 NLO: fresh NLOCT UV/R2 counterterms mandatory."];
Exit[0];
