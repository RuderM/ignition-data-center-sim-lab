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

Reuse these existing style classes first:

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

Use inline styles for layout, sizing, spacing, overflow control, and one-off component tuning. Add a new Perspective style class only when the visual pattern is likely to be reused across multiple screens.

Keep the current palette and density:

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

- Root `ia.container.flex`, column direction, `sg/page`, full-height scrolling.
- Header or hero panel with equipment name, area/path, status pills, and short context.
- Summary panel for device role, manufacturer/model, upstream/downstream relation, or other descriptive metadata.
- KPI grid using `ia.display.view` instances of `Shared/MetricCard` for simple numeric values.
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

Bind card params rather than duplicating the card layout. Use `status` values of `Good`, `Warning`, or `Danger` so the shared component maps them to the existing status style classes.

Use `progress` for percent-like values or for normalized values where the range is obvious from the UDT. If a metric does not have a meaningful 0-100 scale, set `progress` to `0` or omit the visual emphasis by using a custom panel only when necessary.

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
- Confirm each route `viewPath` exactly matches the generated view folder path.
- Confirm bindings use Perspective binding shapes already present in the project.
- Confirm the screen uses `baseTagPath` instead of hard-coding one UDT instance path, unless the user explicitly requested a fixed instance screen.

If the gateway is running and accessible, run:

```sh
./scripts/flint-project-scan.sh
```

If the scan cannot be run, report why.

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
