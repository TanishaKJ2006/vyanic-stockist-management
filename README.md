# Vyanic Technologies Stockist Management Portal

A responsive stockist operations portal using the required Python/FastAPI, React/Vite, React Router, Axios, MySQL/SQLAlchemy, MongoDB, and JWT stack. The Navy, Ivory, and Champagne Gold application shell remains in place. Stage 3A provides the dashboard, product, stockist, pincode, and audit-log backend APIs; Stage 3B connects the React pages to those protected APIs. No sample business records are seeded.

## Project structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/routes/        # Health, auth, dashboard, product, stockist, and audit APIs
|   |   |-- auth/              # JWT, password security, admin bootstrap
|   |   |-- core/              # Environment-based settings
|   |   |-- db/                # SQLAlchemy sessions and MongoDB access
|   |   |-- models/            # SQLAlchemy ORM models
|   |   |-- schemas/           # Pydantic request/response schemas
|   |   |-- services/          # Business logic and SQL/Mongo audit coordination
|   |   `-- main.py            # FastAPI app, middleware, startup
|   |-- alembic/               # Database migrations
|   |-- tests/                 # Backend tests
|   |-- alembic.ini
|   |-- .env.example
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- components/        # Layout, auth guards, and shared UI
|   |   |-- contexts/          # Authentication state
|   |   |-- pages/             # Auth and portal pages
|   |   |-- services/          # Axios client and session storage
|   |   `-- styles/            # Navy, ivory, and champagne design system
|   |-- .env.example
|   `-- package.json
`-- README.md
```

## Prerequisites

- Python 3.11 or newer
- Node.js 20.19+ or 22.12+, plus npm
- MySQL 8 with the `vyanic_stockist` database
- MongoDB with the existing `audit_logs` collection

The backend starts without a MySQL connection, but database-backed registration and login require valid MySQL credentials and the migration to be applied. On application startup, it attempts to create the MongoDB timestamp index; if MongoDB is unavailable, the API logs a warning and continues.

## MySQL setup

If the database does not already exist, create it from a MySQL administrative session:

```sql
CREATE DATABASE vyanic_stockist
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Use the credentials for your MySQL installation. Do not put real credentials in source files or commit a `.env` file.

## Backend configuration and run

From the project root, create a local environment file only when one does not already exist:

```powershell
if (-not (Test-Path backend/.env)) {
    Copy-Item backend/.env.example backend/.env
}
```

Edit `backend/.env` and set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, and `MYSQL_PASSWORD`. Set `MONGODB_URI` to your MongoDB connection string and keep `MONGODB_DATABASE=vyanic_stockist`. Generate a unique signing key:

```powershell
py -3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated value in `JWT_SECRET`. Set `JWT_ACCESS_TOKEN_MINUTES` to the desired access-token lifetime (the default is 30 minutes). `CORS_ORIGINS` lists the local Vite origins.

Create a virtual environment and install the Python dependencies from the project root:

```powershell
Set-Location .\backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Apply all MySQL schema migrations:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## Administrator Account Creation and Login

Administrator accounts cannot be created through public registration. The portal's registration page creates read-only Viewer accounts; the API retains its documented legacy `stockist` default when an optional role is omitted. Create the administrator through the local bootstrap command below.

After configuring the backend environment, installing backend dependencies, and applying the MySQL migrations, run these commands from the project root. The MySQL server must be available and the configured backend database user must have access to `vyanic_stockist`:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m app.auth.bootstrap_admin
```

The command interactively asks for the administrator name, email address, password, and password confirmation. The password must be 12â€“128 characters. Password entry is private through Python's `getpass`; it is stored as an Argon2 hash.

This bootstrap process can create only one administrator. It checks for an existing administrator after collecting and validating the entered values. If one already exists, the command exits without creating another account or resetting the existing password. In that case, use the existing administrator's email and password.

Start the frontend in a separate PowerShell window from the project root (create its local environment file if needed, then install and start it):

```powershell
Set-Location .\frontend
if (-not (Test-Path .\.env)) {
    Copy-Item .\.env.example .\.env
}
npm ci
npm run dev
```

With the backend and frontend running, open `http://127.0.0.1:5173/login` and sign in using the email address and password entered during administrator bootstrap. If an administrator already existed, use that account's existing credentials instead.

Start the API from the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API health: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Authentication endpoints: `POST /auth/register`, `POST /auth/login`, and protected `GET /auth/me`

The registration page creates `viewer` accounts; the backend continues to accept its legacy `stockist` role for compatibility. Passwords are hashed with Argon2. JWTs are signed with `JWT_SECRET`, use the configured expiry, and are validated against the current user record on protected requests. Logout removes the browser's stored token; the token remains valid only until expiry if copied elsewhere.

### Changing the backend port

Port 8000 is the default. If it is occupied, start FastAPI on another port, for example 8001:

    .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

Set VITE_API_BASE_URL in frontend/.env to the same backend address (http://127.0.0.1:8001 in this example), then restart the Vite development server. CORS_ORIGINS contains frontend origins, not the backend port; change it only if the frontend itself runs on a different origin.

## Stage 3A API endpoints

All dashboard, product, stockist, pincode, and audit-log endpoints require a valid bearer token. Any authenticated account may read these resources. Product writes, stockist creation, and pincode assignment require the `admin` role.

| Method and path | Access | Behavior |
| --- | --- | --- |
| `GET /dashboard/stats` | Authenticated | Counts products, stockists, and assigned pincodes from MySQL and returns the newest five MongoDB audit entries as `recent_activity`. |
| `GET /products?page=1&limit=10&search=&category=` | Authenticated | Returns `items`, `total`, `page`, `limit`, and `pages`; searches name, SKU, or category and filters by category. Limit is 1-100. |
| `POST /products` | Admin | Creates a product; duplicate SKU returns HTTP 409. |
| `PUT /products/{product_id}` | Admin | Updates a product; unknown IDs return HTTP 404. |
| `DELETE /products/{product_id}` | Admin | Deletes a product and returns HTTP 204. |
| `GET /stockists` | Authenticated | Returns stockists ordered by name. |
| `POST /stockists` | Admin | Creates a stockist. |
| `POST /stockists/{stockist_id}/pincodes` | Admin | Assigns a six-digit pincode. Pincodes are globally unique; duplicates return HTTP 400 with `This pincode is already assigned to another stockist.` |
| `GET /stockists/{stockist_id}/pincodes` | Authenticated | Returns assigned pincodes or HTTP 404 for an unknown stockist. |
| `GET /audit-logs` | Authenticated | Returns the latest 50 MongoDB entries, newest first. |

Successful product create/update/delete operations write `CREATE`/`UPDATE`/`DELETE` audit records with module `Product`. Stockist creation uses module `Stockist`; pincode assignment uses module `Pincode`. Audit entries include the acting user's ID and email, an object-valued details field, and a UTC timestamp. SQL writes are not committed unless the audit insert succeeds. An audit-service failure returns HTTP 503 and rolls back the SQL transaction; SQL commit failures trigger best-effort removal of the corresponding audit event and also return an error.

The assignment uses `admin` and `viewer` roles. Existing Stage 2 installations may also contain `stockist` accounts, so a forward-only migration adds `viewer` to the role constraint without renaming or invalidating any account. `stockist` remains a supported, read-only compatibility role. Public registration rejects `admin`; the UI explicitly registers new read-only accounts as `viewer`, while the API retains its `stockist` default for existing integrations that omit the optional role. Apply the compatibility migration with `.\.venv\Scripts\python.exe -m alembic upgrade head` from the backend directory before registering viewer accounts. The migration's downgrade refuses to remove the viewer role while viewer accounts exist.

## MongoDB audit-log setup

Set `MONGODB_URI` in `backend/.env`; the application selects the `vyanic_stockist` database and the existing `audit_logs` collection. Startup ensures an idempotent descending index named `ix_audit_logs_timestamp_desc` on `timestamp`. Stage 3A writes audit events for the required product, stockist, and pincode mutations and reads them for dashboard and audit-log responses.

## Frontend setup and run

In a second PowerShell window, start from the project root:

```powershell
Set-Location .\frontend
if (-not (Test-Path .\.env)) {
    Copy-Item .\.env.example .\.env
}
npm ci
npm run dev
```

`VITE_API_BASE_URL` in `frontend/.env` should point to the backend, normally `http://127.0.0.1:8000`. Frontend variables are browser-visible and must never contain database credentials or JWT signing keys. The login flow stores the access token in localStorage, Axios attaches it as a bearer token, and protected routes validate the session through `GET /auth/me`.

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`

## Assumptions and Design Decisions

- The public registration page creates Viewer accounts. Public users cannot register as administrators. The API retains its legacy stockist default for compatibility with existing integrations.
- Administrator accounts are created through the secure one-time bootstrap process described above. It prompts for credentials locally and stores a password hash.
- Existing stockist accounts are retained without renaming and remain read-only for compatibility.
- MySQL stores application records, including users, products, stockists, and pincode assignments. MongoDB stores audit logs in the vyanic_stockist database and audit_logs collection.
- Sample records are demonstration data, not production data. The application does not seed sample business records automatically; any records entered for walkthroughs or screenshots should be treated as demonstrations.

## Tests and production build

From the project root, run the backend tests with the configured MongoDB available. API behavior uses isolated SQLite sessions; the audit integration test uses a disposable temporary MongoDB collection:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m pytest
```

From the project root, build the frontend:

```powershell
Set-Location ..
Set-Location .\frontend
npm run build
```

To create a later schema migration after changing ORM models:

```powershell
Set-Location ..\backend
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe schema change"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## Stage 3B frontend integration

The dashboard reads live counts and the latest five audit records from `GET /dashboard/stats`. Products support server-side pagination, search, category filtering, and administrator-only create, update, and delete actions. Stockists and their assigned pincodes are read from the protected stockist endpoints; administrators can create stockists and assign pincodes. The audit page displays the newest 50 records from `GET /audit-logs`. Read-only accounts can inspect all pages but do not see administrator controls. Loading, empty, and error states are rendered without seeded or fabricated records.
