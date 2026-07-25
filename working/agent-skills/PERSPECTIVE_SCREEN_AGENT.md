# Perspective Screen Agent Instructions

Use this file as the starting context when asking an agent to create Ignition 8.3 Perspective SCADA screens for this simulated data center project.

The goal is to produce working Perspective project files that match the existing visual language, bind cleanly to UDT instances, and remain reusable for future equipment screens.

## Project Context

- Ignition version: 8.3.x.
- Target project: `data/projects/env1-project`.
- Perspective resources live under:
  `data/projects/env1-project/com.inductiveautomation.perspective`.
- Existing style classes live under:
  `data/projects/env1-project/com.inductiveautomation.perspective/style-classes/sg`.
- A working screen syntax reference is:
  `data/projects/env1-project/com.inductiveautomation.perspective/views/Gateway/Status/view.json`.
- A reusable KPI card component is:
  `data/projects/env1-project/com.inductiveautomation.perspective/views/Shared/MetricCard/view.json`.
- Utility UDT reference:
  `working/ignition-8.3-udt-UtilitySource_GridSim_Industries_GS-13K8-01-SIM.json`.
- Utility wireframe reference:
  `working/MBT1_Utility_Screen_Perspective_Style.svg`.

## Expected Agent Output

When asked to create a new Perspective screen, create or edit repo files directly.

## Filesystem Ownership Policy

This project is edited from VS Code as host user `ubuntu`, while the Ignition
container runs as UID/GID `2003`. New Ignition project resources must be handed
back to Ignition ownership before completion.

For any new file or directory created under `data/projects/env1-project`, set
ownership to UID/GID `2003:2003` after creation:

```sh
sudo chown -R 2003:2003 "data/projects/env1-project/path/to/new/resource"
```

Do not change ownership of unrelated project files. The project tree uses ACLs
to allow both `ubuntu` and UID/GID `2003` to write; preserve those ACLs.

For each new screen:

- Create a Perspective view folder under:
  `data/projects/env1-project/com.inductiveautomation.perspective/views`.
- Add a valid `view.json`.
- Add a valid `resource.json` with the same basic shape used by existing view resources.
- Add a page route in:
  `data/projects/env1-project/com.inductiveautomation.perspective/page-config/config.json`.
- Do not update the imported Exchange responsive navigation unless explicitly requested.
- Do not overwrite unrelated dirty worktree changes.

Do not return only a JSON snippet unless the user explicitly asks for that. The normal deliverable is a working repo-backed screen.

## Binding Model

Equipment and device screens should be reusable across UDT instances.

Use a required input view parameter:

```json
"params": {
  "baseTagPath": "[default]Path/To/Device"
}
```

Add the corresponding input param config:

```json
"propConfig": {
  "params.baseTagPath": {
    "paramDirection": "input"
  }
}
```

Bind UDT member tags relative to `view.params.baseTagPath`. Prefer expression bindings when the tag path must be assembled from the base path, and follow the existing `Gateway/Status` binding structure for syntax.

Use UDT names, point documentation, engineering units, alarm setpoints, and folder grouping from the supplied UDT JSON to decide what the operator should see.

## Visual System

Screens must look like part of the same SCADA application, not one-off mockups.

New screens and substantial redesigns of existing screens **must use the
`sg-simple` Perspective style-class family**. A wireframe or conceptual image
does not justify recreating the visual system with inline styles.

The legacy `sg` family is only for small, targeted changes to screens that
already use it:

- `sg/page`
- `sg/hero`
- `sg/panel`
- `sg/metricCard`
- `sg/metricValue`
- `sg/heading`
- `sg/eyebrow`
- `sg/muted`
- `sg/statusGood`
- `sg/statusWarning`
- `sg/statusDanger`

### Design-system screens (`sg-simple`)

Use `sg-simple` for every new screen and substantial screen redesign:

- Surface and layout: `sg-simple/page`, `sg-simple/hero`, `sg-simple/panel`
- Typography: `sg-simple/heroTitle`, `sg-simple/heroEyebrow`,
  `sg-simple/heading`, `sg-simple/eyebrow`, `sg-simple/muted`,
  `sg-simple/metricValue`, `sg-simple/accentValue`
- Reusable controls: `sg-simple/metricCard`, `sg-simple/statusPill`,
  `sg-simple/trendIcon`

`sg-simple` implements the current Inter-based system: `#F5F7FA` page
surface, white panels, `#0053AD` primary blue, `#0671E0` action/progress blue,
`#212121` ink, `#717171`/`#89939E` supporting text, `#DBEDFF` borders, and
8px card radii.

Apply static typography, colors, backgrounds, borders, radii, shadows, and
padding through `sg-simple` classes. Do not duplicate those declarations in
component `props.style` objects. Inline styles are reserved for layout, sizing,
spacing, overflow control, data-bound state colors, and properties that
Perspective cannot emit from a style class (for example, a trend icon's 24px
dimensions).

Before delivery, audit every edited component's `props.style`. Any static visual
declaration that duplicates the design system must be removed in favor of an
existing `sg-simple` class. If a genuinely reusable visual pattern is missing,
create one new Perspective style class and reuse it; do not distribute repeated
inline declarations across the view.

For small edits to legacy screens, preserve their existing `sg` family rather
than mixing `sg` and `sg-simple` within the same visual region. A substantial
redesign is a clean migration to `sg-simple`, not an expansion of legacy inline
styling.

Keep the legacy `sg` palette and density for legacy screens:

- Page background: light gray surface.
- Panels/cards: white with light border.
- Primary ink: dark blue-gray.
- Muted text: gray-blue.
- Accent: teal.
- Primary chart/progress color: blue.
- Warning/danger/good states: use the existing status classes where possible.
- Border radii should generally stay at 8px or less, except pill-style status labels.

## Preferred Screen Structure

Use the existing `Gateway/Status` screen as the structural reference.

Typical equipment screen structure:

- Root `ia.container.flex`, column direction, `sg/page` or `sg-simple/page`, full-height scrolling.
- Header or hero panel with equipment name, area/path, status pills, and short context.
- Summary panel for device role, manufacturer/model, upstream/downstream relation, or other descriptive metadata.
- KPI grid using `Shared/MetricCard` on legacy screens or `Shared/SimpleMetricCard` on `sg-simple` screens.
- Trend or chart panel when the UDT includes historical measurement points.
- Action buttons or links only when requested or clearly present in the wireframe.

Use clear `meta.name` values for maintainability. Prefer names that identify the operator-facing purpose, such as `voltageCard`, `statusPills`, `powerTrend`, or `deviceSummary`.

## Metric Cards

Use `Shared/MetricCard` for simple KPI tiles.

The card accepts:

```json
{
  "label": "Metric",
  "value": "Unavailable",
  "unit": "",
  "status": "Good",
  "helperText": "",
  "progress": 0
}
```

`status` (`Good`, `Warning`, `Danger`) and `progress` are inputs of legacy
`Shared/MetricCard`; use them only where that card is deliberately retained.
`Shared/SimpleMetricCard` accepts them for migration compatibility but keeps its
cards neutral, so do not use either as a visual-emphasis mechanism.

### `Shared/SimpleMetricCard`

Use `Shared/SimpleMetricCard` for `sg-simple` metric grids instead of
duplicating card component trees. Its inputs are:

```json
{
  "label": "Metric",
  "value": "Unavailable",
  "unit": "",
  "helperText": "",
  "status": "Good",
  "progress": 0,
  "trendTagPath": "",
  "trendLabel": "",
  "trendUnit": ""
}
```

Bind `trendTagPath` to the historized tag. A non-empty value displays the chart
icon and opens `Shared/MetricTrendPopup`; use `trendLabel` and `trendUnit` to
label that popup correctly.

## Routes

Add a page route for each generated screen in:

`data/projects/env1-project/com.inductiveautomation.perspective/page-config/config.json`

Route policy:

- Use a concise route path derived from the requested screen name.
- Point `viewPath` to the generated view path.
- Keep existing routes intact.
- Leave route `title` empty unless the user provides a title convention.

Example:

```json
"/Utility": {
  "title": "",
  "viewPath": "DataCenter/Utility"
}
```

Do not update nav menu data by default.

## Validation Checklist

Before finishing, validate the generated files.

Required checks:

- Run `jq` against every edited JSON file.
- Confirm each new `view.json` has `custom`, `params`, `props`, and `root`.
- Confirm each new view resource has `resource.json` with `scope`, `version`, `restricted`, `overridable`, and `files`.
- Confirm all referenced style classes exist, unless the task also created them.
- For every new or substantially redesigned screen, confirm static visual
  properties come from `sg-simple` classes rather than repeated inline styles.
- Inspect edited `props.style` objects and justify each remaining property as
  layout, sizing, spacing, overflow, data-bound state, or a Perspective
  limitation.
- Confirm each route `viewPath` exactly matches the generated view folder path.
- Confirm bindings use Perspective binding shapes already present in the project.
- Confirm the screen uses `baseTagPath` instead of hard-coding one UDT instance path, unless the user explicitly requested a fixed instance screen.

If the gateway is running and accessible, run:

```sh
./scripts/flint-project-scan.sh
```

If the scan cannot be run, report why.

## Lessons from Perspective Screen Work

- Treat conceptual wireframes as layout and visual-hierarchy references only.
  Point names, engineering units, equipment relationships, ratings, and
  electrical topology must come from the current UDT definitions, instance
  hierarchy, point list, and working equipment screens.
- Do not invent wireframe-only telemetry. If the model has no THD, bus
  temperature, spare feeder breaker, or similar point, replace it with useful
  modeled data rather than binding to a plausible-looking nonexistent tag.
- Before writing bindings, map every displayed device to its exact live instance
  root. Afterward, extract every `tag()` path from the completed view and compare
  its relative member path with the authoritative point list.
- A site-specific one-line overview may intentionally use fixed instance paths.
  Reusable equipment views still require `baseTagPath`; do not generalize this
  overview exception to device screens.
- Verify the configured Perspective route in `page-config/config.json`, then
  load that route in a real browser. A thumbnail, wireframe PNG, or Designer
  preview is not proof that the deployed page is correct.
- Test with the application's shared docks visible. Coordinate-view
  `defaultSize` and `minWidth` must account for the navigation dock; otherwise a
  layout that looks correct in isolation can clip the final branch card or force
  unnecessary horizontal scrolling.
- Browser verification must show live tag values, status colors, the complete
  equipment hierarchy, and the lowest visible row. Exercise at least one
  navigation target when cards or controls are clickable.
- Bind-mounted file changes are not always hot-reloaded into an existing Gateway
  session. If the container sees the new file but the browser still shows the
  old resource, use `docker compose restart ignition`; never use
  `docker compose down -v` merely to reload a project.
- Flint scanning and Gateway project loading are separate concerns. A `404` from
  `/data/flint/health` or `/data/flint/rpc` means the Flint Designer Bridge is
  unavailable, but it does not prevent the Gateway from loading valid project
  files after a safe restart.
- Preserve UID/GID `2003:2003` and the project ACLs on every touched Perspective
  resource. Verify ownership after external edits.

## Current Utility Screen References

The current utility wireframe describes a screen with:

- Title: `Utility`.
- Context: `MBT1 / Utility_1`.
- Header facts: last update and bound device.
- Status pills: overall, available, communication, and fault state.
- Summary panel: site power summary plus manufacturer/model.
- KPI tiles: voltage, current, frequency, real power, apparent power, power factor, total energy, and utility load.
- Trend panel: recent real power over the last 60 minutes.

The current utility UDT exposes these major groups:

- `Status`: `Available`, `CommGood`, `Faulted`.
- `Electrical`: `VoltageLLAvg`, `CurrentAvg`, `Frequency`.
- `Power`: `RealPower`, `ApparentPower`, `PowerFactor`.
- `Energy`: `TotalEnergy`.
- `Capacity`: `RatedPower`, `LoadPct`.

Use the UDT engineering units, ranges, alarm setpoints, and documentation to drive labels, formatting, helper text, and status logic.

## Final Response Expectations

When reporting completion, keep the response concise and include:

- Files created or edited.
- Route added.
- Validation commands run and their results.
- Any gateway scan result, or why the scan was not run.
- Any assumptions made, especially default `baseTagPath` or route naming.
