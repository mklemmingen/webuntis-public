"""Parsing helpers for WebUntis public API JSON responses."""

from __future__ import annotations

from .models import ClassGroup, Element, ElementType, Period, WeeklyTimetable
from .semester import parse_date, parse_time


def _build_element_lookup(elements: list[dict]) -> dict[tuple[int, int], dict]:
    """Build a ``{(type, id): raw_element}`` lookup from the elements array."""
    return {(e["type"], e["id"]): e for e in elements}


def _resolve_element(ref: dict, lookup: dict[tuple[int, int], dict]) -> Element:
    """Resolve a single element reference against the lookup table."""
    key = (ref["type"], ref["id"])
    info = lookup.get(key, {})
    return Element(
        type=ElementType(ref["type"]),
        id=ref["id"],
        name=info.get("name", f"id:{ref['id']}"),
        long_name=info.get("longName", ""),
        alternate_name=info.get("alternatename", ""),
    )


def parse_weekly_response(
    json_data: dict,
    class_id: int,
    week_start_date: object | None = None,
) -> WeeklyTimetable:
    """Parse a raw weekly timetable JSON response into a :class:`WeeklyTimetable`.

    Parameters
    ----------
    json_data:
        The raw JSON dict returned by the weekly timetable endpoint.
    class_id:
        The element ID of the class this data belongs to.
    week_start_date:
        Optional date for the week start; used as metadata on the result.
    """
    result = json_data.get("data", {}).get("result", {}).get("data", {})
    periods_raw = result.get("elementPeriods", {}).get(str(class_id), [])
    elements_list = result.get("elements", [])

    lookup = _build_element_lookup(elements_list)

    periods: list[Period] = []
    for p in periods_raw:
        if p.get("cellState") == "CANCEL":
            continue

        subjects: list[Element] = []
        teachers: list[Element] = []
        rooms: list[Element] = []
        classes: list[Element] = []

        for ref in p.get("elements", []):
            elem = _resolve_element(ref, lookup)
            if elem.type == ElementType.SUBJECT:
                subjects.append(elem)
            elif elem.type == ElementType.TEACHER:
                teachers.append(elem)
            elif elem.type == ElementType.ROOM:
                rooms.append(elem)
            elif elem.type == ElementType.CLASS:
                classes.append(elem)

        periods.append(Period(
            date=parse_date(p["date"]),
            start_time=parse_time(p["startTime"]),
            end_time=parse_time(p["endTime"]),
            subjects=tuple(subjects),
            teachers=tuple(teachers),
            rooms=tuple(rooms),
            classes=tuple(classes),
            lesson_id=p.get("lessonId"),
            lesson_code=p.get("lessonCode", ""),
            cell_state=p.get("cellState", ""),
            lesson_text=p.get("lessonText", ""),
            period_text=p.get("periodText", ""),
        ))

    import datetime
    if week_start_date is None and periods:
        week_start_date = min(p.date for p in periods)
    elif week_start_date is None:
        week_start_date = datetime.date.today()

    return WeeklyTimetable(
        class_id=class_id,
        week_start=week_start_date,  # type: ignore[arg-type]
        periods=tuple(periods),
    )


def parse_pageconfig(json_data: dict) -> list[ClassGroup]:
    """Parse the page configuration response to extract available class groups.

    Parameters
    ----------
    json_data:
        The raw JSON dict returned by the ``pageConfig`` endpoint.
    """
    elements = (
        json_data
        .get("data", {})
        .get("elements", json_data.get("elements", []))
    )
    groups: list[ClassGroup] = []
    for e in elements:
        if e.get("type", 0) == ElementType.CLASS:
            groups.append(ClassGroup(
                id=e["id"],
                name=e.get("name", f"id:{e['id']}"),
                long_name=e.get("longName", ""),
            ))
    return groups
