(* Run: math -script scripts/zee_sarah_check.m
   Execute from the repository root. No SPheno generation occurs. *)
root = Directory[];
modelDir = FileNameJoin[{root,"models","SARAH","ZeeTypeII"}];
logDir = FileNameJoin[{root,"work","sarah_zee"}];
If[!DirectoryQ[modelDir],Print["FAIL MODEL_DIRECTORY_MISSING ",modelDir];Exit[2]];
If[!DirectoryQ[logDir],CreateDirectory[logDir,CreateIntermediateDirectories->True]];
logFile = FileNameJoin[{logDir,"checkmodel.log"}];
statusFile = FileNameJoin[{logDir,"checkmodel_status.txt"}];
logStream = OpenWrite[logFile,PageWidth->Infinity];
status = "SOURCE_IMPLEMENTED_NOT_VALIDATED";
(* Mirror Print messages to a persistent transcript. The kernel messages
   are separately logged through MessagesNotebook-independent $Messages. *)
writeStatus[s_] := (Export[statusFile,s<>"\n","Text"];Print["ZEE_SARAH_STATUS ",s]);
CheckAbort[
  Needs["SARAH`"];
  If[!ValueQ[SARAH[InputDirectories]],Print["FAIL SARAH_INPUT_DIRS_UNAVAILABLE"];Exit[3]];
  SARAH[InputDirectories] = Prepend[SARAH[InputDirectories],DirectoryName[modelDir]];
  Print["ZEE_SARAH_MODEL_DIR ",modelDir];
  Print["ZEE_SARAH_INPUT_DIRS ",SARAH[InputDirectories]];
  $Messages = logStream;
  Print["ZEE_SARAH_START_BEGIN"];
  startResult = Start["ZeeTypeII"];
  Print["ZEE_SARAH_START_RESULT ",InputForm[startResult]];
  If[!TrueQ[ModelLoaded],writeStatus["SARAH_START_FAILED"];Close[logStream];Exit[4]];
  writeStatus["SARAH_MODEL_INITIALIZED_NOT_CHECKED"];
  Print["ZEE_SARAH_CHECKMODEL_BEGIN"];
  checkResult = CheckModel[];
  Print["ZEE_SARAH_CHECKMODEL_RESULT ",InputForm[checkResult]];
  (* No unconditional PASS: CheckModel[] may return Null after warnings;
     expert review of all emitted diagnostics is mandatory. *)
  writeStatus["SARAH_CHECKMODEL_COMPLETED_REVIEW_WARNINGS"];
  Close[logStream];
  Print["ZEE_SARAH_MESSAGE_LOG ",logFile];
  Exit[0],
  writeStatus["SARAH_CHECK_ABORTED"];Close[logStream];Exit[5]
];
