"""Example batch helpers for exercising Flint's Jython language support."""

import system

import project.util.math as math_utils


def summarize_numbers(values):
    """Return a summary dictionary for a list of numeric values."""
    cleaned = []
    for value in values:
        try:
            cleaned.append(float(value))
        except (TypeError, ValueError):
            system.util.getLogger("demo.batch").warn(
                "Skipping non-numeric value: %r" % value
            )

    return {
        "count": len(cleaned),
        "total": sum(cleaned),
        "average": math_utils.average(cleaned),
        "minimum": min(cleaned) if cleaned else None,
        "maximum": max(cleaned) if cleaned else None,
    }


def group_by_status(items):
    """Group dictionaries that contain a status key."""
    grouped = {}
    for item in items:
        status = item.get("status", "Unknown")
        grouped.setdefault(status, []).append(item)
    return grouped


def log_summary(values):
    """Compute a summary and write it to the gateway log."""
    summary = summarize_numbers(values)
    system.util.getLogger("demo.batch").info("Summary: %s" % summary)
    return summary
