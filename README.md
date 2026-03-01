# webuntis-public

Python client for the [WebUntis](https://www.untis.at/) **public** timetable REST API.
No authentication or API key required.

## Installation

```bash
pip install webuntis-public
```

## Quick Start

```python
from webuntis_public import WebUntisPublicClient

# Connect to any WebUntis school
client = WebUntisPublicClient("hs-reutlingen.webuntis.com")

# List all available classes
classes = client.list_classes()
for c in classes[:5]:
    print(f"{c.id}: {c.name} ({c.long_name})")

# Search for classes by name
mkib = client.find_classes("MKIB")

# Fetch a single week
from datetime import date
week = client.fetch_week(class_id=21893, date=date(2026, 3, 2))
for period in week.periods:
    subj = ", ".join(s.name for s in period.subjects)
    print(f"  {period.date} {period.start_time}-{period.end_time}: {subj}")

# Fetch an entire semester
semester = client.fetch_semester(
    class_id=21893,
    start=date(2026, 3, 2),
    end=date(2026, 7, 5),
)
print(f"Total periods: {len(semester.periods)}")
```

## API Reference

### `WebUntisPublicClient(server, *, school=None, rate_limit=0.3)`

Create a client for the given WebUntis server hostname.

**Methods:**

| Method | Description |
|--------|-------------|
| `list_classes()` | Returns all `ClassGroup` entries on the server |
| `find_classes(pattern)` | Case-insensitive search for class groups by name |
| `fetch_week(class_id, date)` | Fetch one week of timetable data |
| `fetch_semester(class_id, start, end)` | Fetch all weeks in a date range |

### Data Models

All models are frozen dataclasses:

- **`ClassGroup`** — `id`, `name`, `long_name`
- **`Period`** — `date`, `start_time`, `end_time`, `subjects`, `teachers`, `rooms`, `classes`, `lesson_id`, ...
- **`Element`** — `type` (`ElementType`), `id`, `name`, `long_name`, `alternate_name`
- **`WeeklyTimetable`** — `class_id`, `week_start`, `periods`
- **`SemesterTimetable`** — `class_id`, `start`, `end`, `weeks`, `periods` (property)

### Utility Functions

- `parse_date(int) -> date` — e.g. `20260302` -> `date(2026, 3, 2)`
- `parse_time(int) -> time` — e.g. `800` -> `time(8, 0)`
- `format_date(int) -> str` — e.g. `20260302` -> `"2026-03-02"`
- `format_time(int) -> str` — e.g. `800` -> `"08:00"`
- `iter_mondays(start, end)` — yield all Mondays in range

## License

Apache-2.0
