# Serpent Spectator Arena 🐍

Real-time multiplayer snake spectator arena with live WebSocket streaming, leaderboard tracking, and authentication.

## Architecture

The system is containerized with **Docker Compose**. The frontend, backend, and
reverse proxy run together in one application container; PostgreSQL runs
separately with a persistent data volume:

```
     ┌───────────────────────┐       ┌──────────────────┐
     │      App (Port 80)    │       │   PostgreSQL 16  │
     │ Nginx + frontend SSR  │──────▶│    (Port 5432)   │
     │  + FastAPI/WebSocket  │       └──────────────────┘
     └───────────────────────┘
```

1. **App (`app`)**: One container built from the repository root. Supervisor runs Nginx, the TanStack Start SSR server, and FastAPI together. Nginx listens on ports `80` and `8080`.
   - Serves TanStack Start SSR frontend routes (`/`, `/watch`, `/login`, etc.)
   - Proxies backend REST endpoints (`/auth/*`, `/leaderboard`, `/scores`, `/live`, `/docs`)
   - Upgrades `/ws/` connections to FastAPI WebSocket with zero CORS friction
2. **Database (`db`)**: PostgreSQL 16 Alpine with healthcheck and persistent volume storage (`postgres_data`).

---

## Quick Start with Docker Compose

Ensure Docker and Docker Compose are installed, then run:

```bash
docker compose up --build
```
*(or use `make docker-up`)*

### Service URLs

- **Web Application**: [http://localhost](http://localhost) (or [http://localhost:8080](http://localhost:8080))
- **FastAPI Interactive Docs**: [http://localhost/docs](http://localhost/docs)
- **PostgreSQL**: `localhost:5432` (`user: serpent`, `password: serpent_secret`, `database: serpent_arena`)

## Deploy to Render (Free Demo)

The root [render.yaml](./render.yaml) Blueprint creates the Docker web service
and a managed PostgreSQL database in Frankfurt. To deploy:

1. Push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), choose **New >
   Blueprint** and connect the repository.
3. Review the `serpent-spectator-arena` web service and
   `serpent-spectator-db` database, then apply the Blueprint.
4. Wait for the first build and deploy. Open the service's `onrender.com` URL
   when Render reports it as live.

This is suitable for a demo, not production: Render's free web service spins
down after 15 minutes without inbound traffic, so the next visit may wait about
a minute. The free PostgreSQL database expires 30 days after creation. Upgrade
the database before it expires to retain its data; upgrade the web service to
avoid spin-downs. The web service filesystem is ephemeral, so application data
must stay in PostgreSQL.

### Demo Accounts

The database is automatically seeded on startup with the following accounts:

| Username | Email | Password |
|---|---|---|
| `neonviper` | `neonviper@snake.dev` | `demo123` |
| `pixelpython` | `pixelpython@snake.dev` | `demo123` |
| `cobraclaw` | `cobraclaw@snake.dev` | `demo123` |
| `slitherbot` | `slitherbot@snake.dev` | `demo123` |
| `phantomsnek` | `phantomsnek@snake.dev` | `demo123` |

---

## Useful Makefile Commands

```bash
# Docker Compose commands
make docker-up        # Build & launch the app container and PostgreSQL
make docker-down      # Stop all containers
make docker-logs      # Follow logs from all running containers
make docker-clean     # Stop containers and purge persistent database volume

# Local development (without Docker)
make dev              # Run backend and frontend concurrently
make test-backend-all # Run unit and integration tests using uv
```
