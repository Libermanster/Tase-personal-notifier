# TASE Personal Notifier

## Project Overview
This project is a personal notifier and data tracker for the Tel Aviv Stock Exchange (TASE). It is designed to autonomously fetch, store, and eventually alert on stock market data.

### Core Technologies
- **Language**: Python 3.11
- **Database**: PostgreSQL 15 (running in Docker)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) (a lean wrapper around SQLAlchemy and Pydantic)
- **API Integration**: [tasepy](https://github.com/m-m-m-m/tasepy) and direct `requests` to TASE DataWise API.
- **Containerization**: Docker & Docker Compose

### Architecture
The system consists of a multi-container Docker setup:
1.  **`app`**: The Python application that handles API logic and database interactions.
2.  **`db`**: A PostgreSQL instance for persistent storage.
Data is synced from TASE to Postgres and also exported to a local SQL backup in the `data/` directory for additional durability.

## Building and Running
The project uses a `Makefile` to simplify common operations.

- **Initial Setup**:
  1. Create a `.env` file based on `.env.example` and add your `TASE_API_KEY`.
  2. Run `make build` to build the Docker images.
- **Start Database**: `make up` (starts Postgres in the background).
- **Sync Data**: `make sync` (fetches companies from TASE and populates the database).
- **View Logs**: `make logs`
- **Database Shell**: `make db-shell` (opens `psql` in the database container).
- **Cleanup**: `make clean` (removes containers and volumes).

## Development Conventions
- **Docker First**: All commands should be run within the Docker environment to ensure consistency.
- **Module Execution**: The application should be run as a module using `python -m src.main` (configured in `docker-compose.yml`).
- **Data Persistence**: 
    - Real-time data is stored in the `db` container's volume.
    - A snapshot is exported to `data/tase_backup.sql` after every successful sync.
- **Secrets**: Never commit `.env` or files in the `data/` directory. Use `.env.example` for sharing configuration structure.
- **Coding Style**: Use SQLModel for all database interactions to maintain type safety and ease of future integration with FastAPI.
