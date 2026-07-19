# Metric Card Trend Popup Handover

Date: 2026-07-19

## Context

After the simulator produced moving historian data, this session added a reusable
trend popup to the standard `Shared/MetricCard`.

The user installed the third-party EMBR Charts module and requested a simple
line chart in the popup with a selectable `1h` / `8h` history range.

Important EMBR details discovered:

```text
Component type: embr.chart.apex-charts
Line chart prop shape: type, options, series
Series shape: [{"name": "...", "data": [{"x": epochMillis, "y": value}]}]
```

## Implemented Files

Reusable card edited:

```text
data/projects/env1-project/com.inductiveautomation.perspective/views/Shared/MetricCard/view.json
```

New popup view:

```text
data/projects/env1-project/com.inductiveautomation.perspective/views/Shared/MetricTrendPopup/view.json
data/projects/env1-project/com.inductiveautomation.perspective/views/Shared/MetricTrendPopup/resource.json
```

New project script helper:

```text
data/projects/env1-project/ignition/script-python/util/trends/code.py
data/projects/env1-project/ignition/script-python/util/trends/resource.json
```

Existing equipment views wired:

```text
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/Utility/view.json
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/MSG/view.json
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/PDU/view.json
```

## MetricCard API Additions

`Shared/MetricCard` now has optional input params:

```json
{
  "trendTagPath": "",
  "trendLabel": "",
  "trendUnit": ""
}
```

Behavior:

- If `trendTagPath` is empty, no trend icon is shown.
- If `trendTagPath` is supplied, a faint `material/insert_chart_outlined` icon
  appears in the card header.
- Clicking the icon opens `Shared/MetricTrendPopup`.

Popup params:

```json
{
  "tagPath": "",
  "label": "Trend",
  "unit": ""
}
```

## Critical Binding Detail

The popup chart series binding must call the project script without a `project.`
prefix:

```python
runScript("util.trends.get_apex_line_series", 60000, {view.params.tagPath}, {view.custom.hours}, {view.params.label})
```

This was corrected by the user after an overlay error. The incorrect version was:

```python
runScript("project.util.trends.get_apex_line_series", ...)
```

Do not reintroduce the `project.` prefix in Perspective `runScript()` bindings
for this project.

## History Helper

Function:

```python
util.trends.get_apex_line_series(tag_path, hours=1, label="Trend")
```

Behavior:

- Accepts only `1` or `8` hours; anything else falls back to `1`.
- Uses `system.tag.queryTagHistory`.
- Uses `aggregationMode="Average"` and `returnFormat="Wide"`.
- Returns an empty valid Apex series on error instead of throwing an overlay.
- Logs history query failures with logger `util.trends`.

Current return sizes:

```text
1h -> 60 points
8h -> 96 points
```

## Cards Wired

Trend icons were added to historized metric cards on Utility, MSG, and PDU.

Examples include:

```text
Voltage
Current
Frequency
Real Power
Apparent Power
Power Factor
Total Energy
Load %
PDU Enclosure Temp
```

Non-historized configuration cards were intentionally left without trends:

```text
Rated Power
Rated Current
```

## Validation Already Performed

- JSON validation passed for edited/new Perspective views.
- Python syntax check passed for `util.trends`.
- Mocked helper test confirmed Apex series shape.
- `./scripts/flint-project-scan.sh` returned success.
- New Ignition resources were handed back to UID/GID `2003:2003`.

## Known Current State

The user confirmed the trend popup works after fixing the `runScript()` path.

If an overlay returns, check:

```text
metricTrendPopup/trendChart.series
util.trends logger
tagPath passed into popup params
historian status for that tag
```

