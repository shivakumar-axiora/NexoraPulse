# NexoraPulse Backend

FastAPI + PostgreSQL + SQLAlchemy backend for the NexoraPulse survey platform.

## Prerequisites
- **Python**: 3.11+ (Recommended: `python3`)
- **Pip**: 23.0+ (Recommended: `python3 -m pip`)
- **PostgreSQL**: Running locally or via Docker
- **Docker**: Optional (for running the database)

## Quick Start

### 1. Start the database
If you have Docker installed, you can start the database using Docker Compose:
```bash
docker-compose up -d
```
This will start a PostgreSQL instance with the credentials configured in `docker-compose.yml`.

**Verify it's running:**
```bash
docker ps
```
You should see `nexpulse_db` in the list.

### 2. Configure environment

**On macOS/Linux:**
```bash
cp .env.example .env
```

**On Windows:**
```bash
cp .env.example .env
```

# Edit .env and set your DATABASE_URL and SECRET_KEY

### 3. Create & activate a virtual environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*Note: If `python` doesn't work, try `python3`. If PowerShell blocks scripts, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.*

### 4. Install dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 5. Run the server
The application will **automatically create the database, auto-generate migrations (in dev), and apply tables** on startup.
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Database Migrations (Automatic)
The project is configured to handle migrations automatically, similar to Hibernate/Liquibase:
- **On Startup**: The app checks if your `db/models.py` matches the database schema.
- **Auto-Generation**: If you are in `ENVIRONMENT=development` and make changes to models, a new migration script is automatically created in `migrations/versions/`.
- **Auto-Application**: All pending migrations are applied to the database before the server starts.

You no longer need to manually run `alembic` commands for basic development.

## Troubleshooting

### Error: `externally-managed-environment`
This occurs on macOS/Linux when trying to install packages system-wide.
**Fix:** Always ensure you have **activated** your virtual environment (Step 3) before running `pip install`.

### Error: `failed-wheel-build-for-install` (e.g., pydantic-core)
This usually means your Python version is too new for the pinned dependency versions, and your system lacks the tools to build them from source.
**Fix:** We have updated `requirements.txt` to allow newer versions of Pydantic. If you still face issues, ensure your `pip` is up to date: `python3 -m pip install --upgrade pip`.

### Error: `OperationalError` or `connection failed`
If the app fails to start with a database connection error:
1. Ensure Docker is running and the database container is up (`docker ps`).
2. If using Docker on Mac/Windows, sometimes `127.0.0.1` is preferred over `localhost`. We use `127.0.0.1` by default.
3. Check container logs: `docker logs nexpulse_db` to see if the database is failing to start.
4. If you see "server closed the connection unexpectedly", the database might still be initializing. The app will retry, but you can also try restarting the container: `docker-compose restart db`.

The API will be available at **http://127.0.0.1:8000**
Interactive docs: **http://127.0.0.1:8000/docs**

## Project Structure

```
backend/
├── app/
│   └── main.py          ← FastAPI app, CORS, router registration
├── db/
│   ├── database.py      ← SQLAlchemy engine + session factory
│   └── models.py        ← All ORM models (Tenant, UserProfile, Survey, …)
├── routes/
│   ├── auth.py          ← POST /auth/register, /auth/login, GET /auth/me
│   ├── users.py         ← /users/* (invite, role, status, delete)
│   ├── tenants.py       ← PATCH /tenants/me
│   ├── surveys.py       ← /surveys/* full CRUD + questions
│   ├── responses.py     ← /responses/* (create, auto-save, submit)
│   ├── feedback.py      ← /feedback/*
│   ├── dashboard.py     ← /dashboard/stats, /dashboard/recent
│   └── utils.py         ← /utils/slug/check
├── schemas.py           ← All Pydantic v2 request/response models
├── auth_utils.py                ← JWT encode/decode, password hashing
├── dependencies.py      ← get_db, get_current_user FastAPI dependencies
├── .env                 ← Local environment config (not committed)
├── .env.example         ← Template
└── requirements.txt
```

## API Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | — | Create org + super_admin |
| POST | /auth/login | — | Login, returns JWT |
| GET | /auth/me | ✓ | Current user + tenant |
| PATCH | /auth/me/profile | ✓ | Update name |
| PATCH | /auth/me/password | ✓ | Change password |
| GET | /users/ | ✓ | List team members |
| POST | /users/invite | ✓ | Invite user |
| PATCH | /users/{id}/role | ✓ | Change role |
| DELETE | /users/{id} | ✓ | Delete user |
| GET | /tenants/me | ✓ | Get org settings |
| PATCH | /tenants/me | ✓ | Update org settings |
| GET | /surveys/ | ✓ | List surveys |
| POST | /surveys/ | ✓ | Create survey |
| GET | /surveys/{id} | ✓ | Get survey |
| PATCH | /surveys/{id} | ✓ | Update survey |
| DELETE | /surveys/{id} | ✓ | Delete survey |
| GET | /surveys/slug/{slug} | — | Public: fetch by slug |
| PUT | /surveys/{id}/questions | ✓ | Bulk replace questions |
| POST | /surveys/{id}/duplicate | ✓ | Duplicate survey |
| POST | /responses/ | — | Start response session |
| POST | /responses/{id}/answers | — | Auto-save answers |
| POST | /responses/{id}/submit | — | Submit response |
| POST | /feedback/ | — | Submit post-survey feedback |
| GET | /dashboard/stats | ✓ | Summary counts |
| GET | /dashboard/recent | ✓ | Last 6 surveys |
| GET | /utils/slug/check | — | Check slug availability |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql://nexpulseuser:nexpulsepass@127.0.0.1:5432/nexpulsedb | PostgreSQL connection string |
| SECRET_KEY | (required) | JWT signing key — change in production |
| ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | Token lifetime (24 hours) |
