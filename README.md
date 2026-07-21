# MBT1 Ignition EPMS Simulator

Docker Compose development environment and source-controlled Ignition project for
a simplified single-site EPMS built on Inductive Automation Ignition 8.3.6.

The current application models the `MBT1` simulated data center. It is intended
as a compact hobby and learning project: small enough to rebuild from source,
but complete enough to exercise UDTs, memory-tag simulation, history, alarms,
Perspective screens, project scripting, Docker infrastructure, and operational
handover notes.

## Environment

Services are defined in `compose.yaml`.

- Ignition Gateway: `inductiveautomation/ignition:8.3.6`
- PostgreSQL: `postgres:16`
- Ignition container: `ignition-env1-gateway`
- PostgreSQL container: `ignition-env1-postgres`
- Ignition project: `data/projects/env1-project`

Ignition gateway data is persisted in the Docker named volume `ignition-data`.
Project files are also exposed through a host bind mount:

```text
./data/projects:/usr/local/bin/ignition/data/projects
```

This lets the Ignition project be edited and source-controlled from the host
while the rest of gateway data remains in the named volume.

## Start and Stop

Start the stack:

```sh
docker compose up -d
```

Open Ignition:

```text
http://localhost:8088
```

Default development credentials and connection values:

```text
Ignition admin password: password
PostgreSQL database: ignition
PostgreSQL user: ignition
PostgreSQL password: ignition
JDBC URL: jdbc:postgresql://postgres:5432/ignition
```

Local values can be overridden by creating a `.env` file before starting the
stack. Common variables are visible in `compose.yaml`, including
`GATEWAY_ADMIN_PASSWORD`, `IGNITION_HTTP_PORT`, `IGNITION_HTTPS_PORT`,
`IGNITION_GATEWAY_NAME`, `IGNITION_PUBLIC_ADDRESS`, `POSTGRES_DB`,
`POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT`.

Stop the stack:

```sh
docker compose down
```

Remove containers and persistent volumes:

```sh
docker compose down -v
```

## Current EPMS Model

The active modeled electrical hierarchy is:

```text
MBT1
+-- Utility1
    +-- MSG1
        +-- PDU1
            +-- Transformer1
            +-- PDUOutputBus
                +-- Way1 / PowerMeter1
                +-- Way2 / PowerMeter2
                +-- Way3 / PowerMeter3
                +-- Way4 / PowerMeter4
```

The current implementation intentionally ends at branch-level power meters.
Generator, UPS, RPP, RSB, rack, and server-load devices are future scope unless
the project is explicitly expanded.

UDT definitions, instances, and the point list are tracked under:

```text
working/UDT/
```

Important files:

```text
working/UDT/MBT1_EPMS_UDT_DEFINITIONS_v1.json
working/UDT/MBT1EPMSInstancesV1.json
working/UDT/MBT1_epms_points_list.csv
working/UDT/MBT1_EPMS_UDT_HANDOFF.md
```

## Ignition Project

The Ignition project lives at:

```text
data/projects/env1-project
```

Current Perspective areas include:

- `DataCenter/Utility`
- `DataCenter/MSG`
- `DataCenter/PDU`
- `DataCenter/Trends`
- `Shared/MetricCard`
- `Shared/MetricTrendPopup`
- `Gateway/Status`

Project scripts currently include:

```text
ignition/script-python/gateway/epms_sim
ignition/script-python/gateway/health
ignition/script-python/util/dates
ignition/script-python/util/math
ignition/script-python/util/trends
```

## Simulator

The Ignition-native simulator entry point is:

```python
project.gateway.epms_sim.tick()
```

It is intended to run from a Gateway Timer Event every 10 seconds. The timer
should use fixed delay, dedicated threading, and an enabled script body that
calls the simulator tick.

The repository currently also contains a Gateway timer resource at:

```text
data/projects/env1-project/ignition/timer/SIM
```

Review that resource in Designer before changing timer behavior, because
Designer may have generated or modified Gateway Event metadata.

The simulator writes calculated measurement values and rollups while preserving
operator-controlled state tags such as availability, communication health,
faults, and breaker state. Branch power meter loads roll up through Way, PDU,
Transformer, Main Switchgear, and Utility Source values.

## Perspective Notes

Metric cards support optional trend popups using the third-party EMBR ApexCharts
component.

`Shared/MetricCard` optional input parameters:

```json
{
  "trendTagPath": "",
  "trendLabel": "",
  "trendUnit": ""
}
```

The trend popup view is:

```text
Shared/MetricTrendPopup
```

For Perspective `runScript()` bindings, use project-library paths without the
`project.` prefix. Example:

```python
runScript("util.trends.get_apex_line_series", 60000, {view.params.tagPath}, {view.custom.hours}, {view.params.label})
```

Do not change this to `project.util.trends...`; that form causes Perspective
binding errors in this project.

### Alarm roll-up

The Utility pilot is the reference implementation:

```text
ignition/script-python/gateway/alarm_rollup
views/Shared/AlarmRollup
views/DataCenter/Utility
views/DataCenter/AlarmStatus
```

Use one gateway-side projection per equipment header. It should query only
`"ActiveAcked"` and `"ActiveUnacked"` states, filter by alarm-source patterns
such as `prov:T1:/tag:MBT1/Utility1/UtilitySource/*`, and return all display
fields in one plain result object. In particular, format priority text and
choose its color in that projection; do not pass Perspective property-tree
values into nested `runScript()` calls.

Ignition 8.3's scripting namespace does not expose
`system.alarm.AlarmState`; pass the active-state names above to
`system.alarm.queryStatus()`. To count configured alarms on a UDT instance,
read its `typeId`, then inspect the UDT definition at
`[provider]_types_/typeId`; recursive instance configuration does not reliably
materialize inherited alarm definitions.

Perspective binding transforms may receive a qualified value in Designer and a
plain Unicode string in a browser session. When converting the Utility
`baseTagPath` into the shared view's `scopePaths` list, support both:

```python
return [value.value if hasattr(value, "value") else value]
```

Validate this work in both Designer and a browser with an active alarm. A clean
Flint scan alone cannot catch binding quality overlays.

Utility, MSG, and PDU headers use embedded SVG one-line style page icons. Source
assets are kept in:

```text
working/PageIcons/oneline-style
```

## Working Context

Start new development by reading:

```text
working/General Context/Project Charter
```

Then read the current handovers relevant to the area being changed:

```text
working/handovers/IGNITION_FLINT_PERMISSIONS_HANDOVER.md
working/handovers/MBT1_EPMS_SIMULATOR_HANDOVER.md
working/handovers/METRIC_CARD_TREND_POPUP_HANDOVER.md
working/handovers/HEADER_LOGO_AND_PAGE_ICONS_HANDOVER.md
```

Additional working artifacts are under:

```text
working/Simulator/
working/Utility/
working/Logo/
working/PageIcons/
working/styleguide/
working/agent-skills/
```

## Permissions

Ignition runs project resources as UID/GID `2003:2003`. Host edits are commonly
made as the `ubuntu` user.

Before editing, inspect the worktree:

```sh
git status --short
```

Do not revert unrelated Designer-generated or user-generated changes unless
explicitly asked.

After creating or editing Ignition project resources under
`data/projects/env1-project`, preserve ACLs and hand touched or new Ignition
resources back to Ignition ownership:

```sh
sudo chown -R 2003:2003 data/projects/env1-project/path/to/touched/resource
```

Apply ownership narrowly to the touched Ignition resource files or directories,
not broadly across unrelated project content. See
`working/handovers/IGNITION_FLINT_PERMISSIONS_HANDOVER.md` for details.

## Validation

After editing Ignition project files, validate affected JSON and run a Flint
project scan:

```sh
python3 -m json.tool path/to/file.json >/dev/null
./scripts/flint-project-scan.sh
```

For broad checks, validate all project JSON files:

```sh
find data/projects/env1-project -name '*.json' -print0 \
  | xargs -0 -n1 python3 -m json.tool >/dev/null
```

Run the Flint scan after project edits:

```sh
./scripts/flint-project-scan.sh
```
