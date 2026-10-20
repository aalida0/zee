(* ZeeTypeII local SARAH validation. Run from repository root:
   math -script scripts/zee_sarah_check.m
   Source-level / initialization audit only: never generate SPheno here. *)

root = Directory[];
modelDir = FileNameJoin[{root, "models", "SARAH", "ZeeTypeII"}];
logDir = FileNameJoin[{root, "work", "sarah_zee"}];
If[!DirectoryQ[logDir],
  CreateDirectory[logDir, CreateIntermediateDirectories -> True]];
logFile = FileNameJoin[{logDir, "checkmodel.log"}];
statusFile = FileNameJoin[{logDir, "checkmodel_status.txt"}];
writeStatus[s_String] := (
  Export[statusFile, s <> "\n", "Text"];
  Print["ZEE_SARAH_STATUS ", s]
);
writeStatus["SOURCE_IMPLEMENTED_NOT_VALIDATED"];
If[!DirectoryQ[modelDir],
  Print["FAIL MODEL_DIRECTORY_MISSING ", modelDir];
  writeStatus["MODEL_DIRECTORY_MISSING"]; Exit[2]
];

(* In noninteractive 'math -script' mode, $Path can differ from the
   interactive notebook/kernel search path. Locate SARAH.m explicitly,
   without changing or reinstalling the SARAH installation. *)
appDirs = DeleteDuplicates[{
  FileNameJoin[{$HomeDirectory, ".Mathematica", "Applications"}],
  FileNameJoin[{$HomeDirectory, ".Wolfram", "Applications"}],
  FileNameJoin[{$UserBaseDirectory, "Applications"}]
}];
knownSources = {
  FileNameJoin[{$HomeDirectory, ".Mathematica", "Applications",
                "SARAH-4.15.4", "SARAH.m"}],
  FileNameJoin[{$HomeDirectory, ".Mathematica", "Applications",
                "SARAH", "SARAH.m"}]
};
sourceCandidates = DeleteDuplicates[Join[
  knownSources,
  Flatten[FileNames["SARAH.m", #, 2] & /@
    Select[appDirs, DirectoryQ]]
]];
sarahSource = SelectFirst[sourceCandidates, FileExistsQ,
                          Missing["NotFound"]];
If[!StringQ[sarahSource],
  Print["FAIL SARAH_SOURCE_NOT_FOUND. Checked ", InputForm[appDirs]];
  writeStatus["SARAH_SOURCE_NOT_FOUND"]; Exit[3]
];
Print["ZEE_SARAH_SOURCE ", sarahSource];
PrependTo[$Path, DirectoryName[sarahSource]];

(* Retain stdout messages for shell tee AND copy messages to a log.
   $Messages is a LIST of streams, not a single output stream. *)
messageStream = OpenWrite[logFile, PageWidth -> Infinity];
If[ListQ[$Messages], AppendTo[$Messages, messageStream]];

(* Load at TOP LEVEL before any subsequent expression containing the
   SARAH`Start symbol is parsed: necessary for correct context resolution. *)
loadResult = Check[Get[sarahSource], $Failed];
If[loadResult === $Failed || !MemberQ[$Packages, "SARAH`"],
  Print["FAIL SARAH_LOAD_FAILED"];
  writeStatus["SARAH_LOAD_FAILED"]; Close[messageStream]; Exit[4]
];
Print["ZEE_SARAH_LOADED ", SA`Version];

If[!ListQ[SARAH[InputDirectories]],
  Print["FAIL SARAH_INPUT_DIRS_UNAVAILABLE"];
  writeStatus["SARAH_INPUT_DIRS_UNAVAILABLE"]; Close[messageStream]; Exit[5]
];
SARAH[InputDirectories] =
  Prepend[SARAH[InputDirectories], DirectoryName[modelDir]];
Print["ZEE_SARAH_MODEL_DIR ", modelDir];
Print["ZEE_SARAH_INPUT_DIRS ", InputForm[SARAH[InputDirectories]]];

CheckAbort[
  Print["ZEE_SARAH_START_BEGIN"];
  startResult = Start["ZeeTypeII"];
  Print["ZEE_SARAH_START_RESULT ", InputForm[startResult]];
  If[!TrueQ[ModelLoaded] || TrueQ[AbortStart],
    writeStatus["SARAH_START_FAILED"];
    Close[messageStream]; Exit[6]
  ];
  writeStatus["SARAH_MODEL_INITIALIZED_NOT_CHECKED"];
  Print["ZEE_SARAH_CHECKMODEL_BEGIN"];
  checkResult = CheckModel[];
  Print["ZEE_SARAH_CHECKMODEL_RESULT ", InputForm[checkResult]];
  (* CheckModel may return Null despite warnings. This is NOT a PASS. *)
  writeStatus["SARAH_CHECKMODEL_COMPLETED_REVIEW_WARNINGS"];
  Close[messageStream];
  Print["ZEE_SARAH_MESSAGE_LOG ", logFile];
  Exit[0],
  writeStatus["SARAH_CHECK_ABORTED"];
  Close[messageStream];
  Exit[7]
];
