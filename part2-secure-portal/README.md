# PenguWave - Security Operations Portal

PenguWave is an enterprise-grade, high-fidelity Security Operations Center (SOC) dashboard designed to ingest, isolate, and remediate infrastructure security telemetry.

The system features a structured architecture combining a secure **FastAPI (Python)** backend logging pipeline with a typed **React / TypeScript / Vite** frontend workspace. The ecosystem enforces robust Role-Based Access Control (RBAC), advanced mitigations against Broken Object-Level Authorization (BOLA/IDOR), dynamic clearance mapping, and secure session management.

---

# 🏗️ Project Directory Architecture

The project is structured as a unified repository layout, placing frontend configuration files directly within the project root while completely isolating backend computational models inside a dedicated sub-environment.

<details>
<summary><strong>View Project Structure</strong></summary>

```text
├── backend/                      # 🛡️ Relational Telemetry Storage & Routing Engine (FastAPI)
│   ├── app/
│   │   ├── routes/               # REST API Endpoint Matrices
│   │   │   ├── auth.py           # Cryptographic Token Generation Gateway
│   │   │   ├── events.py         # Telemetry Manipulation Pipeline & Isolation Guards
│   │   │   └── users.py          # Administrative Identity Profile Workspace
│   │   ├── config.py             # Pydantic Structural Settings Verification
│   │   ├── crud.py               # Database Mutator Layer & Bcrypt Verification Operations
│   │   ├── database.py           # SQLAlchemy Persistence Configurations & Engine Pools
│   │   ├── dependencies.py       # Global Request Contexts, RBAC & Anti-BOLA Middlewares
│   │   ├── main.py               # Core Web Application Framework Ingress
│   │   ├── models.py             # SQLAlchemy Persistent Database Schema Mappings
│   │   └── schemas.py            # Pydantic Input Validation & Payload Sanitization
│   ├── data/                     # Repository for Source Telemetry JSON Feeds
│   │   └── mock_events.json      # Structured Seed Telemetry Logs
│   ├── tests/                    # Backend Validation Suites (`pytest`)
│   │   └── test_portal.py        # Unified Security Integration Suite (BOLA, Rate-Limiting)
│   ├── .env                      # Local Active Secret Variable Configurations
│   ├── .env.example              # Generic Blueprint Environment Template
│   ├── create_db.py              # Idempotent System Identity & Telemetry Seeding Script
│   └── requirements.txt          # Python Explicit Dependency Lockfile
├── src/                          # 💻 Modern Component UI Workspace (React + TS)
│   ├── components/               # Self-Contained Interface Views & Visual Elements
│   │   ├── EventViewModal.tsx    # Multi-Tier Remediation & Analytical Window
│   │   ├── Navbar.tsx            # Navigation Hub Restricting Context Views Dynamically
│   │   ├── ProtectedRoute.tsx    # Client-Side Virtual Route Session Enforcement Gate
│   │   ├── SignInPage.tsx        # Isolated Authentication Ingress Visual Interface
│   │   └── WelcomeBanner.tsx     # Session Greeter & Adaptive Branding Container
│   ├── context/                  # State Persistence Layers
│   │   └── AuthContext.tsx       # Global Session Context & HttpOnly Token Verification Hub
│   ├── pages/                    # Dynamic High-Level View Panes
│   │   ├── EventsPage.tsx        # Real-Time Operational Telemetry Streams Page (Optimized Max 50 Rows)
│   │   ├── NotFound.tsx          # Standalone 404 Route Interception Template
│   │   └── UsersPage.tsx         # Identity Management Workspace (Admin Exclusive)
│   ├── utils/                    # Common Client-Side Extraction Utilities
│   ├── api.ts                    # Centralized Communication Pipeline mapping Frontend to API
│   ├── App.css                   # Operational Theme Stylesheets
│   ├── App.tsx                   # Central React Layout Engine & DOM Switchboard
│   ├── main.tsx                  # Global Virtual DOM Mounting Layer
│   └── types.ts                  # Shared TypeScript System Boundaries
├── index.html                    # SPA Basic Markup Entrypoint
├── package.json                  # Frontend Dependency Node Manifest
├── run.py                        # 🚀 Core Multi-OS Automation Lifecycle Launcher
└── vite.config.ts                # Build Configuration Engine
```

</details>

---

# 🗄️ Storage Infrastructure Design

User and incident information is stored in a relational database mapping layer utilizing the SQLAlchemy ORM framework.

### Database Engine Selection (SQLite)

SQLite was explicitly selected for this MVP and home assignment because it provides reliable persistent storage while keeping the architecture lightweight, simple, and exceptionally easy to evaluate for the reviewer (requiring zero local database server installations).

### SQL Injection Defenses

Utilizing SQLAlchemy ORM inherently eliminates SQL Injection (SQLi) risks across the application footprint through parameterized query generation and safe data access patterns.

### Production Database Strategy

For an enterprise corporate deployment, PostgreSQL would be preferred over SQLite due to its advanced vertical and horizontal scalability and high concurrency handling capabilities.

> **Architecture Note:** Because the entire application structure was strictly built on top of SQLAlchemy ORM models, migrating the ecosystem from SQLite to PostgreSQL in production requires zero backend code refactoring—it can be fully achieved by swapping a single configuration connection string inside the environment file.

### Soft Delete Lifecycle Execution

The database configuration tracks user states natively via logical Soft Delete semantics.

Deactivated operators are flagged with a persistent `deleted_at` timestamp rather than undergoing physical row purging.

This pattern actively mitigates unique constraint collisions during re-registration pipelines while maintaining unbroken forensic audit trails across historical data sets.

### Strict Identity Bootstrapping & Validation Pipeline

During the initial database migration and seeding lifecycle (`create_db.py`), the application parses the environment variables to initialize the starting user registry.

The bootstrapper enforces a strict structural safety check:

#### 1. Mandatory Administrator Guard

The system requires at least one valid Administrator account with a secure password to be explicitly defined in the `.env` configurations.

If an active admin configuration is missing or structurally invalid, the system halts execution immediately and refuses to start, preventing an unmanaged lockout out of the box.

#### 2. Graceful Fault Tolerance for Secondary Users

If optional testing profiles or auxiliary analyst accounts within the environment string are malformed, missing required schema fields, or fail validation checks, the bootstrapper logs a warning and gracefully skips them.

The application continues to boot successfully with the verified Admin context, ensuring runtime stability despite configuration contract drifts.

---
# 🔐 Core Threat Vectors & Implemented Mitigations

## 1. Authentication & Gateway Hardening

### Threats

* Automated brute-force attacks
* Dictionary attacks
* Credential stuffing

### Mitigations Implemented

#### SlowAPI Rate Limiting

Enforced a network middleware to track host signatures and drop high-velocity attacks with `429 Too Many Requests` before triggering heavy database lookups.

#### Bcrypt Password Salting

Implemented computational cryptographic hashing to ensure plaintext credentials are never logged, stored, or exposed.

#### Stateful Session Checks

Synced the application gateway to re-verify account status flags from the live database context on every request, immediately terminating disabled sessions.

---

## 2. Access Control & Object Isolation (RBAC / BOLA)

### Threats

* Vertical privilege escalation
* Lateral data tampering via resource ID manipulation (IDOR)

### Mitigations Implemented

#### FastAPI Router Dependencies

Mounted explicit security dependencies on administrative endpoint matrices (e.g., `/users`), returning `403 Forbidden` to unauthorized roles before route execution.

#### SQL-Level Context Binding

Prevented BOLA by embedding the caller's validated identity token directly into the SQL generation lifecycle:

```text
db.query(SecurityEvent).filter(SecurityEvent.user_id == current_user.id)
```

#### Pydantic Payload Sanitization

Utilized strict data transfer objects (DTOs) to automatically filter out sensitive credential hashes from leaving the server egress perimeter.

---

## 3. Dynamic Clearance-Tag Authorization Architecture

To meet core security configurations without modifying static source files, the backend incorporates context-aware dynamic access controls.

### Zero-Maintenance Asset Discovery

The application exposes an administrative workflow via:

```text
GET /events/clearance-tags
```

This path analyzes the mock JSON feed on-the-fly using highly optimized set comprehensions to capture all active telemetry identity domains (such as `userId` scopes like `usr-001`, `usr-002`, etc.).

If the telemetry source scales vertically to introduce new actors (e.g., `usr-004`), the backend discovers the scope automatically without code updates.

### Granular UI Permissive Allocation

Administrators use the centralized identity management desk to bind discovered clearance strings to standard Analyst rows.

Permissions serialize cleanly as comma-separated token sequences inside the persistent engine.

---

## 4. Role-Based Access Control (RBAC) Entitlement Matrix

Endpoints map permissions to categorical tiers (`admin`, `analyst`, `viewer`), ensuring strict operational boundaries across the enterprise.

Frontend guards act as a usability layer only—any programmatic UI bypass triggers a strict server-side fallback (`401` or `403`).

| Method   | Endpoint           | Minimum Role Required | Security Ingress Path           |
| -------- | ------------------ | --------------------- | ------------------------------- |
| `POST`   | `/api/auth/login`  | None (Public)         | Request Payload Ingress         |
| `POST`   | `/api/auth/logout` | Any Authenticated     | Session Cookie Clearance        |
| `GET`    | `/api/auth/me`     | Any Authenticated     | Identity Session Sync           |
| `GET`    | `/api/events`      | `viewer`              | Context-Bound Telemetry View    |
| `PATCH`  | `/api/events/{id}` | `analyst`             | Workflow Note Modifications     |
| `POST`   | `/api/events`      | `analyst` (Pipeline)  | Automated Log Ingestion Channel |
| `DELETE` | `/api/events/{id}` | `admin`               | Explicit Forensic Purge         |
| `ALL`    | `/api/users/*`     | `admin`               | Administrative Profile Controls |

---

## 5. Injection & Script Execution (XSS / SQLi)

### Threats

* Client-side session hijacking via malicious log payloads
* Backend database compromise

### Mitigations Implemented

#### React JSX Entity Encoding

Eradicated raw HTML rendering vectors (`dangerouslySetInnerHTML`), utilizing native React text node interpolation to escape scripts automatically.

#### SQLAlchemy Parameterization

Abstracted raw queries into predefined ORM objects, eliminating SQL Injection vectors by preventing user input from mutating SQL commands.

---

## 6. Data Exposure & Session Hijacking

### Threats

* Stolen session tokens via client-side script exfiltration
* Unauthorized cross-origin data access

### Mitigations Implemented

#### HttpOnly & Secure Cookies

Transmitted JWT tokens within hidden browser cookie contexts (`credentials: "include"`), breaking the line of sight from malicious JavaScript.

#### CORS Gateway Controls

Restricted Cross-Origin Resource Sharing strictly to the verified frontend host address to drop anonymous cross-domain traffic.

#### Centralized Client Guardrails

Configured the frontend client to intercept `401 Unauthorized` states globally, instantly purging stale UI states and forcing login redirection.

#### Hardened Configurations & Environmental Overrides

Crucial application criteria are structured using Pydantic BaseSettings to enforce safe fallback baselines (*Hardened Defaults*).

These values are declared inside `.env` variables to give deployment pipelines runtime control over security policies without altering source files:

```ini
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

#### Decoupled Lifecycle Pipelines

Backend paths for log creation (`POST`) and records purging (`DELETE`) are fully coded and structurally isolated.

While security events originate from remote automated sensors rather than manual dashboard operations, these paths feature independent RBAC checks.

The administrative `DELETE` gateway strictly prevents malicious log tampering by unprivileged users attempting to conceal intrusion traces.

#### Dual-Control Lockout Mitigations

The database controller explicitly restricts an active administrator from executing deletion or status mutations against their own personal profile context.

This ensures continuous system management access, while enterprise multi-operator deployments can scale toward strict dual-authorization controls.

---
# 📊 UI & Data Telemetry Optimization

To match the operational workflows of a real-world Security Operations Center (SOC), the event display model was optimized.

### Frontend Scale

Increased the default `PAGE_SIZE` from 10 to 50 inside `EventsPage` to allow analysts a holistic view of concurrent security threats without constant context-switching via manual pagination.

### Backend Alignment

Synced the API client logic (`getEvents`) to dynamically request up to 50 telemetry records per chunk, maximizing rendering efficiency while strictly respecting server-side limits.

### Egress Telemetry Normalization

To preserve relational simplicity in the database schema, the unstructured raw `tags` list was omitted from the relational layer.

The application handles this normalization seamlessly during frontend ingestion by fallback-mapping empty data sets (`[]`), ensuring layout continuity.

### Hermetic Component Roots

The authentication screen is engineered as a strict `Conditional Root Component` within `App.tsx` rather than a standard accessible client-side path.

This design completely eliminates client-side routing bypass techniques, blocking unauthenticated browsers from compiling UI layers or operational views in local memory before access token verification completes.

### Forensic Evidence Integrity Layer

The interface preserves a dedicated raw telemetry pane at the base of the `EventViewModal`.

In active incident response operations, analysts require untampered log visibility to review metadata fields directly from edge devices, ensuring strict audit trail verification.

---

# 🚀 Deployment Instructions & Ecosystem Initialization

PenguWave utilizes an automated bootstrapper capable of setting up and launching the full-stack environment across any host OS (Windows, macOS, Linux).

## Prerequisites

Ensure your local host machine has the following foundational runtimes installed:

* Python 3.10+
* Node.js 18+ (with npm)

---

## 1. Initialize Configuration Environment

Clone the repository and duplicate the provided blueprint environment template inside the backend directory.

The application is configured to run securely out-of-the-box using these predefined variables:

```bash
cp backend/.env.example backend/.env
```

(Optional) If you wish to inspect or modify the runtime parameters, the generated `backend/.env` file contains the following separated structural variables:

```ini
DATABASE_URL=sqlite:///./users.db
JWT_SECRET_KEY=penguwave_super_secret_security_operations_key_2026
```

---

## 2. Execute the Automated Bootstrapper

Run the centralized launch utility in your terminal window.

The script will dynamically evaluate your host operating system, create an isolated virtual workspace (`.venv`), install all required libraries cleanly, build database structures, inject mock metrics, and spin up both microservice runtimes simultaneously:

```bash
python run.py
```

### Database Persistence Behavior

During the first initialization, the application automatically creates a local SQLite database file inside the backend project directory.

If the database file already exists, subsequent executions will reuse the existing database and preserve all previously created users, incidents, and application data.

This behavior allows the environment to retain state across restarts and prevents accidental loss of data between development sessions.

To start with a completely fresh environment, manually delete the SQLite database file from the backend directory before running the bootstrap process again.

---

## Available Endpoints

### SOC Portal Interface Client Dashboard

```text
http://localhost:5173
```

### Automated REST API Documentation Portal (Swagger)

```text
http://localhost:8000/docs
```

> **Development Workspace Note:** The Swagger utility remains unlocked inside this local assessment setup to ease endpoint testing. For enterprise production deployments, this interface is entirely disabled to restrict perimeter enumeration vectors.

---

# 📈 Future Security Enhancements Roadmap

## Distributed Production Caching (Redis)

Transition the local thread-locked in-memory rate limiter to an external, high-speed Redis cluster shared across multiple stateless application containers running behind a load balancer.

This removes memory footprint boundaries and ensures persistence across system failures.

---

## Dedicated Authentication Audit Table

Scale the user schema to support a separate forensic audit table tracking:

* Authentication attempts
* Account state lock events
* Incoming IP addresses
* User-agent properties

This reinforces incident investigation loops and long-term forensic visibility.

---

## CI/CD Security Scans

Integrate static application security testing (SAST) utilities such as:

* Bandit
* Dependency audit pipelines

into the deployment workflow to fail builds automatically upon detecting high-severity CVE profiles.

---
