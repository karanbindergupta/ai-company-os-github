# Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `HARNESS DENY` on a legitimate command | rule too broad (see the `*rm*`/"permit" incident) | tighten `arg_match` to a token: `harness.py rule ...` |
| `APPROVAL REQUIRED` and you are the founder | `REQUIRE_APPROVAL` needs a grant | `harness.py approve scope="Tool:arg" by=founder` |
| Everything denied including reads | `GLOBAL_PAUSE` is on | `harness.py control set=GLOBAL_PAUSE value=off by=founder` |
| `resume` refuses | unconfirmed side effect, or MUST_NOT_RETRY class | `harness.py recover execution=...` then `opkey-done`, then `reconciled=1` |
| `TASK STORE DIVERGENCE` | someone hand-edited `tasks.json` | `harness.py tasks-project` — the DB is authoritative |
| `complete` refuses with evidence present | evidence is claim-only (`verified=0`) | supply `path=` to a real file |
| Committed DB missing recent rows | WAL not checkpointed | `PRAGMA wal_checkpoint(FULL)` before `git add` |
