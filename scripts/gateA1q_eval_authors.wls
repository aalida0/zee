(* Gate A1Q: numerical evaluation of AUTHENTIC original KIT c2HDM.m.
   Run ONLY with work/gateA1q_original_nnlo_v1/c2HDM.m, checksum
   independently checked by the controlling Python runner.
   Algebraic reference only; NO RG, BR, exclusion or physics patches.
   CLI: wolframscript -file scripts/gateA1q_eval_authors.wls SOURCE INPUT_JSON OUTPUT_TXT
*)
If[Length[$ScriptCommandLine] != 4,
  Print["A1Q_ERROR wrong number of arguments"];
  Exit[2]
];
sourcePath = $ScriptCommandLine[[2]];
inputPath = $ScriptCommandLine[[3]];
outputPath = $ScriptCommandLine[[4]];
If[!FileExistsQ[sourcePath] || !FileExistsQ[inputPath],
  Print["A1Q_ERROR missing original source or inputs"]; Exit[2]
];
params = Import[inputPath, "RawJSON"];
If[!AssociationQ[params],
  Print["A1Q_ERROR input JSON must be an association"]; Exit[2]
];
required = {"mt_numerator","mt_denominator","mu_numerator",
            "mu_denominator","tan_numerator","tan_denominator",
            "masses_GeV"};
If[!And@@(KeyExistsQ[params,#]& /@ required),
  Print["A1Q_ERROR incomplete numeric inputs"]; Exit[2]
];
(* Exact decimal rational inputs avoid premature machine rounding. *)
exactInput[n_] := Module[{a,b},
  a = ToExpression[params[n<>"_numerator"]];
  b = ToExpression[params[n<>"_denominator"]];
  If[!IntegerQ[a] || !IntegerQ[b] || b<=0,
    Print["A1Q_ERROR noninteger input numerator/denominator"];Exit[2]
  ];
  a/b
];
mt0=exactInput["mt"];
mu0=exactInput["mu"];
tan0=exactInput["tan"];
If[!And@@(NumericQ /@ {mt0,mu0,tan0}) ||
   mt0<=100 || mt0>=250 || mu0<=0 || tan0<=0,
  Print["A1Q_ERROR invalid fixed inputs"]; Exit[2]
];
massList=params["masses_GeV"];
If[massList =!= {300,700,1000,2000},
  Print["A1Q_ERROR unexpected mass grid"];Exit[2]
];
(* Load once; keep ALL original formula definitions untouched. *)
Quiet[Check[Get[sourcePath],
  Print["A1Q_ERROR original c2HDM.m Get[] failed"]; Exit[1]
]];
quantities={
  {0,7,HoldForm[cHeff[0,7]]},{0,8,HoldForm[cHeff[0,8]]},
  {1,7,HoldForm[cHeff[1,7]]},{1,8,HoldForm[cHeff[1,8]]},
  {2,3,HoldForm[cH[2,3]]},{2,4,HoldForm[cH[2,4]]},
  {2,5,HoldForm[cH[2,5]]},{2,6,HoldForm[cH[2,6]]},
  {2,7,HoldForm[cHeff[2,7]]},{2,8,HoldForm[cHeff[2,8]]},
  {3,7,HoldForm[cH[3,7]]},{3,8,HoldForm[cH[3,8]]}
};
(* HoldForm only prevents premature evaluation during rule construction.
   ReleaseHold occurs after the official Get[] and at fixed numeric inputs. *)
fh=OpenWrite[outputPath,FormatType->InputForm];
If[Head[fh] =!= OutputStream,
  Print["A1Q_ERROR cannot open numerical output"];Exit[1]
];
WriteString[fh,"STATUS A1Q_ORIGINAL_AUTHOR_NUMERICAL_VALUES_NO_BR\n"];
For[k=1,k<=Length[massList],k++,
  m=massList[[k]];
  rr=mt0^2/m^2;
  rules={Au->1/tan0,AuC->1/tan0,Ad->-tan0,AdC->-tan0,
         r->rr,u->1-1/rr,ubar->1-rr,
         mu->mu0,mt->mt0};
  For[j=1,j<=Length[quantities],j++,
    ord=quantities[[j,1]];
    op=quantities[[j,2]];
    val=N[ReleaseHold[quantities[[j,3]]] /. rules,25];
    (* Avoid false pass for unresolved Mathematica symbols. *)
    If[!NumberQ[val] || !FreeQ[val,Indeterminate|ComplexInfinity] ||
       Abs[Im[val]]>10^-11 || Abs[Re[val]]>10^7,
      Print["A1Q_ERROR unresolved/nonreal source formula m=",m,
            " order=",ord," op=",op," expression=",InputForm[val]];
      Close[fh];Exit[1]
    ];
    WriteString[fh,"AUTHOR mass=",ToString[m],
      " order=",ToString[ord],
      " op=",ToString[op],
      " value=",ToString[InputForm[N[Re[val],19]]],"\n"
    ];
  ]
];
Close[fh];
Print["STATUS A1Q_ORIGINAL_AUTHOR_NUMERICAL_VALUES_NO_BR"];
Print["VALUES_WRITTEN ",Length[massList]*Length[quantities]];
Print["SOURCE ",sourcePath];
Print["OUTPUT ",outputPath];
