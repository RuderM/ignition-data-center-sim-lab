# Header Logo and Page Icons Handover

Date: 2026-07-19

## Context

This session also worked on visual identity assets for the Perspective UI:

- A compact MBT1 data center logo intended for the top-left nav.
- Page header icons for Utility, MSG, and PDU.

The first page-icon set was too illustrative. The second set follows electrical
one-line diagram conventions and adds modest UI polish.

## Logo Assets

Created under:

```text
working/Logo/
```

Files:

```text
working/Logo/mbt1-data-center-logo.svg
working/Logo/mbt1-data-center-logo.png
working/Logo/mbt1-data-center-logo-data-uri.txt
working/Logo/generate_mbt1_logo.py
working/Logo/decoded-from-data-uri.png
```

Logo PNG:

```text
106 x 93
```

This matches the dimensions of the original base64 logo prefix the user
provided.

Important correction:

- The first generated data URI had a literal trailing `\n` in the base64 payload,
  which caused a broken image icon.
- The generator was fixed to write a real newline.
- The current `mbt1-data-center-logo-data-uri.txt` round-trip decodes to the
  PNG successfully.

Validation performed:

```text
Base64 payload length divisible by 4
No invalid base64 characters
Decoded PNG matches source PNG
PNG signature valid
Dimensions 106 x 93
```

## Page Icon Assets

First attempt, preserved for comparison:

```text
working/PageIcons/utility-icon.svg
working/PageIcons/msg-icon.svg
working/PageIcons/pdu-icon.svg
```

Preferred second attempt:

```text
working/PageIcons/oneline-style/utility-oneline-icon.svg
working/PageIcons/oneline-style/msg-oneline-icon.svg
working/PageIcons/oneline-style/pdu-oneline-icon.svg
```

The second set uses one-line electrical references:

```text
Utility: source circle / sine wave / incoming feeder
MSG: bus bar with breaker/feeders
PDU: transformer coils and branch distribution
```

Palette follows the existing project style:

```text
Dark ink: #16213e
Blue accent: #2f80ed
Teal accent: #18a999
Amber power accent: #f5b84b
Border: #d9e2ef
White panel background
```

All SVGs were validated as well-formed XML.

## Header Wiring

The one-line-style icons are currently embedded into:

```text
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/Utility/view.json
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/MSG/view.json
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/PDU/view.json
```

Implementation:

- Each header contains a `titleRow`.
- `titleRow` contains:

```text
screenTitle
pageIcon
```

- `pageIcon` is an `ia.display.image`.
- The SVG is embedded as:

```text
data:image/svg+xml;base64,...
```

The user accidentally overwrote the icons once. They were re-added by re-running
the header injection logic.

## Validation Already Performed

- Utility/MSG/PDU `view.json` files parsed as JSON.
- Header structure was checked and showed `titleRow` plus `pageIcon`.
- `./scripts/flint-project-scan.sh` returned success after re-adding icons.
- Edited view files were handed back to UID/GID `2003:2003`.

## Notes for Future Work

When updating these icons again:

- Keep SVG sources in `working/PageIcons/oneline-style`.
- Base64-embed SVGs into `ia.display.image.props.source` only when ready to
  apply them to Perspective views.
- Preserve the `titleRow` pattern to avoid layout drift.
- After edits, run:

```sh
python3 -m json.tool <edited view.json> >/dev/null
./scripts/flint-project-scan.sh
sudo chown 2003:2003 <edited Ignition project files>
```

