import time


def timestamp_now() -> int:
    """
    Return the current timestamp.

    Use this function to obtain the current timestamp in a consistent format
    across the application.

    Returns
    -------
    int
        The current timestamp in milliseconds
    """
    return time.time_ns() // 1_000_000
