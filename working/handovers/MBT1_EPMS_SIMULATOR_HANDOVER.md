# MBT1 EPMS Simulator Handover

Date: 2026-07-19

## Context

This session added an Ignition-native EPMS simulator for the MBT1 data center
model. The simulator is intended to run from an Ignition Gateway Timer Event
every 10 seconds.

The project charter specifically wanted downstream branch power meter loads to
roll up through parent devices instead of unrelated random values. The current
implementation follows that model.

## Implemented Files

Ignition project script:

```text
data/projects/env1-project/ignition/script-python/gateway/epms_sim/code.py
data/projects/env1-project/ignition/script-python/gateway/epms_sim/resource.json
```

Designer project-library path:

```python
project.gateway.epms_sim.tick()
```

The helper handoff created earlier is also present:

```text
working/Simulator/MBT1_EPMS_SIMULATOR_HANDOFF.md
```

## Runtime Setup

The script module exists in the project, but the Gateway Timer Event is a
Designer-side setup step unless it has already been created manually.

Recommended Designer setup:

```text
Project Browser > Scripting > Gateway Events > Timer

Name: MBT1_EPMS_Simulator
Delay: 10000
Delay Type: Fixed Delay
Threading: Dedicated
Enabled: true
```

Script body:

```python
project.gateway.epms_sim.tick()
```

## Behavior

The simulator reads manual source and breaker states, then writes calculated
measurements and rollups.

It does not overwrite operator-controlled state tags such as:

```text
Status/Available
Status/CommGood
Status/Faulted
Breaker/*Closed
Breaker/*Tripped
```

It simulates the downstream meters:

```text
[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way1/PowerMeter1/PowerMeter
[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way2/PowerMeter2/PowerMeter
[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way3/PowerMeter3/PowerMeter
[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way4/PowerMeter4/PowerMeter
```

Then it rolls values up to:

```text
Way
PDU
Transformer
MainSwitchgear
UtilitySource
```

## Load Profile

The branch kW target uses deterministic waves:

```python
base_kw * daily * slow * medium
```

Current tuning:

```python
daily = 0.91 +/- 0.13 over a daily cycle
slow = 1.0 +/- 0.045 on a slower cycle
medium = 1.0 +/- 0.080 on about a 3.8 minute cycle
```

This was increased from a smaller `+/- 2%` medium wave because whole-number
display cards looked too static.

The simulator still smooths each tick toward the target:

```python
_smooth(previous_kw, target_kw, 0.35)
```

## Validation Already Performed

- Project script JSON parsed successfully.
- Python syntax compilation passed.
- A mocked `system.tag` harness verified normal operation and utility-off
  behavior.
- Simulator write target suffixes were checked against the current UDT point
  list.
- `./scripts/flint-project-scan.sh` returned success after changes.
- New Ignition resources were handed back to UID/GID `2003:2003`.

## Useful Checks

Manual Script Console test:

```python
project.gateway.epms_sim.tick()
```

History check example used later in the session:

```python
path = "[T1]MBT1/Utility1/MSG1/PDU1/PDU/Power/RealPower"

ds = system.tag.queryTagHistory(
    paths=[path],
    startDate=system.date.addMinutes(system.date.now(), -30),
    endDate=system.date.now(),
    returnSize=20,
    aggregationMode="LastValue",
    returnFormat="Wide"
)

print "Rows:", ds.getRowCount()
for row in range(ds.getRowCount()):
    print ds.getValueAt(row, 0), ds.getValueAt(row, 1)
```

History was confirmed working by the user.

