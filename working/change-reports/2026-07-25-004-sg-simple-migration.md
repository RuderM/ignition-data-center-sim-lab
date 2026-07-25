# Remaining Perspective screens migrated to `sg-simple`

- Date: 2026-07-25
- Scope: Gateway Status, Alarm Status, and shared metric resources

## Result

No Perspective screen resource retains an `sg/*` style-class reference. The
Gateway Status and Alarm Status pages render with the current `sg-simple` design
system, and the shared metric trend popup remains operational.

## Changes

- Migrated `views/Gateway/Status/view.json` to `sg-simple` page, hero, hero
  typography, and status-pill classes.
- Replaced six Gateway Status `Shared/MetricCard` embeddings with
  `Shared/SimpleMetricCard`.
- Migrated `views/DataCenter/AlarmStatus/view.json` to `sg-simple` page and hero
  classes.
- Migrated `views/Shared/MetricCard/view.json` to `sg-simple` typography, card,
  status-pill, trend-icon, and metric-value classes; updated progress colors to
  the current palette.
- Migrated `views/Shared/MetricTrendPopup/view.json` to `sg-simple` panel,
  heading, and muted-text classes.
- Left the unreferenced `style-classes/sg_20260725` archive untouched.

## Verification

- Parsed all four edited JSON resources successfully.
- Confirmed all 13 referenced `sg-simple` classes exist.
- Searched the entire Perspective project and found no remaining `sg/`
  references.
- Loaded Gateway Status and Alarm Status in Chromium and visually confirmed the
  migrated layouts with live data.
- Opened a Utility metric trend icon and observed the migrated trend popup.
- Ran Flint `project.scan`; result was `success: true`.
- Confirmed all touched resources retained UID/GID `2003:2003` and mode `664`.

## Follow-ups

- None for the requested legacy-class migration.
