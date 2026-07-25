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

After a fresh clone, configure the bind-mounted project tree before starting
the stack. Git does not preserve filesystem ACLs, so each checkout needs this
one-time bootstrap:

```sh
./scripts/bootstrap-permissions.sh
docker compose up -d
```

The script requires `setfacl`, which is supplied by the `acl` package on common
Linux distributions. It detects the checkout owner's UID and grants that UID
and Ignition UID `2003` access to existing resources plus default inheritance
for resources created later.
If the checkout already contains resources owned by another UID, rerun the
script with `sudo`.

For later starts:

```sh
docker compose up -d
```

On its first start, the Gateway restores
`backups/gateway/ignition-env1.gwbk` into the `ignition-data` volume. Ignition
only performs that restore while the volume has no `db/config.idb`. If an
earlier startup initialized the volume without restoring, reset this
development environment and start it again:

```sh
docker compose down -v
docker compose up -d
```

`docker compose down -v` permanently removes both the Gateway and PostgreSQL
development volumes; do not use it after creating local state you need to keep.

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

## Gateway Backup

Generate or replace the Git LFS-tracked gateway backup:

```sh
./scripts/create-gateway-backup.sh
```

The script writes `backups/gateway/ignition-env1.gwbk` without a date suffix.
It validates the temporary archive before replacing the previous backup.

## PostgreSQL Backup

Generate or replace the Git LFS-tracked PostgreSQL recovery artifacts:

```sh
./scripts/create-postgres-backup.sh
```

The script writes these stable names without date suffixes:

```text
backups/postgres/ignition.dump
backups/postgres/globals.sql
```

`ignition.dump` is a custom-format database archive with database creation
metadata. `globals.sql` preserves cluster-wide roles and tablespaces. Run the
script before transferring the environment; both files are required to recover
the Ignition database with its roles.

### PostgreSQL Restore

The restore permanently replaces the target Ignition database. Stop the
Gateway, restore the database and globals, then start the Gateway:

```sh
docker compose stop ignition
./scripts/restore-postgres-backup.sh --replace
docker compose start ignition
```

The restore helper refuses to run while the Gateway container is running and
requires the explicit `--replace` acknowledgement.

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
working/change-reports/
```

After completing and verifying any repository change, preserve the user-facing
completion report under `working/change-reports/` before ending the turn. Follow
the naming and evidence format in `working/change-reports/README.md`, choose the
next unused sequence number for the date, and never rewrite an earlier report
to hide a later correction.

## External References

The public repositories under [`thirdgen88`](https://github.com/thirdgen88) are
useful implementation references for Ignition container deployments. In
particular:

- [`thirdgen88/ignition-docker`](https://github.com/thirdgen88/ignition-docker)
  contains Docker entrypoint and supplemental-module registration examples.
- [`thirdgen88/ignition-examples`](https://github.com/thirdgen88/ignition-examples)
  includes Compose environments and an IIoT custom-image example that registers
  third-party module certificates and EULAs in a gateway backup.

Use these as patterns rather than version-independent specifications. Confirm
paths, database behavior, and entrypoint options against the pinned Ignition
`8.3.6` image before applying an older example.

## Permissions

Ignition runs project resources as UID/GID `2003:2003`. A fresh clone is
normally owned by the local Linux user, whose numeric UID may differ.

Before the first startup after cloning, run:

```sh
./scripts/bootstrap-permissions.sh
```

The script applies access ACLs recursively to `data/projects` for the checkout
owner and UID `2003`, then applies default ACLs to every directory so both users
can write resources created later. It detects the checkout owner automatically;
`HOST_UID` and `IGNITION_UID` may be supplied to override either value.

Before editing, inspect the worktree:

```sh
git status --short
```

Do not revert unrelated Designer-generated or user-generated changes unless
explicitly asked.

Do not replace the access and default ACLs with a shared group alone: Ignition
may create resources with mode `0644`, which denies group writes.

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

### Browser verification prerequisites

Perspective screen changes should be exercised at:

```text
http://localhost:8088/data/perspective/client/env1-project/
```

The automated browser uses a managed Chromium build. On a minimal Ubuntu
workstation, Chromium installation and startup require an archive extractor and
its shared libraries:

```sh
sudo apt-get update
sudo apt-get install -y \
  unzip \
  libatk1.0-0t64 \
  libatk-bridge2.0-0t64 \
  libcups2t64 \
  libasound2t64 \
  libgbm1 \
  libcairo2 \
  libpango-1.0-0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libatspi2.0-0t64
```

Ubuntu releases before the `t64` transition may use package names without the
`t64` suffix. If Chromium still fails to start, run `ldd` against its reported
executable path and install only the libraries shown as `not found`.

If the browser installer reports that its version directory exists but the
Chromium executable is missing, check that the directory is empty, remove only
that empty version directory, and retry. An incomplete empty cache directory can
prevent a clean reinstall.

The Perspective root page is configured in
`com.inductiveautomation.perspective/page-config/config.json`; verify the route
and `viewPath` before assuming a PNG or other static artifact is the page under
test. Screenshots are verification output only and are not Perspective
resources.

Direct bind-mounted project edits may not appear in an already-running Gateway
session immediately. A development Gateway container restart reloads the
project without removing its volumes:

```sh
docker compose restart ignition
```

Do not use `docker compose down -v` for this purpose.

### Flint scan prerequisite

`./scripts/flint-project-scan.sh` requires the Flint Designer Bridge module to
be installed and running on the Gateway. For Ignition 8.3, install the signed
`Flint-Designer-Bridge-<version>-8.3.modl` artifact from:

```text
https://github.com/bw-design-group/flint-designer-bridge-ignition-module/releases
```

Verify the module before running a scan:

```sh
curl http://localhost:8088/data/flint/health
```

A `404` from `/data/flint/health` or `/data/flint/rpc` means the bridge module
is not installed or its Gateway scope is not running.