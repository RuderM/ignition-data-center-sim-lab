# Browser and Flint verification prerequisites

- Date: 2026-07-25
- Scope: Perspective verification tooling and project documentation

## Result

The root README now records the workstation and Gateway prerequisites needed to
repeat automated Perspective browser checks and Flint project scans.

## Changes

- Added browser verification guidance to `README.md`.
- Documented the live Perspective client URL and page-configuration check.
- Documented Chromium's `unzip` and shared-library prerequisites on minimal
  Ubuntu installations, including `t64` package-name differences and `ldd`
  troubleshooting.
- Documented recovery from an incomplete empty managed-browser cache directory.
- Documented safe project reload with `docker compose restart ignition` and the
  prohibition on using `docker compose down -v` merely to reload resources.
- Documented the Ignition 8.3 Flint Designer Bridge artifact and the public
  `/data/flint/health` check.

## Verification

- Installed the missing extractor and Chromium runtime libraries on the active
  workstation.
- Launched the managed Chromium build and exercised the live Perspective client.
- Initially observed `404` from Flint RPC while the bridge was absent.
- After the bridge was installed, observed an `ok` Flint health response and a
  successful `project.scan` result.

## Follow-ups

- Install the matching Flint Designer Bridge module on any new Gateway before
  expecting `./scripts/flint-project-scan.sh` to work.
