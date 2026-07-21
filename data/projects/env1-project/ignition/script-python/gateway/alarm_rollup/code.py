"""Gateway-side projection for scoped equipment alarm roll-ups."""

import time
import traceback

import system


# Scope keys are the only scope identifiers allowed in Perspective navigation.
# Add an equipment definition here before embedding the shared roll-up elsewhere.
_SCOPE_REGISTRY = {
    "utility": {
        "label": "Utility",
        "paths": ("[T1]MBT1/Utility1/UtilitySource",),
    },
    "msg": {
        "label": "Main Switchgear",
        "paths": ("[T1]MBT1/Utility1/MSG1/MainSwitchgear",),
    },
    "pdu": {
        "label": "Power Distribution Unit",
        "paths": ("[T1]MBT1/Utility1/MSG1/PDU1/PDU",),
    },
    "transformer": {
        "label": "Transformer",
        "paths": ("[T1]MBT1/Utility1/MSG1/PDU1/Transformer1/Transformer",),
    },
    "way1": {
        "label": "Way 1 and Power Meter 1",
        "paths": (
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way1/Way",
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way1/PowerMeter1/PowerMeter",
        ),
        "sourceFilter": "prov:T1:/tag:MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way1/*",
    },
    "way2": {
        "label": "Way 2 and Power Meter 2",
        "paths": (
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way2/Way",
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way2/PowerMeter2/PowerMeter",
        ),
        "sourceFilter": "prov:T1:/tag:MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way2/*",
    },
    "way3": {
        "label": "Way 3 and Power Meter 3",
        "paths": (
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way3/Way",
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way3/PowerMeter3/PowerMeter",
        ),
        "sourceFilter": "prov:T1:/tag:MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way3/*",
    },
    "way4": {
        "label": "Way 4 and Power Meter 4",
        "paths": (
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way4/Way",
            "[T1]MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way4/PowerMeter4/PowerMeter",
        ),
        "sourceFilter": "prov:T1:/tag:MBT1/Utility1/MSG1/PDU1/PDUOutputBus/Way4/*",
    },
}

_PRIORITY_COLORS = {
    "Critical": "#b91c1c",
    "High": "#c2410c",
    "Medium": "#b45309",
    "Low": "#2563eb",
    "Diagnostic": "#475569",
}

_MONITORED_TOTAL_TTL_SECONDS = 300
_monitored_total_cache = {}


def get_rollup(scope_paths):
    """Return the active alarm projection for the supplied equipment roots."""
    try:
        paths = _normalize_paths(scope_paths)
        scope_key = _scope_key_for_paths(paths)
        events = _query_active_events(paths)
        priorities = _group_priorities(events)

        return {
            "activeTotal": len(events),
            "priorities": priorities,
            "priorityColor": _priority_color(priorities),
            "prioritySummary": _format_priorities(priorities),
            "monitoredTotal": _get_monitored_total(paths),
            "scopeKey": scope_key,
        }
    except:
        system.util.getLogger("gateway.alarm_rollup").error(traceback.format_exc())
        raise


def get_scope_details(scope_key):
    """Resolve a navigation scope key without exposing tag paths to the client."""
    definition = _SCOPE_REGISTRY.get(str(scope_key or ""))
    if not definition:
        return {"key": "", "label": "All equipment", "valid": False}

    return {
        "key": scope_key,
        "label": definition["label"],
        "valid": True,
    }


def get_alarm_source_filter(scope_key):
    """Return the Alarm Status Table source filter for a registered scope key."""
    definition = _SCOPE_REGISTRY.get(str(scope_key or ""))
    if not definition:
        return ""

    return definition.get("sourceFilter", _source_pattern(definition["paths"][0]))


def _format_priorities(priorities):
    """Format arbitrary non-empty priority groups for the compact header."""
    return " \u00b7 ".join(
        "%s %s" % (group["count"], group["name"])
        for group in priorities
        if group["count"] > 0
    )


def _priority_color(priorities):
    """Use the highest returned severity color; normal text remains graphite."""
    if not priorities:
        return "#1f2937"
    return _PRIORITY_COLORS.get(priorities[0]["name"], "#9f1239")


def _normalize_paths(scope_paths):
    if isinstance(scope_paths, basestring):
        scope_paths = [scope_paths]
    return tuple(
        _unwrap_qualified_value(path).rstrip("/")
        for path in (scope_paths or [])
        if path and _unwrap_qualified_value(path).strip()
    )


def _unwrap_qualified_value(value):
    while hasattr(value, "value"):
        next_value = value.value
        if next_value is value:
            break
        value = next_value
    return str(value)
def _scope_key_for_paths(paths):
    for key, definition in _SCOPE_REGISTRY.items():
        if paths == tuple(definition["paths"]):
            return key
    return ""


def _query_active_events(paths):
    if not paths:
        return []

    events = system.alarm.queryStatus(
        state=[
            "ActiveAcked",
            "ActiveUnacked",
        ],
        source=[_source_pattern(path) for path in paths],
    )
    return list(events)


def _group_priorities(events):
    groups = {}
    for event in events:
        priority = event.getPriority()
        name = _priority_name(priority)
        order = _priority_order(priority, name)
        group = groups.setdefault(name, {"name": name, "count": 0, "severityOrder": order})
        group["count"] += 1

    return sorted(groups.values(), key=lambda group: (-group["severityOrder"], group["name"]))


def _priority_name(priority):
    try:
        return str(priority.name())
    except AttributeError:
        return str(priority)


def _priority_order(priority, name):
    try:
        return int(priority.ordinal())
    except AttributeError:
        return {"Diagnostic": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(name, -1)


def _get_monitored_total(paths):
    cache_key = "|".join(paths)
    now = time.time()
    cached = _monitored_total_cache.get(cache_key)
    if cached and now - cached["checkedAt"] < _MONITORED_TOTAL_TTL_SECONDS:
        return cached["total"]

    total = sum(_count_configured_alarms(path) for path in paths)
    _monitored_total_cache[cache_key] = {"checkedAt": now, "total": total}
    return total


def _count_configured_alarms(instance_path):
    instance_config = system.tag.getConfiguration(instance_path, False)
    if not instance_config:
        return 0

    type_id = instance_config[0].get("typeId")
    definition_config = system.tag.getConfiguration(_udt_definition_path(instance_path, type_id), True)
    if not definition_config:
        return 0
    return _count_alarms_in_config(definition_config[0])

def _udt_definition_path(instance_path, type_id):
    provider_end = instance_path.find("]")
    provider = instance_path[1:provider_end]
    return "[%s]_types_/%s" % (provider, type_id)




def _count_alarms_in_config(tag_config):
    total = len(tag_config.get("alarms", []))
    for child in tag_config.get("tags", []):
        total += _count_alarms_in_config(child)
    return total


def _source_pattern(tag_path):
    provider_end = tag_path.find("]")
    if not tag_path.startswith("[") or provider_end < 1:
        raise ValueError("Scope path must include an Ignition tag provider: %s" % tag_path)
    provider = tag_path[1:provider_end]
    path = tag_path[provider_end + 1:].lstrip("/")
    return "prov:%s:/tag:%s/*" % (provider, path)
