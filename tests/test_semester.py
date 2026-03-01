"""Tests for semester date/time utilities."""

import datetime

from webuntis_public.semester import (
    format_date,
    format_time,
    iter_mondays,
    parse_date,
    parse_time,
    weekday_name,
)


class TestIterMondays:
    def test_basic_range(self):
        start = datetime.date(2026, 3, 2)  # Monday
        end = datetime.date(2026, 3, 22)
        mondays = list(iter_mondays(start, end))
        assert len(mondays) == 3
        assert mondays[0] == datetime.date(2026, 3, 2)
        assert mondays[1] == datetime.date(2026, 3, 9)
        assert mondays[2] == datetime.date(2026, 3, 16)

    def test_start_not_monday(self):
        start = datetime.date(2026, 3, 4)  # Wednesday
        end = datetime.date(2026, 3, 16)
        mondays = list(iter_mondays(start, end))
        assert len(mondays) == 2
        assert mondays[0] == datetime.date(2026, 3, 9)
        assert mondays[1] == datetime.date(2026, 3, 16)

    def test_empty_range(self):
        start = datetime.date(2026, 3, 10)
        end = datetime.date(2026, 3, 8)
        assert list(iter_mondays(start, end)) == []

    def test_single_monday(self):
        monday = datetime.date(2026, 3, 2)
        assert list(iter_mondays(monday, monday)) == [monday]


class TestParseDate:
    def test_basic(self):
        assert parse_date(20260302) == datetime.date(2026, 3, 2)

    def test_december(self):
        assert parse_date(20251231) == datetime.date(2025, 12, 31)


class TestParseTime:
    def test_morning(self):
        assert parse_time(800) == datetime.time(8, 0)

    def test_afternoon(self):
        assert parse_time(1345) == datetime.time(13, 45)

    def test_midnight(self):
        assert parse_time(0) == datetime.time(0, 0)


class TestFormatDate:
    def test_basic(self):
        assert format_date(20260302) == "2026-03-02"


class TestFormatTime:
    def test_padded(self):
        assert format_time(800) == "08:00"

    def test_afternoon(self):
        assert format_time(1345) == "13:45"


class TestWeekdayName:
    def test_monday(self):
        assert weekday_name(20260302) == "Monday"

    def test_friday(self):
        assert weekday_name(20260306) == "Friday"
