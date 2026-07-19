# MBT1 Simplified Data Center EPMS — UDT Handoff

## Purpose

This file provides the context needed to continue development of a simplified data center Electrical Power Monitoring System (EPMS) in a future ChatGPT session.

The next major task is to use the accompanying CSV points list to create Ignition UDT definitions and UDT instances.

Companion file:

```text
MBT1_epms_points_list.csv
```

## Project Goal

Build a small but complete simulated data center EPMS as a hobby and learning project.

The system should demonstrate:

- Ignition UDT design
- Reusable equipment models
- Memory tags that can be driven by an Ignition-based simulator
- Electrical hierarchy and load rollups
- Alarming
- Tag history
- Perspective visualization
- MQTT integration in a later phase
- Docker-based infrastructure in a later phase
- Source-controlled configuration and documentation

This is not intended to be a detailed electrical engineering model. The priority is a compact, understandable, reusable system.

## Current Electrical Hierarchy

```text
MBT1
└── Utility_1
	└── MSG_1
		└── PDU_1
			├── Transformer_1
			└── PDU Output Bus
				├── Way_1
				│	└── PowerMeter_1
				├── Way_2
				│	└── PowerMeter_2
				├── Way_3
				│	└── PowerMeter_3
				└── Way_4
					└── PowerMeter_4
```

## Component Definitions

### Utility Source

Represents the external electrical utility feeding the site.

### Main Switchgear — MSG

Represents the main facility switchgear receiving utility power and feeding downstream distribution equipment.

The project currently contains one main switchgear instance:

```text
MSG_1
```

### Power Distribution Unit — PDU

Represents a floor-standing data center PDU.

The PDU receives power from the main switchgear and includes:

- An incoming breaker
- An internal transformer
- A secondary output bus
- Multiple outgoing ways

The project currently contains one PDU instance:

```text
PDU_1
```

### Transformer

Represents the transformer contained within the PDU.

For the initial simulated design, the transformer steps the PDU input from approximately 480 V to approximately 208 V.

### Way

A Way represents a breaker-protected outgoing circuit from the PDU output bus.

The project currently contains four Ways:

```text
Way_1
Way_2
Way_3
Way_4
```

Each Way contains a child Power Meter.

The Way owns breaker-related states and commands. The child Power Meter owns the detailed electrical measurements.

### Power Meter

A Power Meter represents branch-level electrical metering for a Way.

The Power Meter is the lowest modeled device level in the current project.

Server loads are intentionally not modeled as separate devices at this stage.

The simulator will drive the Power Meter values directly, and upstream device values will eventually be calculated or rolled up from the downstream meters.

## Current Scope

The model currently ends at the Power Meter level.

Do not create:

- ServerLoad UDTs
- Rack UDTs
- Server UDTs
- Generator UDTs
- UPS UDTs
- RPP or RSB UDTs

These may be added later, but they are outside the current scope.

## CSV File Purpose

The CSV is the source specification for the initial Ignition UDT definitions and instances.

Each row represents one atomic tag belonging to one device instance.

Important columns include:

```text
Site
DevicePath
ParentDevicePath
DeviceName
UDTType
Manufacturer
Model
TagPath
PointRole
DataType
ValueSource
Access
EngineeringUnits
EngLow
EngHigh
DefaultValue
Historize
HistoryDeadband
AlarmName
AlarmCondition
Description
```

## CSV Interpretation Rules

### UDT Definitions

Group CSV rows by:

```text
UDTType
```

Each unique `UDTType` should become one Ignition UDT definition.

Current expected UDT types are:

```text
UtilitySource
MainSwitchgear
PDU
Transformer
Way
PowerMeter
```

Within each UDT definition:

- Use `TagPath` as the relative path of the tag.
- Create folders implied by slash-delimited paths.
- Use `DataType` for the Ignition tag data type.
- Use `DefaultValue` as the initial value.
- Apply `EngineeringUnits`, `EngLow`, and `EngHigh` where appropriate.
- Use `Description` as tag documentation.
- Configure history when `Historize` is true.
- Configure alarms from `AlarmName` and `AlarmCondition` where practical.
- Preserve `PointRole` as documentation or as a custom property if useful.

### Tag Access

All tags in the current CSV are intentionally marked:

```text
ReadWrite
```

This is deliberate.

The first simulator will be implemented in Ignition and will write directly to the memory tags.

Do not convert measurement or status tags to read-only OPC tags during the first implementation.

### Value Source

The current CSV uses:

```text
Memory
```

Create memory tags unless a later request explicitly changes the architecture.

### UDT Instances

Create one UDT instance for every unique `DevicePath`.

Use:

- `DeviceName` as the instance name.
- `UDTType` as the UDT definition.
- `DevicePath` and `ParentDevicePath` to determine hierarchy.
- `Manufacturer` and `Model` as UDT parameter values or instance metadata.

Suggested UDT parameters:

```text
Manufacturer
Model
DeviceName
DevicePath
ParentDevicePath
```

Additional parameters may be introduced where they reduce duplication.

## Suggested Ignition Structure

A clean initial tag structure would be:

```text
[default]
├── _types_
│	├── UtilitySource
│	├── MainSwitchgear
│	├── PDU
│	├── Transformer
│	├── Way
│	└── PowerMeter
└── MBT1
	└── Utility_1
		└── MSG_1
			└── PDU_1
				├── Transformer_1
				├── Way_1
				│	└── PowerMeter_1
				├── Way_2
				│	└── PowerMeter_2
				├── Way_3
				│	└── PowerMeter_3
				└── Way_4
					└── PowerMeter_4
```

Ignition's exact handling of nested UDT instances should be considered carefully.

If nesting child UDT instances directly inside parent UDT instances creates unnecessary complexity, it is acceptable to place instances in folders that reproduce the same hierarchy.

Prefer a maintainable structure over clever inheritance or deep nesting.

## Simulator Expectations

The first simulator will be Ignition-native.

It will eventually:

- Write values to memory tags
- Simulate normal electrical variation
- Simulate breaker states and trips
- Vary branch loads at each Power Meter
- Sum Power Meter loads into the PDU
- Roll PDU load into the MSG
- Roll MSG load into the Utility
- Simulate alarms such as overload, undervoltage, communication loss, and breaker trip

The simulator should be implemented as a separate logical layer.

Do not embed random expressions independently throughout every UDT.

Prefer a centralized gateway script or project library that calculates values and writes them in batches.

## Design Preferences

- Keep the first version simple.
- Prefer explicit and readable structures.
- Avoid unnecessary UDT inheritance.
- Avoid creating tags that are not represented in the CSV unless required for Ignition mechanics.
- Use folders within UDTs based on `TagPath`.
- Preserve the ability to regenerate the UDTs if the CSV changes.
- Treat the CSV as the source of truth for the point definitions.
- Use tab indentation in any Python or Jython code samples.

## Expected Future Deliverable

When asked to create the UDTs from the CSV, produce one or more of the following as appropriate:

1. Ignition 8.1 tag JSON import file containing the UDT definitions
2. Ignition 8.1 tag JSON import file containing the UDT instances
3. A Jython gateway script that reads the CSV and creates or updates UDT definitions and instances using `system.tag.configure`
4. Documentation explaining how to import or run the generated output

The preferred approach should be selected based on maintainability and compatibility with Ignition 8.1.

If generating JSON directly is fragile, prefer a clear Jython generation script driven by the CSV.

## Suggested Prompt for a Future Chat

Upload both this file and the CSV, then use a prompt similar to:

```text
This Markdown file explains the project context and the CSV is the source points list.

Create the Ignition 8.1 UDT definitions and device instances described by the CSV.

Use the CSV as the source of truth. Group rows by UDTType, use TagPath as the relative tag path, create the implied folders, preserve history and alarm metadata, and create the MBT1 instance hierarchy.

All tags should remain read-write memory tags because an Ignition simulator will drive them later.

Provide the generated import files or a Jython system.tag.configure script, plus concise import instructions.
```

## Current Source Files

```text
MBT1_EPMS_UDT_HANDOFF.md
MBT1_epms_points_list.csv
```

These two files should be sufficient to seed a future session.
