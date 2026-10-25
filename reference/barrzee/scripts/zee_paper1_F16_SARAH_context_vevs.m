(* Strict F16 numerical VEV resolution across Wolfram symbol contexts.
   The F13 fixture is read BEFORE SARAH/Susyno load, so the source rule
   "v1->..." may be Global`v1 while SARAH mass-matrix expressions use
   SARAH`v1 or Susyno`LieGroups`v1. These are not the same symbol.

   Use only the physical F13 v and beta, never model defaults.
   Explicitly enumerate the three evidenced contexts. If a new context
   appears, the downstream NumericQ gate MUST fail closed.
*)
zeeF16VEVResolverStatus = "F16_CONTEXT_SAFE_PHYSICAL_F13_VEVS";
zeeF16ResolveVEVs[expression_, vev_?NumericQ, beta_?NumericQ] :=
 With[{zeeValue1=N[vev Cos[beta]],
       zeeValue2=N[vev Sin[beta]]},
  expression /. {
   HoldPattern[Global`v1] :> zeeValue1,
   HoldPattern[Global`v2] :> zeeValue2,
   HoldPattern[SARAH`v1] :> zeeValue1,
   HoldPattern[SARAH`v2] :> zeeValue2,
   HoldPattern[Susyno`LieGroups`v1] :> zeeValue1,
   HoldPattern[Susyno`LieGroups`v2] :> zeeValue2
  }
];
