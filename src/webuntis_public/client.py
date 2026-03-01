"""HTTP client for the WebUntis public timetable REST API."""

from __future__ import annotations

import datetime
import time as _time

import requests

from .models import ClassGroup, SemesterTimetable, WeeklyTimetable
from .parsing import parse_entries_response, parse_filter_response
from .semester import iter_mondays


class WebUntisError(Exception):
    """Raised when the WebUntis API returns an error."""


class WebUntisPublicClient:
    """Client for the WebUntis public (anonymous) timetable REST API.

    Uses the ``/api/rest/view/v1/timetable/`` endpoints with the
    ``anonymous-school`` header for unauthenticated access.

    Parameters
    ----------
    server:
        Hostname of the WebUntis instance, e.g. ``"hs-reutlingen.webuntis.com"``.
    school:
        School identifier used in the ``anonymous-school`` HTTP header.
        Required for anonymous access (e.g. ``"hs-reutlingen"``).
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
        self._session.headers.update({"User-Agent": "webuntis-public/0.2.0"})
        if school:
            self._session.headers["anonymous-school"] = school
        self._base_url = f"https://{server}/WebUntis/api/rest/view/v1/timetable"

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
        url = f"{self._base_url}/filter"
        data = self._get(url, params={"resourceType": "CLASS"})
        return parse_filter_response(data)

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
            Any date within the desired week.  Accepts a :class:`datetime.date`
            or an ISO-format string.
        """
        if isinstance(date, datetime.date):
            date_str = date.strftime("%Y-%m-%d")
        else:
            date_str = date

        # Compute Monday and Friday of the week
        if isinstance(date, str):
            ref = datetime.date.fromisoformat(date_str)
        else:
            ref = date
        monday = ref - datetime.timedelta(days=ref.weekday())
        saturday = monday + datetime.timedelta(days=5)

        url = f"{self._base_url}/entries"
        params = {
            "start": monday.strftime("%Y-%m-%d"),
            "end": saturday.strftime("%Y-%m-%d"),
            "format": "2",
            "resourceType": "CLASS",
            "resources": str(class_id),
            "timetableType": "STANDARD",
            "layout": "START_TIME",
        }
        raw = self._get(url, params)
        return parse_entries_response(raw, class_id, week_start_date=monday)

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
            Date range (inclusive) -- every Monday in between is fetched.
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