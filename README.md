# ignition-env1

Minimal Docker Compose environment for Inductive Automation Ignition 8.3.6 and PostgreSQL.

Ignition gateway data is persisted in the Docker named volume `ignition-data`.
The project files are also exposed through a host bind mount at `./data/projects`,
mounted into the container at `/usr/local/bin/ignition/data/projects`, so you can
manage those files from the host while the rest of gateway data remains in the
named volume.

## Services

- Ignition Gateway: `inductiveautomation/ignition:8.3.6`
- PostgreSQL: `postgres:16`

## Usage

Start the environment:

```sh
docker compose up -d
```

Open Ignition:

```text
http://localhost:8088
```

Default development credentials:

```text
Ignition admin password: password
PostgreSQL database: ignition
PostgreSQL user: ignition
PostgreSQL password: ignition
```

From Ignition, use this JDBC URL when creating a PostgreSQL connection:

```text
jdbc:postgresql://postgres:5432/ignition
```

To customize local values:

```sh
cp .env.example .env
```

Then edit `.env` before starting the stack.

Stop the environment:

```sh
docker compose down
```

Remove containers and persistent volumes:

```sh
docker compose down -v
```
