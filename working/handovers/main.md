We are working on an Inductive Automation Ignition 8.3.6 project in repo:

  /home/ubuntu/projects/ignition-env1

  This is a simplified single-site EPMS for a simulated data center. Start by reading the project charter:

  working/General Context/Project Charter

  The current modeled electrical hierarchy is roughly:

  MBT1
  └── Utility1
      └── MSG1
          └── PDU1
              ├── Transformer1
              └── PDUOutputBus
                  ├── Way1 / PowerMeter1
                  ├── Way2 / PowerMeter2
                  ├── Way3 / PowerMeter3
                  └── Way4 / PowerMeter4

  UDT definitions, instances, and point list are in:

  working/UDT/

  Important handovers to read before changing anything:

  working/handovers/IGNITION_FLINT_PERMISSIONS_HANDOVER.md
  working/handovers/MBT1_EPMS_SIMULATOR_HANDOVER.md
  working/handovers/METRIC_CARD_TREND_POPUP_HANDOVER.md
  working/handovers/HEADER_LOGO_AND_PAGE_ICONS_HANDOVER.md

  Current key features:
  - Ignition project is `data/projects/env1-project`.
  - Perspective screens exist for Utility, MSG, PDU, Trends, and shared components.
  - The simulator project script is `project.gateway.epms_sim.tick()` and is intended to run from a Gateway
  Timer Event every 10 seconds.
  - Metric cards now support optional trend popups using EMBR ApexCharts.
  - For Perspective `runScript()` bindings, use project-library paths without `project.` prefix, e.g.
  `util.trends.get_apex_line_series`.
  - Utility/MSG/PDU headers use embedded SVG one-line style page icons from `working/PageIcons/oneline-
  style`.

  Filesystem/permissions note:
  Ignition runs as UID/GID `2003:2003`. After creating or editing Ignition project resources under `data/
  projects/env1-project`, preserve ACLs and set touched/new Ignition resources back to `2003:2003`. See the
  permissions handover.

  Before editing, inspect the current worktree with `git status --short` because Designer may have generated
  changes. Do not revert unrelated changes unless explicitly asked. After edits, validate JSON, run `./
  scripts/flint-project-scan.sh`, and report what changed.