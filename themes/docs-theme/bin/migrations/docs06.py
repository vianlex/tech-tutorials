#!/usr/bin/env python3
"""Docs 0.6 migration toolkit.

    bin/migrations/docs06.py report  --sites ~/pgsty/site-a ~/www/ddia [--json r.json] [--md r.md]
    bin/migrations/docs06.py migrate --site ~/pgsty/site-a [--only callout,tabs] [--write] [--json out.json]
    bin/migrations/docs06.py check   --site ~/pgsty/site-a

Dry-run is the default; ``--write`` rewrites files atomically. A second run
must report zero changes. Constructs the scripts cannot express are left
untouched and listed with file:line and the reason. Stdlib only.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from docs06.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
