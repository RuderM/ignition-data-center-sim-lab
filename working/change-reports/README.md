# Change Reports

This directory preserves the evidence-based completion reports produced after
repository changes. It is a chronological project change log for future agents
and maintainers; it does not replace focused handovers or Git history.

## Required workflow

After completing and verifying a repository change:

1. Write the user-facing completion report.
2. Save the same material here before ending the turn.
3. Include only observed changes and verification results. Mark inferences.
4. Record failed or unavailable verification and its exact reason.
5. Do not rewrite earlier reports. Add a corrective report if later evidence
   changes a prior conclusion.

Research-only answers that do not change the repository do not require a report
unless the user asks to preserve them.

## File naming

Use:

```text
YYYY-MM-DD-NNN-short-title.md
```

`NNN` is a zero-padded sequence for that date. Choose the next unused number.
Keep the title concise and filesystem-safe.

## Report format

```markdown
# Short change title

- Date: YYYY-MM-DD
- Scope: concise subsystem or feature

## Result

What is now true from the user's perspective.

## Changes

- Exact files, resources, symbols, routes, or behavior changed.

## Verification

- Commands and scenarios actually exercised, with observed results.

## Follow-ups

- Remaining prerequisite, limitation, or `None`.
```

## Index

- `2026-07-25-001-overview-v2.md` — MBT1 Perspective Overview redesign.
- `2026-07-25-002-browser-flint-prerequisites.md` — Browser and Flint setup notes.
- `2026-07-25-003-perspective-style-policy.md` — Mandatory `sg-simple` policy.
- `2026-07-25-004-sg-simple-migration.md` — Migration of remaining legacy screen references.
- `2026-07-25-005-persistent-change-reports.md` — Persistent completion-report workflow.
