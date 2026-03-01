"""Date and time utilities for WebUntis data."""

from __future__ import annotations

import datetime
from collections.abc import Iterator


def iter_mondays(start: datetime.date, end: datetime.date) -> Iterator[datetime.date]:
    """Yield every Monday between *start* and *end* (inclusive).

    If *start* is not a Monday, advances to the next Monday first.
    """
    current = start
    while current.weekday() != 0:
        current += datetime.timedelta(days=1)
    while current <= end:
        yield current
        current += datetime.timedelta(days=7)


def parse_date(d: int) -> datetime.date:
    """Convert a WebUntis date integer (e.g. ``20260302``) to a :class:`datetime.date`."""
    s = str(d)
    return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def parse_time(t: int) -> datetime.time:
    """Convert a WebUntis time integer (e.g. ``800`` -> 08:00, ``1345`` -> 13:45)."""
    return datetime.time(t // 100, t % 100)


def format_date(d: int) -> str:
    """Format a WebUntis date integer as ``YYYY-MM-DD``."""
    s = str(d)
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"


def format_time(t: int) -> str:
    """Format a WebUntis time integer as ``HH:MM``."""
    return f"{t // 100:02d}:{t % 100:02d}"


def weekday_name(d: int) -> str:
    """Return the English weekday name for a WebUntis date integer."""
    return parse_date(d).strftime("%A")
