"""Tests for the WebUntisPublicClient (using mocked HTTP)."""

import datetime
from unittest.mock import patch

from webuntis_public.client import WebUntisPublicClient


MOCK_FILTER = {
    "resourceType": "CLASS",
    "classes": [
        {
            "class": {"id": 100, "shortName": "3MKIB4", "longName": "MKIB Semester 4"},
            "classTeacher1": None,
            "classTeacher2": None,
            "department": None,
        },
        {
            "class": {"id": 101, "shortName": "3WIB2", "longName": "WIB Semester 2"},
            "classTeacher1": None,
            "classTeacher2": None,
            "department": None,
        },
    ],
}

MOCK_ENTRIES = {
    "format": 2,
    "days": [
        {
            "date": "2026-03-02",
            "resourceType": "CLASS",
            "resource": {"id": 100, "shortName": "3MKIB4"},
            "status": "REGULAR",
            "dayEntries": [],
            "gridEntries": [
                {
                    "ids": [1],
                    "duration": {
                        "start": "2026-03-02T08:00",
                        "end": "2026-03-02T09:30",
                    },
                    "type": "NORMAL_TEACHING_PERIOD",
                    "status": "REGULAR",
                    "position1": [
                        {
                            "current": {
                                "type": "SUBJECT",
                                "shortName": "MATH",
                                "longName": "Mathematics",
                                "displayName": "Mathematics",
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
                }
            ],
            "backEntries": [],
        }
    ],
    "errors": [],
}


class TestListClasses:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_FILTER)
    def test_returns_all_classes(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        classes = client.list_classes()
        assert len(classes) == 2
        assert classes[0].name == "3MKIB4"


class TestFindClasses:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_FILTER)
    def test_filter_by_name(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        results = client.find_classes("MKIB")
        assert len(results) == 1
        assert results[0].name == "3MKIB4"

    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_FILTER)
    def test_case_insensitive(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        results = client.find_classes("mkib")
        assert len(results) == 1


class TestAnonymousSchoolHeader:
    def test_header_set_when_school_provided(self):
        client = WebUntisPublicClient(
            "example.webuntis.com", school="test-school", rate_limit=0,
        )
        assert client._session.headers.get("anonymous-school") == "test-school"

    def test_header_absent_when_no_school(self):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        assert "anonymous-school" not in client._session.headers


class TestFetchWeek:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_ENTRIES)
    def test_returns_weekly_timetable(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        week = client.fetch_week(100, datetime.date(2026, 3, 2))
        assert week.class_id == 100
        assert len(week.periods) == 1
        assert week.periods[0].subjects[0].name == "MATH"

    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_ENTRIES)
    def test_accepts_string_date(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        week = client.fetch_week(100, "2026-03-02")
        assert len(week.periods) == 1

    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_ENTRIES)
    def test_computes_monday(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        # Wednesday 2026-03-04 should round to Monday 2026-03-02
        client.fetch_week(100, datetime.date(2026, 3, 4))
        call_params = mock_get.call_args
        url = call_params[0][0]
        params = call_params[1].get("params", call_params[0][1] if len(call_params[0]) > 1 else {})
        assert params["start"] == "2026-03-02"


class TestFetchSemester:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_ENTRIES)
    def test_fetches_multiple_weeks(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        sem = client.fetch_semester(
            100,
            datetime.date(2026, 3, 2),
            datetime.date(2026, 3, 15),
        )
        assert sem.class_id == 100
        assert len(sem.weeks) == 2
        assert len(sem.periods) == 2  # 1 period per mocked week
