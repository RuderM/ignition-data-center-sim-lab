# Persistent change-report log

- Date: 2026-07-25
- Scope: `working/change-reports` and project working-context guidance

## Result

Evidence-based completion reports now persist across assistant sessions as a
chronological project change log under `working/change-reports/`.

## Changes

- Created `working/change-reports/README.md` with the required workflow,
  `YYYY-MM-DD-NNN-short-title.md` naming convention, report template, and index.
- Backfilled four substantive reports from the current session: Overview v2,
  browser and Flint prerequisites, the Perspective style policy, and the
  `sg-simple` screen migration.
- Added `working/change-reports/` to the root README's working-artifact list.
- Added a root README requirement that future verified repository changes save
  their user-facing completion report before the turn ends.
- Established append-only correction behavior: earlier reports remain intact;
  later corrections receive a new report.

## Verification

- Created the report directory, index, four backfilled reports, and this report.
- Confirmed the root README points future sessions to the directory and its
  reporting convention.

## Follow-ups

- Future agents must choose the next unused daily sequence and update the index
  when adding a report.
