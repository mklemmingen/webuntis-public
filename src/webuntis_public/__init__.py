"""WebUntis public timetable API client — no authentication required."""

from .client import WebUntisError, WebUntisPublicClient
from .models import (
    ClassGroup,
    Element,
    ElementType,
    Period,
    SemesterTimetable,
    WeeklyTimetable,
)
from .semester import format_date, format_time, iter_mondays, parse_date, parse_time

__all__ = [
    "ClassGroup",
    "Element",
    "ElementType",
    "Period",
    "SemesterTimetable",
    "WeeklyTimetable",
    "WebUntisError",
    "WebUntisPublicClient",
    "format_date",
    "format_time",
    "iter_mondays",
    "parse_date",
    "parse_time",
]

__version__ = "0.1.0"
