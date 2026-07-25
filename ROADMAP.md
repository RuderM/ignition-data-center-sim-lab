# Future Revisions

## Automate third-party module installation

Embr Charts is currently installed manually through the Ignition Gateway. This
is fast enough for the current development workflow, so its module file is not
mounted by `compose.yaml`.

A future revision may provide the module binary automatically by adding this
file-level bind mount to the Ignition service:

```yaml
services:
  ignition:
    volumes:
      - ./modules/Embr-Charts-Ignition83-6.0.1.modl:/usr/local/bin/ignition/data/var/ignition/modl/Embr-Charts-Ignition83-6.0.1.modl:ro
```

The destination is the external-module folder configured by the Ignition 8.3.6
Docker entrypoint. Mounting the file alone does not accept a third-party signing
certificate or module EULA. Before adopting this configuration:

1. Install Embr Charts once through the Gateway and accept its certificate and
   EULA.
2. Confirm the module starts after recreating the Ignition container with the
   bind mount.
3. Run `./scripts/create-gateway-backup.sh` so fresh environments restore the
   certificate and EULA acceptance while the bind mount supplies the module
   binary.

If fully automatic acceptance is needed instead, use a controlled image-build
step that registers the module certificate and EULA in the backup configuration
database. Do not bypass module signature validation at runtime.
