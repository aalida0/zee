#!/usr/bin/env bash
# Run from repository root. Keep a complete transcript, including stderr.
SARAH_ROOT=${SARAH_ROOT:-"$HOME/.Mathematica/Applications/SARAH-4.15.4"}
export SARAH_ROOT
out=research/spheno_flavorkit/local
mkdir -p "$out/models/ZeeTypeII"
cp models/SARAH/ZeeTypeII/{ZeeTypeII,parameters,particles}.m "$out/models/ZeeTypeII/"
cp research/spheno_flavorkit/model/SPheno.m "$out/models/ZeeTypeII/SPheno.m"
math -script research/spheno_flavorkit/generate.m > "$out/generation.log" 2>&1
result=$?
printf 'Kernel exit status: %s\n' "$result" | tee -a "$out/generation.log"
exit "$result"
