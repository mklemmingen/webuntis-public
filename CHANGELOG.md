# Changelog

## 0.2.0 (2026-03-01)

### Breaking Changes

- Switched from the deprecated `/api/public/timetable/weekly/` endpoints to the
  REST v1 API (`/api/rest/view/v1/timetable/filter` and `/entries`).
- `WebUntisPublicClient` constructor now accepts a `school` keyword argument
  used for the `anonymous-school` HTTP header (required for anonymous access).

### Fixed

- `list_classes()` no longer returns HTTP 500 on servers that disabled the
  legacy `pageConfig` endpoint.
- Class names are no longer masked as `"?"` in timetable responses.

### Added

- `anonymous-school` header support for unauthenticated public access.
- New response parsing for REST v1 format (grid entries with position-based
  element layout).

## 0.1.0 (2025-12-01)

- Initial release with `pageConfig` and weekly `data` endpoint support.
