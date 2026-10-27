V4Career job-title dropdown deduplication patch

File: app.py
Change: /api/filter-options now groups title options case-insensitively after trimming whitespace, showing one dropdown option for titles such as "Software Developer", "software developer", and " Software Developer ".

Backup your current app.py before replacing it. Copy this app.py into the actual V4Career project root, replacing the existing app.py. Do not replace or upload .env.

This fix addresses case/whitespace duplicates. It intentionally does not merge semantically different titles (for example, "Software Engineer" and "Software Developer") because they may be distinct roles. Such synonym grouping should be added as an explicit, reviewable canonical-title mapping, not guessed silently.

The project should be tested against the configured DB and UI after replacement. This patch does not modify database rows or schema.
