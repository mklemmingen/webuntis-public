"""Tests for WebUntis REST v1 response parsing."""

import datetime

from webuntis_public.models import ElementType
from webuntis_public.parsing import parse_entries_response, parse_filter_response


# -- Fixtures --

FILTER_RESPONSE = {
    "resourceType": "CLASS",
    "classes": [
        {
            "class": {
                "id": 21899,
                "shortName": "3MKIB6",
                "longName": "Medien- und Kommunikationsinformatik",
                "displayName": "3MKIB6",
            },
            "classTeacher1": None,
            "classTeacher2": None,
            "department": {
                "id": 64,
                "shortName": "LS-P",
                "longName": "LS - PRÜFUNG",
                "displayName": "LS - PRÜFUNG",
            },
        },
        {
            "class": {
                "id": 22371,
                "shortName": "1ACB",
                "longName": "Angewandte Chemie, Bachelor",
                "displayName": "1ACB",
            },
            "classTeacher1": None,
            "classTeacher2": None,
            "department": None,
        },
    ],
    "resources": [],
    "rooms": [],
    "subjects": [],
    "students": [],
    "teachers": [],
}

ENTRIES_RESPONSE = {
    "format": 2,
    "days": [
        {
            "date": "2026-03-23",
            "resourceType": "CLASS",
            "resource": {
                "id": 21899,
                "shortName": "3MKIB6",
                "longName": "Medien- und Kommunikationsinformatik",
                "displayName": "",
            },
            "status": "REGULAR",
            "dayEntries": [],
            "gridEntries": [
                {
                    "ids": [4940783],
                    "duration": {
                        "start": "2026-03-23T08:00",
                        "end": "2026-03-23T09:30",
                    },
                    "type": "NORMAL_TEACHING_PERIOD",
                    "status": "REGULAR",
                    "position1": [
                        {
                            "current": {
                                "type": "SUBJECT",
                                "status": "REGULAR",
                                "shortName": "MATH",
                                "longName": "Mathematics",
                                "displayName": "Mathematics",
                            },
                            "removed": None,
                        }
                    ],
                    "position2": [
                        {
                            "current": {
                                "type": "ROOM",
                                "status": "REGULAR",
                                "shortName": "A101",
                                "longName": "Room A101",
                                "displayName": "A101",
                            },
                            "removed": None,
                        }
                    ],
                    "position3": [
                        {
                            "current": {
                                "type": "TEACHER",
                                "status": "REGULAR",
                                "shortName": "Mueller",
                                "longName": "Prof. Mueller",
                                "displayName": "Mueller",
                            },
                            "removed": None,
                        }
                    ],
                    "position4": [
                        {
                            "current": {
                                "type": "CLASS",
                                "status": "REGULAR",
                                "shortName": "3MKIB6",
                                "longName": "MKIB Semester 6",
                                "displayName": "3MKIB6",
                            },
                            "removed": None,
                        }
                    ],
                    "texts": [
                        {"type": "LESSON_INFO", "text": "Extra info"}
                    ],
                    "lessonInfo": "Extra info",
                    "substitutionText": "",
                },
                {
                    "ids": [4940800],
                    "duration": {
                        "start": "2026-03-23T10:00",
                        "end": "2026-03-23T11:30",
                    },
                    "type": "NORMAL_TEACHING_PERIOD",
                    "status": "CANCEL",
                    "position1": [
                        {
                            "current": {
                                "type": "SUBJECT",
                                "status": "REGULAR",
                                "shortName": "PHYS",
                                "longName": "Physics",
                                "displayName": "Physics",
                            },
                            "removed": None,
                        }
                    ],
                    "position2": [],
                    "position3": [],
                    "position4": None,
                    "texts": [],
                    "lessonInfo": "",
                    "substitutionText": "",
                },
            ],
            "backEntries": [],
        },
        {
            "date": "2026-03-24",
            "resourceType": "CLASS",
            "resource": {"id": 21899},
            "status": "NO_DATA",
            "dayEntries": [],
            "gridEntries": [],
            "backEntries": [],
        },
    ],
    "errors": [],
}


class TestParseFilterResponse:
    def test_returns_class_groups(self):
        groups = parse_filter_response(FILTER_RESPONSE)
        assert len(groups) == 2

    def test_group_fields(self):
        groups = parse_filter_response(FILTER_RESPONSE)
        assert groups[0].id == 21899
        assert groups[0].name == "3MKIB6"
        assert groups[0].long_name == "Medien- und Kommunikationsinformatik"

    def test_second_group(self):
        groups = parse_filter_response(FILTER_RESPONSE)
        assert groups[1].id == 22371
        assert groups[1].name == "1ACB"

    def test_empty_response(self):
        groups = parse_filter_response({"classes": []})
        assert groups == []

    def test_missing_classes_key(self):
        groups = parse_filter_response({})
        assert groups == []


class TestParseEntriesResponse:
    def test_returns_weekly_timetable(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        assert wt.class_id == 21899

    def test_filters_cancelled(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        assert len(wt.periods) == 1

    def test_resolves_subject(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        period = wt.periods[0]
        assert len(period.subjects) == 1
        subj = period.subjects[0]
        assert subj.name == "MATH"
        assert subj.long_name == "Mathematics"
        assert subj.type == ElementType.SUBJECT

    def test_resolves_teacher(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        period = wt.periods[0]
        assert len(period.teachers) == 1
        assert period.teachers[0].long_name == "Prof. Mueller"

    def test_resolves_room(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        period = wt.periods[0]
        assert len(period.rooms) == 1
        assert period.rooms[0].name == "A101"

    def test_resolves_class(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        period = wt.periods[0]
        assert len(period.classes) == 1
        assert period.classes[0].name == "3MKIB6"

    def test_date_and_time(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        period = wt.periods[0]
        assert period.date == datetime.date(2026, 3, 23)
        assert period.start_time == datetime.time(8, 0)
        assert period.end_time == datetime.time(9, 30)

    def test_lesson_id(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        assert wt.periods[0].lesson_id == 4940783

    def test_lesson_text(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        assert wt.periods[0].lesson_text == "Extra info"

    def test_empty_response(self):
        wt = parse_entries_response(
            {"format": 2, "days": [], "errors": []}, class_id=100,
        )
        assert len(wt.periods) == 0

    def test_infers_week_start_from_periods(self):
        wt = parse_entries_response(ENTRIES_RESPONSE, class_id=21899)
        assert wt.week_start == datetime.date(2026, 3, 23)

    def test_explicit_week_start(self):
        wt = parse_entries_response(
            ENTRIES_RESPONSE, class_id=21899,
            week_start_date=datetime.date(2026, 3, 22),
        )
        assert wt.week_start == datetime.date(2026, 3, 22)
