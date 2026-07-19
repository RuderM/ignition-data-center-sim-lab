# MBT1 EPMS Simulator Handoff

## Implemented Project Script

The simulator logic lives in:

```text
data/projects/env1-project/ignition/script-python/gateway/epms_sim/code.py
```

Ignition project script path:

```python
project.gateway.epms_sim.tick()
```

The script reads manual source, breaker, and availability states from the `[T1]`
tag provider, simulates downstream PowerMeter values, and rolls calculated power
values upstream through Way, PDU, Transformer, Main Switchgear, and Utility tags.

It intentionally does not overwrite manual state tags such as source
availability, breaker closed/tripped states, or equipment faulted states.

## Gateway Timer Script Setup

Create this in Ignition Designer:

```text
Project Browser > Scripting > Gateway Events > Timer
```

Recommended settings:

```text
Name: MBT1_EPMS_Simulator
Delay: 10000
Delay Type: Fixed Delay
Enabled: true
Threading: Dedicated
```

Script body:

```python
project.gateway.epms_sim.tick()
```

## Validation Performed

- `resource.json` parsed successfully as JSON.
- `code.py` passed Python syntax compilation.
- Simulator write targets were checked against the current UDT point list.
- A mocked `system.tag` harness verified normal operation and utility-off
  behavior.
- Flint project scan returned success after adding the resource.
