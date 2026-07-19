"""Helpers for Perspective trend charts."""

import system


def get_apex_line_series(tag_path, hours=1, label="Trend"):
    """Return tag history formatted for an EMBR ApexCharts line series."""
    logger = system.util.getLogger("util.trends")

    if not tag_path:
        return [{"name": label or "Trend", "data": []}]

    tag_path = str(tag_path)
    label = str(label or "Trend")

    try:
        hours = int(hours)
    except (TypeError, ValueError):
        hours = 1

    if hours not in (1, 8):
        hours = 1

    end_date = system.date.now()
    start_date = system.date.addHours(end_date, -hours)
    return_size = 60 if hours == 1 else 96

    try:
        data = system.tag.queryTagHistory(
            paths=[tag_path],
            startDate=start_date,
            endDate=end_date,
            returnSize=return_size,
            aggregationMode="Average",
            returnFormat="Wide",
        )
    except Exception:
        logger.warn(
            "Unable to query trend history for %s: %s"
            % (tag_path, system.util.getExceptionInfo())
        )
        return [{"name": label, "data": []}]

    points = []
    for row in range(data.getRowCount()):
        timestamp = data.getValueAt(row, 0)
        value = data.getValueAt(row, 1)
        if timestamp is None or value is None:
            continue

        try:
            y_value = round(float(value), 3)
        except (TypeError, ValueError):
            continue

        points.append({
            "x": timestamp.getTime(),
            "y": y_value,
        })

    return [{
        "name": label,
        "data": points,
    }]
