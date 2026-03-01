"""Data models for WebUntis public timetable API responses."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import date, time


class ElementType(enum.IntEnum):
    """WebUntis element type identifiers."""
    CLASS = 1
    TEACHER = 2
    SUBJECT = 3
    ROOM = 4
    STUDENT = 5


@dataclass(frozen=True)
class Element:
    """A resolved timetable element (teacher, subject, room, etc.)."""
    type: ElementType
    id: int
    name: str
    long_name: str = ""
    alternate_name: str = ""


@dataclass(frozen=True)
class Period:
    """A single timetable period (one lesson slot)."""
    date: date
    start_time: time
    end_time: time
    subjects: tuple[Element, ...] = ()
    teachers: tuple[Element, ...] = ()
    rooms: tuple[Element, ...] = ()
    classes: tuple[Element, ...] = ()
    lesson_id: int | None = None
    lesson_code: str = ""
    cell_state: str = ""
    lesson_text: str = ""
    period_text: str = ""


@dataclass(frozen=True)
class ClassGroup:
    """A class/group entry from the WebUntis page configuration."""
    id: int
    name: str
    long_name: str = ""


@dataclass(frozen=True)
class WeeklyTimetable:
    """Timetable data for one class for one week."""
    class_id: int
    week_start: date
    periods: tuple[Period, ...] = ()


@dataclass(frozen=True)
class SemesterTimetable:
    """Aggregated timetable data for one class across a full semester."""
    class_id: int
    start: date
    end: date
    weeks: tuple[WeeklyTimetable, ...] = ()

    @property
    def periods(self) -> tuple[Period, ...]:
        """All periods across all weeks, flattened."""
        return tuple(p for w in self.weeks for p in w.periods)
