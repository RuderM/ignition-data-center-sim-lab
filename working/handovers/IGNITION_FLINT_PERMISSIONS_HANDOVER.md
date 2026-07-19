# Ignition/Flint Permissions Handover

Date: 2026-07-19

## Context

This repo is an Ignition 8.3.6 Docker Compose development environment.

- Repo: `/home/ubuntu/projects/ignition-env1`
- Project: `data/projects/env1-project`
- Ignition container: `ignition-env1-gateway`
- Ignition image: `inductiveautomation/ignition:8.3.6`
- Ignition process user inside container: UID/GID `2003:2003`
- VS Code Remote SSH user on host: `ubuntu` UID/GID `1000:1000`

The project files are bind-mounted:

```text
./data/projects:/usr/local/bin/ignition/data/projects
```

This means host Linux permissions directly affect both Ignition Designer saves
and VS Code/Flint edits.

## Original Symptoms

Designer save failed on a Perspective view thumbnail temp file:

```text
PushException: I/O error during prepare:
/usr/local/bin/ignition/data/projects/env1-project/com.inductiveautomation.perspective/views/Exchange/Responsive Nav/Nav/thumbnail.png.tmp
```

Flint/VS Code edit failed with:

```text
Failed to save 'view.json': Unable to write file ... EACCES: permission denied
```

Example failing file:

```text
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/Utility/view.json
```

## Root Cause

Files created or rewritten by Ignition are owned by UID/GID `2003:2003`, often
with mode `0644`. VS Code runs as `ubuntu`, so it could not write those files.

Files created by VS Code/agents as `ubuntu` could create the opposite problem:
Ignition can read them, but may not be able to update thumbnails, `resource.json`,
or temp replacement files later.

The real goal is not a specific username. The goal is:

- Ignition-owned resources remain compatible with Ignition.
- `ubuntu` can edit them through VS Code/Flint.
- Newly created project resources should not be left in a state that blocks
  Ignition Designer.

## Changes Applied

Installed the Ubuntu `acl` package so `setfacl` and `getfacl` are available.

Applied ACLs to only this tree:

```text
data/projects/env1-project
```

Effective intent:

- Existing ownership is preserved.
- `ubuntu` can read/write project files.
- UID/GID `2003` can read/write project files.
- New files/directories under the project inherit write access for both.

Verified after ACL application:

```text
ubuntu-can-write-view-json
ignition-can-write-view-json
```

for:

```text
data/projects/env1-project/com.inductiveautomation.perspective/views/DataCenter/Utility/view.json
```

## Agent Policy Added

Updated `working/agent-skills/PERSPECTIVE_SCREEN_AGENT.md` with a filesystem
ownership policy.

Any new Ignition project resource created under `data/projects/env1-project`
must be handed back to Ignition ownership before completion:

```sh
sudo chown -R 2003:2003 "data/projects/env1-project/path/to/new/resource"
```

Do not change ownership of unrelated files. Preserve the ACLs.

## Future Guidance

When creating new Perspective views or other Ignition resources:

1. Create/edit the required files.
2. Validate JSON and resource structure.
3. Set ownership only on newly created resource directories/files to `2003:2003`.
4. Do not run broad `chown` unless explicitly requested.
5. If VS Code or Designer hits permission errors again, inspect with:

```sh
namei -l "path/to/file"
getfacl -p "path/to/file"
```

If a new directory does not inherit ACLs as expected, reapply ACLs narrowly to
that directory, not the entire host filesystem.

## Related Flint Finding

The Flint command `flint.copyResourcePath` also failed during this session, but
the VS Code extension-host log indicated a separate extension issue:

```text
TypeError: Error processing argument at index 0, conversion failure
```

That command was passing an object to VS Code's clipboard API instead of a string.
This is likely unrelated to Linux file permissions.
