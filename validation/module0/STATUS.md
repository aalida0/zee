# Module 0 finalization pending

The previous aggregate acceptance is superseded. No current PASS is claimed
until the committed runner completes all executable gates in one fresh run.

```sh
python3 scripts/zee_sarah_module0.py --publish
```

The runner preserves detailed output locally, requires fresh producer outputs
and exact native statuses, and publishes concise reports only after a complete
successful invocation. Partial stage selections cannot publish acceptance.
The validated physics implementation is unchanged by the repository cleanup.
Legacy timestamped evidence remains local and ignored. SPheno/FlavorKit is
outside this finalization and has not been developed or validated.
