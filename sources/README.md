# sources/

Drop the legacy application source here — one subfolder per source system.

```
sources/
  outsystems-export/     # .oml / .osp exports, or an unpacked OS 11 XML tree
  legacy-api/            # a clone or copy of the backing service
  docs/                  # specs, BRDs, screenshots, anything the SME hands over
```

**What this folder is for:** it is the input to Stage 0 triage. Nothing here is read
automatically — `skills/source-triage.md` decides what is in scope, and only then does an
extraction pipeline run against it.

**Where it is declared:** intake questions 1 and 2 (`../intake.md`) record *what* is being
migrated and *where* it came from. Keep those answers and this folder in agreement; if the
source lives outside this workspace (a network share, a client VPN clone), say so in Q2
rather than symlinking it in.

**Version control:** whether this folder is committed was decided at scaffold time — check
`../.gitignore`. Source drops are routinely large and frequently belong to the client, so the
default is to ignore them.
