"""Parsing helpers for WebUntis REST API v1 JSON responses."""

from __future__ import annotations

import datetime

from .models import ClassGroup, Element, ElementType, Period, WeeklyTimetable

# Mapping from REST API type strings to ElementType enum values
_TYPE_MAP: dict[str, ElementType] = {
    "SUBJECT": ElementType.SUBJECT,
    "TEACHER": ElementType.TEACHER,
    "ROOM": ElementType.ROOM,
    "CLASS": ElementType.CLASS,
    "STUDENT": ElementType.STUDENT,
}


def _parse_position_elements(
    position_items: list[dict] | None,
    expected_type: ElementType | None = None,
) -> list[Element]:
    """Parse a position array from a grid entry into Element objects.

    Each position item has ``{"current": {"type": ..., "shortName": ...}, "removed": ...}``.
    """
    if not position_items:
        return []
    elements: list[Element] = []
    for item in position_items:
        current = item.get("current")
        if current is None:
            continue
        elem_type = _TYPE_MAP.get(current.get("type", ""), None)
        if elem_type is None:
            continue
        if expected_type is not None and elem_type != expected_type:
            continue
        elements.append(Element(
            type=elem_type,
            id=0,  # REST v1 entries don't include numeric IDs
            name=current.get("shortName", ""),
            long_name=current.get("longName", ""),
            alternate_name=current.get("displayName", ""),
        ))
    return elements


def _parse_iso_datetime(s: str) -> tuple[datetime.date, datetime.time]:
    """Parse an ISO datetime string like ``'2026-03-23T08:00'``."""
    dt = datetime.datetime.fromisoformat(s)
    return dt.date(), dt.time()


def parse_entries_response(
    json_data: dict,
    class_id: int,
    week_start_date: datetime.date | None = None,
) -> WeeklyTimetable:
    """Parse a REST v1 ``/timetable/entries`` response into a :class:`WeeklyTimetable`.

    Parameters
    ----------
    json_data:
        The raw JSON dict returned by the entries endpoint.
    class_id:
        The element ID of the class this data belongs to.
    week_start_date:
        Optional date for the week start; used as metadata on the result.
    """
    days = json_data.get("days", [])
    periods: list[Period] = []

    for day in days:
        for entry in day.get("gridEntries", []):
            # Skip cancelled entries
            status = entry.get("status", "")
            if status == "CANCEL":
                continue

            # Parse duration
            duration = entry.get("duration", {})
            start_str = duration.get("start", "")
            end_str = duration.get("end", "")
            if not start_str or not end_str:
                continue
            entry_date, start_time = _parse_iso_datetime(start_str)
            _, end_time = _parse_iso_datetime(end_str)

            # Parse positions:
            # position1 = subjects, position2 = rooms, position3 = teachers
            # position4 = classes/student groups
            subjects = _parse_position_elements(
                entry.get("position1"), ElementType.SUBJECT,
            )
            rooms = _parse_position_elements(
                entry.get("position2"), ElementType.ROOM,
            )
            teachers = _parse_position_elements(
                entry.get("position3"), ElementType.TEACHER,
            )
            classes = _parse_position_elements(
                entry.get("position4"), ElementType.CLASS,
            )

            # Extract lesson text from texts array
            lesson_text = ""
            lesson_info = entry.get("lessonInfo", "") or ""
            for text_item in entry.get("texts", []):
                if text_item.get("type") == "LESSON_INFO":
                    lesson_text = text_item.get("text", "")

            periods.append(Period(
                date=entry_date,
                start_time=start_time,
                end_time=end_time,
                subjects=tuple(subjects),
                teachers=tuple(teachers),
                rooms=tuple(rooms),
                classes=tuple(classes),
                lesson_id=entry.get("ids", [None])[0] if entry.get("ids") else None,
                lesson_code="",
                cell_state=status,
                lesson_text=lesson_text or lesson_info,
                period_text=entry.get("substitutionText", ""),
            ))

    if week_start_date is None and periods:
        week_start_date = min(p.date for p in periods)
    elif week_start_date is None:
        week_start_date = datetime.date.today()

    return WeeklyTimetable(
        class_id=class_id,
        week_start=week_start_date,
        periods=tuple(periods),
    )


def parse_filter_response(json_data: dict) -> list[ClassGroup]:
    """Parse a REST v1 ``/timetable/filter`` response to extract available class groups.

    Parameters
    ----------
    json_data:
        The raw JSON dict returned by the ``filter`` endpoint.
    """
    classes_raw = json_data.get("classes", [])
    groups: list[ClassGroup] = []
    for item in classes_raw:
        cls = item.get("class", {})
        groups.append(ClassGroup(
            id=cls.get("id", 0),
            name=cls.get("shortName", ""),
            long_name=cls.get("longName", ""),
        ))
    return groups
