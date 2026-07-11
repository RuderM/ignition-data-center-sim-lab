"""Date and time utility functions for Ignition project scripts."""

import system


DEFAULT_FORMAT = "yyyy-MM-dd HH:mm:ss"


def now():
    """Return the current gateway date."""
    return system.date.now()


def now_iso():
    """Return the current gateway date formatted for logs and payloads."""
    return system.date.format(now(), "yyyy-MM-dd'T'HH:mm:ss")


def format_timestamp(value, pattern=DEFAULT_FORMAT):
    """Format a Java Date using an Ignition date pattern."""
    if value is None:
        return ""
    return system.date.format(value, pattern)


def minutes_between(start_date, end_date):
    """Return the whole-minute difference between two Java Date values."""
    if start_date is None or end_date is None:
        return 0
    millis = system.date.millisBetween(start_date, end_date)
    return int(millis / 60000)


def is_stale(last_seen, max_age_minutes):
    """Return True when last_seen is older than max_age_minutes."""
    return minutes_between(last_seen, now()) > int(max_age_minutes)
