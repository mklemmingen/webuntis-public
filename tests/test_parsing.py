"""Tests for JSON parsing logic."""

import datetime

from webuntis_public.models import ElementType
from webuntis_public.parsing import parse_pageconfig, parse_weekly_response


# -- Fixtures --

WEEKLY_RESPONSE = {
    "data": {
        "result": {
            "data": {
                "elementPeriods": {
                    "100": [
                        {
                            "date": 20260302,
                            "startTime": 800,
                            "endTime": 930,
                            "elements": [
                                {"type": 3, "id": 50},
                                {"type": 2, "id": 10},
                                {"type": 4, "id": 20},
                                {"type": 1, "id": 100},
                            ],
                            "lessonId": 999,
                            "lessonCode": "",
                            "cellState": "STANDARD",
                            "lessonText": "",
                            "periodText": "",
                        },
                        {
                            "date": 20260303,
                            "startTime": 1000,
                            "endTime": 1130,
                            "elements": [
                                {"type": 3, "id": 51},
                            ],
                            "cellState": "CANCEL",
                            "lessonId": 1000,
                        },
                    ]
                },
                "elements": [
                    {"type": 3, "id": 50, "name": "MATH", "longName": "Mathematics", "alternatename": "MA"},
                    {"type": 3, "id": 51, "name": "PHYS", "longName": "Physics"},
                    {"type": 2, "id": 10, "name": "Mueller", "longName": "Prof. Mueller"},
                    {"type": 4, "id": 20, "name": "A101", "longName": "Room A101"},
                    {"type": 1, "id": 100, "name": "3MKIB4", "longName": "MKIB Semester 4"},
                ],
            }
        }
    }
}

PAGECONFIG_RESPONSE = {
    "data": {
        "elements": [
            {"type": 1, "id": 100, "name": "3MKIB4", "longName": "MKIB Semester 4"},
            {"type": 1, "id": 101, "name": "3MKIB6", "longName": "MKIB Semester 6"},
            {"type": 2, "id": 10, "name": "Mueller", "longName": "Prof. Mueller"},
        ]
    }
}


class TestParseWeeklyResponse:
    def test_returns_weekly_timetable(self):
        wt = parse_weekly_response(WEEKLY_RESPONSE, class_id=100)
        assert wt.class_id == 100

    def test_filters_cancelled(self):
        wt = parse_weekly_response(WEEKLY_RESPONSE, class_id=100)
        assert len(wt.periods) == 1

    def test_resolves_subject(self):
        wt = parse_weekly_response(WEEKLY_RESPONSE, class_id=100)
        period = wt.periods[0]
        assert len(period.subjects) == 1
        subj = period.subjects[0]
        assert subj.name == "MATH"
        assert subj.long_name == "Mathematics"
        assert subj.alternate_name == "MA"
        assert subj.type == ElementType.SUBJECT

    def test_resolves_teacher(self):
        wt = parse_weekly_response(WEEKLY_RESPONSE, class_id=100)
        period = wt.periods[0]
        assert len(period.teachers) == 1
        assert period.teachers[0].long_name == "Prof. Mueller"

    def test_resolves_room(self):
        wt = parse_weekly_response(WEEKLY_RESPONSE, class_id=100)
        period = wt.periods[0]
        assert len(period.rooms) == 1
        assert period.rooms[0].name == "A101"

    def test_date_and_time(self):
        wt = parse_weekly_response(WEEKLY_RESPONSE, class_id=100)
        period = wt.periods[0]
        assert period.date == datetime.date(2026, 3, 2)
        assert period.start_time == datetime.time(8, 0)
        assert period.end_time == datetime.time(9, 30)

    def test_empty_response(self):
        wt = parse_weekly_response({"data": {"result": {"data": {}}}}, class_id=100)
        assert len(wt.periods) == 0


class TestParsePageconfig:
    def test_returns_class_groups_only(self):
        groups = parse_pageconfig(PAGECONFIG_RESPONSE)
        assert len(groups) == 2

    def test_group_fields(self):
        groups = parse_pageconfig(PAGECONFIG_RESPONSE)
        assert groups[0].id == 100
        assert groups[0].name == "3MKIB4"
        assert groups[0].long_name == "MKIB Semester 4"

    def test_empty_response(self):
        groups = parse_pageconfig({"data": {"elements": []}})
        assert groups == []
