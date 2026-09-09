# Operations
```bash
python3 scripts/harness.py dash              # what is happening now
python3 scripts/harness.py recover           # after any crash or restart
python3 scripts/harness.py reap              # detect dead workers
python3 scripts/harness.py tasks-check       # prove task stores have not diverged
python3 scripts/harness.py verify            # ledger integrity
python3 scripts/harness_eval.py              # full eval + red team
```
**Founder controls**
```bash
python3 scripts/harness.py control set=GLOBAL_PAUSE value=on by=founder reason="..."
python3 scripts/harness.py approve scope="Bash:git push origin main" by=founder minutes=10 uses=1
python3 scripts/harness.py revoke scope="Bash:git push origin main"
```
**Before committing the tracked DB:** `sqlite3 ... "PRAGMA wal_checkpoint(FULL);"` — WAL sidecars are
gitignored, so uncheckpointed writes would not be committed.
