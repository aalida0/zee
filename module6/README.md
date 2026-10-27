# Coherent D0 candidate pilot

Run the command in [COHERENT_PILOT_AUDIT.md](COHERENT_PILOT_AUDIT.md).
Python API: `pilot(full_module3_input, mt_MSbar_160, reference_lha_sha256)`.
Only full, canonical-SHA-bound Module1 inputs inside inverse-mode Module2 and
Module3 records are accepted. The explicitly supplied reference top mass and
LHA hash must match the frozen source. All flavor masses and angles come from
that same validated scalar record; no separate flavor card is accepted.

The pilot executes the full scalar numerical search, independently replays
Module2, executes frozen Module3, and calls the frozen Module5 LO-linear
diagnostic. It retains gate evidence, matching input, and sector hashes.
`global_zee_acceptance` is always null and `constraints_complete` always false.
Module4 is NOT_EVALUATED. Results never establish an accepted point.

Compact actual evidence: [pilot.json](../validation/module6/pilot.json).
Detailed outputs/logs are ignored under `validation/module6/local/`.
