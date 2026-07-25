# Perspective `sg-simple` policy

- Date: 2026-07-25
- Scope: `working/agent-skills/PERSPECTIVE_SCREEN_AGENT.md`

## Result

Future Perspective agents now have an explicit requirement to use the current
`sg-simple` design system for every new screen and substantial redesign.

## Changes

- Made `sg-simple` mandatory for new screens and substantial redesigns.
- Limited legacy `sg` use to small changes within existing legacy visual regions.
- Prohibited using conceptual wireframes as justification for repeated inline
  visual declarations.
- Restricted inline styles to layout, sizing, spacing, overflow, data-bound
  state, and Perspective limitations.
- Added a required pre-delivery audit of edited `props.style` objects.
- Added project-specific lessons covering authoritative tag-model research,
  fixed overview paths versus reusable `baseTagPath`, route verification,
  shared-dock viewport checks, live browser checks, safe Gateway reloads, Flint
  separation, and Ignition ownership.

## Verification

- Confirmed the agent skill contains the mandatory policy and matching validation
  checklist entries.

## Follow-ups

- Existing screens are not automatically compliant merely because the policy is
  documented; migrations must still be performed and verified.
