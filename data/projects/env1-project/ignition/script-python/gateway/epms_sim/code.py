"""MBT1 EPMS data simulator.

This module is intended to be called by a Gateway Timer Script every 10 seconds:

    project.gateway.epms_sim.tick()

It keeps source and breaker state tags operator-controlled, then calculates
downstream meter loads and upstream rollups from those states.
"""

import math
import time

import system


PROVIDER = "[T1]"
SITE_ROOT = PROVIDER + "MBT1"
UTILITY = SITE_ROOT + "/Utility1/UtilitySource"
MSG = SITE_ROOT + "/Utility1/MSG1/MainSwitchgear"
PDU = SITE_ROOT + "/Utility1/MSG1/PDU1/PDU"
TRANSFORMER = SITE_ROOT + "/Utility1/MSG1/PDU1/Transformer1/Transformer"
OUTPUT_BUS = SITE_ROOT + "/Utility1/MSG1/PDU1/PDUOutputBus"

SQRT3 = math.sqrt(3.0)
TICK_SECONDS_DEFAULT = 10.0
TICK_SECONDS_MAX = 60.0

_last_tick_ms = None


WAYS = [
    {
        "way": OUTPUT_BUS + "/Way1/Way",
        "meter": OUTPUT_BUS + "/Way1/PowerMeter1/PowerMeter",
        "base_kw": 34.0,
        "pf_base": 0.965,
        "phase": 0.0,
    },
    {
        "way": OUTPUT_BUS + "/Way2/Way",
        "meter": OUTPUT_BUS + "/Way2/PowerMeter2/PowerMeter",
        "base_kw": 42.0,
        "pf_base": 0.955,
        "phase": 1.4,
    },
    {
        "way": OUTPUT_BUS + "/Way3/Way",
        "meter": OUTPUT_BUS + "/Way3/PowerMeter3/PowerMeter",
        "base_kw": 28.0,
        "pf_base": 0.972,
        "phase": 2.6,
    },
    {
        "way": OUTPUT_BUS + "/Way4/Way",
        "meter": OUTPUT_BUS + "/Way4/PowerMeter4/PowerMeter",
        "base_kw": 50.0,
        "pf_base": 0.948,
        "phase": 3.8,
    },
]


def tick():
    """Run one simulator update and return a small diagnostic summary."""
    logger = system.util.getLogger("gateway.epms_sim")
    now_ms = int(time.time() * 1000)
    elapsed_hours = _elapsed_hours(now_ms)

    try:
        state = _read_state()
        upstream_energized = _upstream_energized(state)
        timestamp = now_ms / 1000.0

        writes = {}
        totals = {
            "kw": 0.0,
            "kva": 0.0,
            "kvar": 0.0,
            "current": 0.0,
        }

        for index, way_cfg in enumerate(WAYS):
            way_result = _simulate_way(index, way_cfg, state, upstream_energized, timestamp, elapsed_hours)
            totals["kw"] += way_result["kw"]
            totals["kva"] += way_result["kva"]
            totals["kvar"] += way_result["kvar"]
            totals["current"] += way_result["current"]
            writes.update(way_result["writes"])

        aggregate = _aggregate_upstream(totals, state, upstream_energized, timestamp, elapsed_hours)
        writes.update(aggregate["writes"])

        _write_values(writes)
        return {
            "ok": True,
            "written": len(writes),
            "kw": round(totals["kw"], 2),
            "kva": round(totals["kva"], 2),
            "energized": upstream_energized,
        }
    except Exception:
        logger.error("MBT1 EPMS simulator tick failed: %s" % system.util.getExceptionInfo())
        return {"ok": False, "written": 0}


def _elapsed_hours(now_ms):
    global _last_tick_ms

    if _last_tick_ms is None:
        elapsed_seconds = TICK_SECONDS_DEFAULT
    else:
        elapsed_seconds = max(0.0, (now_ms - _last_tick_ms) / 1000.0)
        elapsed_seconds = min(elapsed_seconds, TICK_SECONDS_MAX)

    _last_tick_ms = now_ms
    return elapsed_seconds / 3600.0


def _read_state():
    paths = []
    for base in [UTILITY, MSG, PDU]:
        paths.extend([
            base + "/Status/Available",
            base + "/Status/Faulted",
        ])

    paths.extend([
        MSG + "/Breaker/MainClosed",
        MSG + "/Breaker/MainTripped",
        PDU + "/Breaker/InputClosed",
        PDU + "/Breaker/InputTripped",
        UTILITY + "/Capacity/RatedPower",
        MSG + "/Capacity/RatedCurrent",
        PDU + "/Capacity/RatedPower",
        TRANSFORMER + "/Capacity/RatedPower",
    ])

    for way_cfg in WAYS:
        way = way_cfg["way"]
        meter = way_cfg["meter"]
        paths.extend([
            way + "/Status/Available",
            way + "/Status/Enabled",
            way + "/Status/Faulted",
            way + "/Breaker/Closed",
            way + "/Breaker/Tripped",
            way + "/Config/RatedCurrent",
            meter + "/Power/RealPower",
            meter + "/Demand/PeakDemand",
            meter + "/Energy/TotalEnergy",
        ])

    values = _read_values(paths)
    state = dict(zip(paths, values))
    return state


def _read_values(paths):
    results = system.tag.readBlocking(paths)
    values = []
    for index, result in enumerate(results):
        default = 0.0
        if paths[index].endswith("/Status/Available"):
            default = True
        elif paths[index].endswith("/Status/Enabled"):
            default = True
        elif paths[index].endswith("/Breaker/MainClosed"):
            default = True
        elif paths[index].endswith("/Breaker/InputClosed"):
            default = True
        elif paths[index].endswith("/Breaker/Closed"):
            default = True
        elif paths[index].endswith("/Capacity/RatedPower"):
            if paths[index].startswith(UTILITY):
                default = 2000.0
            else:
                default = 225.0
        elif paths[index].endswith("/Capacity/RatedCurrent"):
            default = 2500.0
        elif paths[index].endswith("/Config/RatedCurrent"):
            default = 225.0

        try:
            if result.quality.isGood():
                values.append(result.value)
            else:
                values.append(default)
        except Exception:
            values.append(default)
    return values


def _upstream_energized(state):
    utility_ok = _state_bool(state, UTILITY + "/Status/Available", True)
    utility_ok = utility_ok and not _state_bool(state, UTILITY + "/Status/Faulted", False)

    msg_ok = _state_bool(state, MSG + "/Status/Available", True)
    msg_ok = msg_ok and not _state_bool(state, MSG + "/Status/Faulted", False)
    msg_ok = msg_ok and _state_bool(state, MSG + "/Breaker/MainClosed", True)
    msg_ok = msg_ok and not _state_bool(state, MSG + "/Breaker/MainTripped", False)

    pdu_ok = _state_bool(state, PDU + "/Status/Available", True)
    pdu_ok = pdu_ok and not _state_bool(state, PDU + "/Status/Faulted", False)
    pdu_ok = pdu_ok and _state_bool(state, PDU + "/Breaker/InputClosed", True)
    pdu_ok = pdu_ok and not _state_bool(state, PDU + "/Breaker/InputTripped", False)

    return utility_ok and msg_ok and pdu_ok


def _simulate_way(index, way_cfg, state, upstream_energized, timestamp, elapsed_hours):
    way = way_cfg["way"]
    meter = way_cfg["meter"]
    phase = way_cfg["phase"]

    way_active = upstream_energized
    way_active = way_active and _state_bool(state, way + "/Status/Available", True)
    way_active = way_active and _state_bool(state, way + "/Status/Enabled", True)
    way_active = way_active and not _state_bool(state, way + "/Status/Faulted", False)
    way_active = way_active and _state_bool(state, way + "/Breaker/Closed", True)
    way_active = way_active and not _state_bool(state, way + "/Breaker/Tripped", False)

    previous_kw = _state_float(state, meter + "/Power/RealPower", 0.0)
    peak_kw = _state_float(state, meter + "/Demand/PeakDemand", 0.0)
    energy_kwh = _state_float(state, meter + "/Energy/TotalEnergy", 0.0)

    if way_active:
        target_kw = _target_kw(way_cfg, timestamp)
        real_kw = _smooth(previous_kw, target_kw, 0.35)
        if real_kw < 1.0:
            real_kw = target_kw
        pf = _clamp(way_cfg["pf_base"] + 0.012 * math.sin(timestamp / 240.0 + phase), 0.92, 0.99)
        voltage_avg = _clamp(208.0 + 1.8 * math.sin(timestamp / 180.0 + phase), 204.0, 212.0)
        frequency = 60.0 + 0.035 * math.sin(timestamp / 210.0)
    else:
        real_kw = 0.0
        pf = way_cfg["pf_base"]
        voltage_avg = 0.0
        frequency = 0.0

    apparent_kva = _safe_divide(real_kw, pf, 0.0)
    reactive_kvar = math.sqrt(max(0.0, apparent_kva * apparent_kva - real_kw * real_kw))
    current_avg = _current_from_kva(apparent_kva, voltage_avg)
    currents = _phase_values(current_avg, 0.018, timestamp, phase)
    voltages = _phase_values(voltage_avg, 0.006, timestamp, phase + 0.8)
    rated_current = _state_float(state, way + "/Config/RatedCurrent", 225.0)
    way_load_pct = _safe_divide(current_avg, rated_current, 0.0) * 100.0
    energy_kwh += real_kw * elapsed_hours
    peak_kw = max(peak_kw, real_kw)

    writes = {
        meter + "/Voltage/PhaseAB": voltages[0],
        meter + "/Voltage/PhaseBC": voltages[1],
        meter + "/Voltage/PhaseCA": voltages[2],
        meter + "/Voltage/LLAvg": voltage_avg,
        meter + "/Voltage/UnbalancePct": _unbalance_pct(voltages),
        meter + "/Current/PhaseA": currents[0],
        meter + "/Current/PhaseB": currents[1],
        meter + "/Current/PhaseC": currents[2],
        meter + "/Current/Avg": current_avg,
        meter + "/Current/UnbalancePct": _unbalance_pct(currents),
        meter + "/Frequency": frequency,
        meter + "/Power/RealPower": real_kw,
        meter + "/Power/ApparentPower": apparent_kva,
        meter + "/Power/ReactivePower": reactive_kvar,
        meter + "/Power/PowerFactor": pf,
        meter + "/Energy/TotalEnergy": energy_kwh,
        meter + "/Demand/PeakDemand": peak_kw,
        way + "/Electrical/CurrentAvg": current_avg,
        way + "/Power/RealPower": real_kw,
        way + "/Capacity/LoadPct": way_load_pct,
        way + "/Alarms/Overload": way_load_pct > 100.0,
    }

    return {
        "kw": real_kw,
        "kva": apparent_kva,
        "kvar": reactive_kvar,
        "current": current_avg,
        "writes": _rounded_writes(writes),
    }


def _aggregate_upstream(totals, state, upstream_energized, timestamp, elapsed_hours):
    writes = {}
    total_kw = totals["kw"]
    total_kva = totals["kva"]
    total_kvar = totals["kvar"]
    total_pf = _safe_divide(total_kw, total_kva, 0.97)

    pdu_load_pct = _load_pct(total_kva, _state_float(state, PDU + "/Capacity/RatedPower", 225.0))
    tx_load_pct = _load_pct(total_kva, _state_float(state, TRANSFORMER + "/Capacity/RatedPower", 225.0))
    efficiency_pct = _transformer_efficiency(tx_load_pct, total_kva)
    efficiency = max(efficiency_pct / 100.0, 0.01)
    upstream_kw = _safe_divide(total_kw, efficiency, 0.0)
    upstream_kva = _safe_divide(total_kva, efficiency, 0.0)
    upstream_pf = _safe_divide(upstream_kw, upstream_kva, 0.97)

    pdu_output_voltage = 208.0 if upstream_energized else 0.0
    pdu_input_voltage = 480.0 if upstream_energized else 0.0
    utility_voltage = 13800.0 if upstream_energized else 0.0
    frequency = 60.0 + 0.035 * math.sin(timestamp / 210.0) if upstream_energized else 0.0

    pdu_output_current = _current_from_kva(total_kva, pdu_output_voltage)
    msg_current = _current_from_kva(upstream_kva, pdu_input_voltage)
    utility_current = _current_from_kva(upstream_kva, utility_voltage)

    pdu_energy = _read_float(PDU + "/Energy/TotalEnergy", 0.0) + total_kw * elapsed_hours
    msg_energy = _read_float(MSG + "/Energy/TotalEnergy", 0.0) + upstream_kw * elapsed_hours
    utility_energy = _read_float(UTILITY + "/Energy/TotalEnergy", 0.0) + upstream_kw * elapsed_hours

    pdu_temp = 27.0 + 0.08 * pdu_load_pct + 1.2 * math.sin(timestamp / 900.0)
    tx_winding_temp = 42.0 + 0.42 * tx_load_pct + 1.8 * math.sin(timestamp / 1200.0)
    tx_enclosure_temp = 29.0 + 0.15 * tx_load_pct + 1.0 * math.sin(timestamp / 1000.0)

    msg_load_pct = _safe_divide(msg_current, _state_float(state, MSG + "/Capacity/RatedCurrent", 2500.0), 0.0) * 100.0
    utility_load_pct = _load_pct(upstream_kva, _state_float(state, UTILITY + "/Capacity/RatedPower", 2000.0))

    writes.update({
        PDU + "/Electrical/InputVoltageLLAvg": pdu_input_voltage,
        PDU + "/Electrical/OutputVoltageLLAvg": pdu_output_voltage,
        PDU + "/Electrical/OutputCurrentAvg": pdu_output_current,
        PDU + "/Power/RealPower": total_kw,
        PDU + "/Power/ApparentPower": total_kva,
        PDU + "/Power/PowerFactor": total_pf,
        PDU + "/Energy/TotalEnergy": pdu_energy,
        PDU + "/Capacity/LoadPct": pdu_load_pct,
        PDU + "/Temperature/EnclosureTemp": pdu_temp,
        PDU + "/Alarms/Overload": pdu_load_pct > 100.0,
        TRANSFORMER + "/Electrical/PrimaryVoltageLLAvg": pdu_input_voltage,
        TRANSFORMER + "/Electrical/SecondaryVoltageLLAvg": pdu_output_voltage,
        TRANSFORMER + "/Electrical/SecondaryCurrentAvg": pdu_output_current,
        TRANSFORMER + "/Power/RealPower": total_kw,
        TRANSFORMER + "/Power/ApparentPower": total_kva,
        TRANSFORMER + "/Capacity/LoadPct": tx_load_pct,
        TRANSFORMER + "/Temperature/WindingTemp": tx_winding_temp,
        TRANSFORMER + "/Temperature/EnclosureTemp": tx_enclosure_temp,
        TRANSFORMER + "/Efficiency/Pct": efficiency_pct,
        TRANSFORMER + "/Alarms/Overtemperature": tx_winding_temp > 120.0,
        TRANSFORMER + "/Alarms/Overload": tx_load_pct > 100.0,
        MSG + "/Electrical/BusVoltageLLAvg": pdu_input_voltage,
        MSG + "/Electrical/BusCurrentAvg": msg_current,
        MSG + "/Electrical/Frequency": frequency,
        MSG + "/Power/RealPower": upstream_kw,
        MSG + "/Power/ApparentPower": upstream_kva,
        MSG + "/Power/PowerFactor": upstream_pf,
        MSG + "/Energy/TotalEnergy": msg_energy,
        MSG + "/Capacity/LoadPct": msg_load_pct,
        UTILITY + "/Electrical/VoltageLLAvg": utility_voltage,
        UTILITY + "/Electrical/CurrentAvg": utility_current,
        UTILITY + "/Electrical/Frequency": frequency,
        UTILITY + "/Power/RealPower": upstream_kw,
        UTILITY + "/Power/ApparentPower": upstream_kva,
        UTILITY + "/Power/PowerFactor": upstream_pf,
        UTILITY + "/Energy/TotalEnergy": utility_energy,
        UTILITY + "/Capacity/LoadPct": utility_load_pct,
    })

    return {"writes": _rounded_writes(writes)}


def _target_kw(way_cfg, timestamp):
    phase = way_cfg["phase"]
    local_hour = time.localtime(timestamp).tm_hour + (time.localtime(timestamp).tm_min / 60.0)
    daily = 0.91 + 0.13 * math.sin((2.0 * math.pi * (local_hour - 5.0) / 24.0) + phase / 6.0)
    slow = 1.0 + 0.045 * math.sin(timestamp / 420.0 + phase)
    medium = 1.0 + 0.080 * math.sin(timestamp / 36.0 + phase * 1.7)
    return max(0.0, way_cfg["base_kw"] * daily * slow * medium)


def _phase_values(avg, spread, timestamp, phase):
    if avg <= 0.0:
        return [0.0, 0.0, 0.0]

    a = avg * (1.0 + spread * math.sin(timestamp / 180.0 + phase))
    b = avg * (1.0 + spread * math.sin(timestamp / 180.0 + phase + 2.1))
    c = avg * (1.0 + spread * math.sin(timestamp / 180.0 + phase + 4.2))
    correction = avg / _safe_divide(a + b + c, 3.0, avg)
    return [a * correction, b * correction, c * correction]


def _transformer_efficiency(load_pct, total_kva):
    if total_kva <= 0.0:
        return 97.5

    load_frac = _clamp(load_pct / 100.0, 0.05, 1.4)
    return _clamp(96.7 + 1.1 * math.sqrt(load_frac) - 0.45 * load_frac, 95.0, 98.2)


def _write_values(writes):
    paths = []
    values = []
    for path in sorted(writes.keys()):
        paths.append(path)
        values.append(writes[path])
    if paths:
        system.tag.writeBlocking(paths, values)


def _read_float(path, default):
    result = system.tag.readBlocking([path])[0]
    try:
        if result.quality.isGood():
            return float(result.value)
    except Exception:
        pass
    return default


def _state_bool(state, path, default):
    value = state.get(path, default)
    if value is None:
        return default
    return bool(value)


def _state_float(state, path, default):
    try:
        value = state.get(path, default)
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _current_from_kva(kva, volts_ll):
    if kva <= 0.0 or volts_ll <= 0.0:
        return 0.0
    return kva * 1000.0 / (SQRT3 * volts_ll)


def _load_pct(kva, rated_kva):
    return _safe_divide(kva, rated_kva, 0.0) * 100.0


def _unbalance_pct(values):
    avg = _safe_divide(sum(values), len(values), 0.0)
    if avg <= 0.0:
        return 0.0
    return max([abs(value - avg) for value in values]) / avg * 100.0


def _smooth(previous, target, alpha):
    if previous <= 0.0:
        return target
    return previous + alpha * (target - previous)


def _safe_divide(numerator, denominator, default):
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception:
        return default


def _clamp(value, low, high):
    return max(low, min(high, value))


def _rounded_writes(writes):
    rounded = {}
    for path, value in writes.items():
        if isinstance(value, bool):
            rounded[path] = value
        else:
            rounded[path] = round(float(value), 3)
    return rounded
