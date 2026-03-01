"""Tests for the WebUntisPublicClient (using mocked HTTP)."""

import datetime
from unittest.mock import MagicMock, patch

from webuntis_public.client import WebUntisPublicClient


MOCK_PAGECONFIG = {
    "data": {
        "elements": [
            {"type": 1, "id": 100, "name": "3MKIB4", "longName": "MKIB Semester 4"},
            {"type": 1, "id": 101, "name": "3WIB2", "longName": "WIB Semester 2"},
        ]
    }
}

MOCK_WEEKLY = {
    "data": {
        "result": {
            "data": {
                "elementPeriods": {
                    "100": [
                        {
                            "date": 20260302,
                            "startTime": 800,
                            "endTime": 930,
                            "elements": [{"type": 3, "id": 50}],
                            "lessonId": 1,
                            "cellState": "STANDARD",
                        }
                    ]
                },
                "elements": [
                    {"type": 3, "id": 50, "name": "MATH", "longName": "Mathematics"},
                ],
            }
        }
    }
}


class TestListClasses:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_PAGECONFIG)
    def test_returns_all_classes(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        classes = client.list_classes()
        assert len(classes) == 2
        assert classes[0].name == "3MKIB4"


class TestFindClasses:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_PAGECONFIG)
    def test_filter_by_name(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        results = client.find_classes("MKIB")
        assert len(results) == 1
        assert results[0].name == "3MKIB4"

    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_PAGECONFIG)
    def test_case_insensitive(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        results = client.find_classes("mkib")
        assert len(results) == 1


class TestFetchWeek:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_WEEKLY)
    def test_returns_weekly_timetable(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        week = client.fetch_week(100, datetime.date(2026, 3, 2))
        assert week.class_id == 100
        assert len(week.periods) == 1
        assert week.periods[0].subjects[0].name == "MATH"

    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_WEEKLY)
    def test_accepts_string_date(self, mock_get):
        client = WebUntisPublicClient("example.webuntis.com", rate_limit=0)
        week = client.fetch_week(100, "2026-03-02")
        assert len(week.periods) == 1


class TestFetchSemester:
    @patch.object(WebUntisPublicClient, "_get", return_value=MOCK_WEEKLY)
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
