"""Small numeric helpers for project script examples."""


def clamp(value, minimum, maximum):
    """Clamp value between minimum and maximum."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def safe_divide(numerator, denominator, fallback=0):
    """Divide two numbers and return fallback when the denominator is zero."""
    if denominator in (None, 0):
        return fallback
    return float(numerator) / float(denominator)


def percent(part, whole):
    """Return part as a percentage of whole."""
    return round(safe_divide(part, whole, 0) * 100, 2)


def average(values):
    """Return the arithmetic mean of a list of numbers."""
    if not values:
        return 0
    return safe_divide(sum(values), len(values), 0)


def moving_average(values, window_size):
    """Return a simple moving average series."""
    if window_size <= 0:
        raise ValueError("window_size must be greater than zero")

    results = []
    for index in range(len(values)):
        window = values[max(0, index - window_size + 1) : index + 1]
        results.append(average(window))
    return results
