"""Gateway health examples that reference common Ignition system functions."""

import system

import project.util.dates as date_utils
import project.util.math as math_utils


def read_gateway_snapshot():
    """Read a few System tags and return a small health snapshot."""
    paths = [
        "[System]Gateway/SystemName",
        "[System]Gateway/LicenseState",
        "[System]Gateway/UptimeSeconds",
    ]
    results = system.tag.readBlocking(paths)

    uptime_seconds = results[2].value
    uptime_days = math_utils.safe_divide(uptime_seconds, 86400, 0)

    return {
        "name": results[0].value,
        "licenseState": results[1].value,
        "uptimeSeconds": uptime_seconds,
        "uptimeDays": round(uptime_days, 2),
        "checkedAt": date_utils.now_iso(),
    }


def get_license_status():
    """Return a normalized license status string."""
    snapshot = read_gateway_snapshot()
    state = str(snapshot.get("licenseState", "Unknown"))
    if state.lower() == "valid":
        return "Good"
    return "Warning"


def log_gateway_snapshot():
    """Write the current gateway snapshot to the wrapper log."""
    snapshot = read_gateway_snapshot()
    system.util.getLogger("gateway.health").info("Gateway snapshot: %s" % snapshot)
    return snapshot
