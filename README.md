# Participium

A citizen-participation web platform for the City of Turin. Citizens report urban issues (potholes, broken streetlights, waste, architectural barriers) on a city map, and municipal operators manage each report through a tracked lifecycle until it is resolved.

Developed by a team of 4 students for the Software Engineering course at Politecnico di Torino.

<!-- Add 1–2 screenshots of the running app here, e.g. the map view and a report detail page -->

## Features

- **Geo-located reports** on an OpenStreetMap map, with title, description, category, 1–3 photos and an optional anonymous mode
- **Report lifecycle:** Pending Approval → Assigned → In Progress → Suspended / Rejected / Resolved, with a mandatory motivation for rejections
- **Public consultation:** map view, filterable and sortable table, report details and CSV export
- **Notifications and messaging:** in-platform and email updates for reporters and followers, direct messages between citizens and operators
- **Statistics:** public statistics by category and over time, private breakdowns for administrators
- **Roles:** visitor, citizen, municipal operator, administrator

## Tech stack

| Layer | Technologies |
| --- | --- |
| Backend | Python, Flask, REST API, OpenAPI (Swagger), SQLAlchemy |
| Frontend | React, TypeScript, Vite, React Router, Leaflet |
| Database | SQLite (default), MySQL 8 (via Docker) |
| Testing | pytest, pytest-cov (unit, integration, black-box, white-box), Selenium end-to-end tests |
| Deployment | Docker, Docker Compose |

## Architecture

The backend follows a layered architecture, so each layer can be tested in isolation:

```text
Routes → Controllers → Services → Repositories → SQLAlchemy models
```

- **Routes** adapt HTTP input and output only
- **Controllers** orchestrate use cases
- **Services** hold the business rules (status transitions, notifications, statistics)
- **Repositories** are the only layer that queries the database

Infrastructure is configuration-driven: switching from SQLite to MySQL only requires environment variables and Docker Compose, with no code changes.

## Getting started

### With Docker (frontend + backend + MySQL)

From the repository root:

```bash
docker compose -f docker/docker-compose.yml up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:5050
- Swagger UI: http://localhost:5050/apidocs/

### Backend only (SQLite)

```bash
cd src/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python wsgi.py
```

See [`src/backend/README.md`](src/backend/README.md) for configuration, seed data and Windows instructions.

### Demo accounts

With demo data enabled (the default), the backend creates:

| Role | Email | Password |
| --- | --- | --- |
| Citizen | citizen@example.com | Citizen123! |
| Operator | operator@example.com | Operator123! |
| Admin | admin@example.com | Admin123! |

## Tests

From `src/backend`:

```bash
python -m pytest --cov=participium --cov-config=.coveragerc --cov-report=term-missing
```

Test suites are split into `unit`, `integration`, `blackbox`, `whitebox` and `e2e`. Coverage targets controllers, routes, services, repositories and core logic.

## Documentation

- [System description (EN)](doc/Participium.md) · [Italiano](doc/Participium_it.md)
- [Requirements and official documentation](doc/OfficialDocumentation.md)
- [Implementation specification](doc/Participium_Implementation_Spec.md)
- [Black-box](doc/deliverable/05_BlackBoxReport.md) and [white-box](doc/deliverable/06_WhiteBoxReport.md) test reports
