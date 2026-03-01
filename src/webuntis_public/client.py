"""HTTP client for the WebUntis public timetable API."""

from __future__ import annotations

import datetime
import time as _time

import requests

from .models import ClassGroup, SemesterTimetable, WeeklyTimetable
from .parsing import parse_pageconfig, parse_weekly_response
from .semester import iter_mondays


class WebUntisError(Exception):
    """Raised when the WebUntis API returns an error."""


class WebUntisPublicClient:
    """Client for the WebUntis public (unauthenticated) timetable API.

    Parameters
    ----------
    server:
        Hostname of the WebUntis instance, e.g. ``"hs-reutlingen.webuntis.com"``.
    school:
        Optional school name for the URL path.  Most public endpoints do not
        require this, but it is kept for forward-compatibility.
    rate_limit:
        Minimum seconds to wait between consecutive HTTP requests.
    """

    def __init__(
        self,
        server: str,
        *,
        school: str | None = None,
        rate_limit: float = 0.3,
    ) -> None:
        self.server = server
        self.school = school
        self._rate_limit = rate_limit
        self._last_request: float = 0.0
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "webuntis-public/0.1.0"})
        self._base_url = f"https://{server}/WebUntis/api/public/timetable/weekly"

    def _get(self, url: str, params: dict | None = None) -> dict:
        """Perform a rate-limited GET request and return JSON."""
        elapsed = _time.monotonic() - self._last_request
        if elapsed < self._rate_limit:
            _time.sleep(self._rate_limit - elapsed)
        resp = self._session.get(url, params=params)
        self._last_request = _time.monotonic()
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Class listing
    # ------------------------------------------------------------------

    def list_classes(self) -> list[ClassGroup]:
        """Return all class groups available on this WebUntis server."""
        url = f"{self._base_url}/pageConfig"
        data = self._get(url)
        return parse_pageconfig(data)

    def find_classes(self, pattern: str) -> list[ClassGroup]:
        """Return class groups whose name contains *pattern* (case-insensitive)."""
        pattern_lower = pattern.lower()
        return [c for c in self.list_classes() if pattern_lower in c.name.lower()]

    # ------------------------------------------------------------------
    # Timetable fetching
    # ------------------------------------------------------------------

    def fetch_week(
        self,
        class_id: int,
        date: datetime.date | str,
    ) -> WeeklyTimetable:
        """Fetch one week of timetable data for the given class.

        Parameters
        ----------
        class_id:
            The numeric element ID of the class.
        date:
            Any date within the desired week (the API rounds to the enclosing
            Monday–Friday range).  Accepts a :class:`datetime.date` or an
            ISO-format string.
        """
        if isinstance(date, datetime.date):
            date_str = date.strftime("%Y-%m-%d")
        else:
            date_str = date
        url = f"{self._base_url}/data"
        params = {
            "elementType": 1,
            "elementId": class_id,
            "date": date_str,
            "formatId": 1,
        }
        raw = self._get(url, params)
        week_date = (
            datetime.date.fromisoformat(date_str)
            if isinstance(date, str) else date
        )
        return parse_weekly_response(raw, class_id, week_start_date=week_date)

    def fetch_semester(
        self,
        class_id: int,
        start: datetime.date,
        end: datetime.date,
        *,
        on_error: str = "warn",
    ) -> SemesterTimetable:
        """Fetch timetable data for every week in a date range.

        Parameters
        ----------
        class_id:
            The numeric element ID of the class.
        start, end:
            Date range (inclusive) — every Monday in between is fetched.
        on_error:
            ``"warn"`` (default) prints errors and continues,
            ``"raise"`` re-raises the first exception,
            ``"skip"`` silently skips failed weeks.
        """
        weeks: list[WeeklyTimetable] = []
        for monday in iter_mondays(start, end):
            try:
                week = self.fetch_week(class_id, monday)
                weeks.append(week)
            except Exception as exc:
                if on_error == "raise":
                    raise
                if on_error == "warn":
                    import sys
                    print(
                        f"Warning: failed to fetch week {monday}: {exc}",
                        file=sys.stderr,
                    )
        return SemesterTimetable(
            class_id=class_id,
            start=start,
            end=end,
            weeks=tuple(weeks),
        )
