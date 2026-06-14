# PenguWave - Security Operations Portal

PenguWave is an enterprise-grade, high-fidelity Security Operations Center (SOC) dashboard designed to ingest, isolate, and remediate infrastructure security telemetry.

The system features a structured architecture combining a secure **FastAPI** backend logging pipeline with a typed **React / TypeScript / Vite** frontend workspace. The ecosystem enforces robust Role-Based Access Control (RBAC), advanced mitigations against Broken Object-Level Authorization (BOLA/IDOR), and stateful token revocation metrics.

---

## 🏗️ Project Directory Architecture

The project is structured as a unified repository layout, placing frontend configuration files directly within the project root while completely isolating backend computational models inside a dedicated sub-environment.

├── backend/                      # 🛡️ Relational Telemetry Storage & Routing Engine
│   ├── app/
│   │   ├── routes/               # REST API Endpoint Matrices
│   │   │   ├── auth.py           # Cryptographic Token Generation & Revocation Gateway
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
│   ├── tests/                    # Backend Validation Suites
│   ├── .env                      # Local Active Secret Variable Configurations
│   ├── .env.example              # Generic Blueprint Environment Template
│   ├── create_db.py              # Idempotent System Identity & Telemetry Seeding Script
│   ├── requirements.txt          # Python Explicit Dependency Lockfile
│   └── users.db                  # Local SQLite Database Instances
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
│   │   ├── EventsPage.tsx        # Real-Time Operational Telemetry Streams Page
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


---

## 🗄️ Storage Infrastructure Design

User and incident information is stored in a relational database mapping layer utilizing the SQLAlchemy ORM framework.

* **Database Engine Selection (SQLite):** SQLite was explicitly selected for this MVP and home assignment because it provides reliable persistent storage while keeping the architecture lightweight, simple, and exceptionally easy to evaluate for the reviewer (requiring zero local database server installations or complex docker setups).
* **Application Fit:** The assignment requirements are relatively small, with a limited number of users and no immediate need to support massive concurrent write operations or highly distributed multi-node deployments.
* **SQL Injection & Maintainability Defenses:** Utilizing SQLAlchemy provides a robust abstraction layer over the raw database layer. It radically improves code maintainability and inherently eliminates SQL Injection (SQLi) risks across the application footprint through parameterized query generation and ORM-based safe data access patterns.
* **Stored Schemas:** The database safely stores system user accounts, cryptographic password hashes, and user role tracking matrices required to power the global authentication and authorization flows.
* **Production Database Strategy:** For an enterprise corporate deployment, PostgreSQL would be heavily preferred over SQLite due to its advanced vertical and horizontal scalability, high concurrency handling capabilities, integrated point-in-time recovery backup tools, and extensive operational tooling ecosystems. 
  
  > *Architecture Note:* Because the entire application structure was strictly built on top of SQLAlchemy ORM models, migrating the ecosystem from SQLite to PostgreSQL in production requires zero backend code refactoring—it can be fully achieved by swapping a single configuration connection string inside the environment file.

---

## 🔐 Advanced Security Engineering Implementations

### 1. Robust Mitigation Against Broken Object-Level Authorization (BOLA / IDOR)
To prevent lateral compromise strategies—where an operational analyst alters URL path markers or telemetry trackers to view or modify incidents assigned to an unrelated corporate team member—the backend implements explicit, dual-layer context isolation:

* **Query Injection Defense (`GET /events`):** Incoming query tracking logic does not apply post-filtering inside application memory. Instead, user session contexts are bound directly during the SQL execution phase:
  
  $$\text{Query Constraint: } \texttt{db.query(SecurityEvent).filter(SecurityEvent.user_id == current\_user.id)}$$
  
  Admins bypass this filter entirely to gain a global corporate operational overview.
* **Path Interception Middleware (`verify_user_ownership_or_admin`):** This global dependency extracts parameter variables (`user_id`) directly out of the active URL string parameters, performing cross-examination checks against the cryptographic cookies before releasing network payloads.

#### Dynamic Clearance-Tag Authorization Architecture
To meet strict security requirements without altering or modifying the static mock data repository, the system avoids fragile, hardcoded user permissions. Instead, it handles authorization dynamically using a context-aware hybrid RBAC (Role-Based Access Control) and Attribute-Based approach:
1. **Dynamic Log Analysis (Zero Code Maintenance):** Rather than maintaining an independent, fragile synchronized list of permissible identity scopes, the backend exposes a dedicated administrative workflow endpoint: `GET /events/clearance-tags`. This endpoint parses the raw JSON repository on-the-fly using a high-performance Python set comprehension to isolate all unique `userId` tags currently present within the active logs. If the static dataset expands in the future (e.g., adding a new log file from `usr-004`), the backend instantly discovers the new identity scope without requiring a code redeploy or configuration file updates.
2. **Admin User Management UI Allocation:** From the frontend User Management console, an administrator can dynamically map one or more discovered clearance profiles to any approved Analyst account. These permissions are serialized and stored as a comma-separated string within the persistent database (`clearance_tags` column).
3. **Enforcing Object Isolation:** When an Analyst requests the event stream via `GET /events/`, the application enforces strict server-side validation using the trusted context derived from their validated identity token (JWT):
   ```python
   allowed_tags = [tag.strip() for tag in current_user.clearance_tags.split(",")]
   filtered_events = [e for e in all_events if e.get("userId") in allowed_tags]


2. Role-Based Access Control (RBAC) Entitlement Matrix
Endpoints map permissions to categorical tiers (admin, analyst, viewer), ensuring strict operational boundaries across the enterprise. Analysts are strictly constrained to modify (status, comments) only rows where the event resource matches their authenticated token context. Administrators bypass this restriction globally, allowing them to reassign events or override severities across the entire corporate perimeter, while structural forensic data remains completely intact:

API Router & Endpoint Target,Authorization Intent,Admin Clearance,Analyst Clearance,Viewer Clearance
POST /auth/login,Ingress Authentication,Allowed,Allowed,Allowed
POST /auth/logout,Session Token Revocation,Allowed,Allowed,Allowed
GET /events,View Assigned Incidents Log,Full Scope View,Assigned View Only,Assigned View Only
GET /events/{id},Fetch Specific Incident File,Bypass Verification,Ownership Bound,Ownership Bound
POST /events,Ingest Foreign Log Streams,Allowed,Blocked (403),Blocked (403)
PATCH /events/{id},Modify Operational Analytics,Full Payload Edit,Workflow/Notes Only,Blocked (403)
DELETE /events/{id},Purge Target Telemetry Record,Allowed,Blocked (403),Blocked (403)
ALL /users Routes Matrix,Admin Identity Workspace,Allowed,Blocked (403),Blocked (403)

3. Session Revocation & Brute-Force Safeguards
Anti-Replay Token Revocation: Logouts do not merely drop client memory pointers. Calling POST /auth/logout takes the current JWT signature and writes it to a persistent database cache array via the BlacklistedToken engine. Every endpoint validated by get_current_user checks this database index to deny compromised or discarded session keys instantly.

Network Rate-Limiting & In-Memory Lockout Semantics: Essential entry ports incorporate defensive middleware (slowapi integration tracking remote host signatures), gracefully dropping brute-force dictionary attempts and denial-of-service vectors by serving strict 429 Too Many Requests states.

Distributed Production Strategy Note: In the current local development environment, an in-memory storage dictionary backed by an explicit Threading Lock is an exceptionally fast, lightweight, and highly effective solution to manage failed authentication tracking. However, in a distributed production environment running across multiple concurrent server nodes behind a Load Balancer, standalone application memory is unshared (Server A will be blind to failed attempts hitting Server B). Furthermore, any service container restart or crash completely wipes the active ban list. Therefore, in a true production deployment, this in-memory dictionary would be swapped for an external, high-speed Redis cluster. Redis acts as a centralized, persistent caching and validation layer shared across all server instances, guaranteeing robust, uniform Rate Limiting and lockout persistence.

Input Validation & Sanitization Gates: Data boundaries are enforced via rigid Pydantic models. String constraints (min_length, max_length), precise Literal evaluation blocks, and explicit length bounds (e.g., maximum 1000 characters on incident commentary) actively neutralize script insertion vectors and buffer manipulation strategies before they can touch the persistence layer.

🛠️ Comprehensive Architectural Component Breakdown
🛡️ Backend Structural Implementation (backend/app/)
main.py (Gateway Bootstrap): Instantiates the primary FastAPI framework container. Hooks global exception handlers to shield sensitive runtime traces, formats uniform JSON fallback wrappers for uncaught 500 Internal Server Errors, and bounds host runtime origins via restrictive CORS resource parameter definitions (CORS_MIDDLEWARE).

Environment Security Note: During local development, the interactive Swagger documentation framework (/docs) remains fully exposed to ensure friction-free testing, evaluation, and seamless endpoint visibility for the reviewer. In a production environment, these documentation endpoints would be completely deactivated or restricted behind hardened corporate network perimeters (VPN/IP Whitelisting) to prevent unauthorized malicious actors from mapping out the API schema landscape.

config.py (Environmental Enforcement Hub): Utilizes pydantic_settings to ingest local configurations (.env) safely. Evaluates the physical validity of variables before server boot, throwing a clean execution error if cryptographic parameters are missing, which prevents insecure misconfigurations in production.

The system uses highly robust Hardened Defaults baked into the Pydantic configuration class to ensure the environment is securely optimized "out of the box":

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

MAX_FAILED_ATTEMPTS=5

LOCKOUT_DURATION_MINUTES=15

While these limits are strictly enforced by default, the Pydantic settings pipeline routes them directly through the environment variable parsing stack. This enables Deployment teams to implement dynamic Runtime Overrides straight from the production .env file, allowing them to harden session expirations or alter lockout durations seamlessly without modifying or recompiling the core source code.

models.py (Relational Persistence Blueprints): Directs the mapping of tables to physical disk blocks using SQLAlchemy:

User: Manages system identifiers, emails, operational roles, and soft-delete preparation attributes.

SecurityEvent: Houses complex event metrics, utilizing relational foreign key parameters (user_id) to maintain secure database-level linkage.

BlacklistedToken: Tracks explicitly revoked session keys to combat session hijack strategies.

schemas.py (Data Transfer Sanitization DTOs): Governs strict contract boundaries separating raw input arrays from database schemas. Employs EmailStr validations to ensure input profiles strictly conform to RFC standards and omits the transmission of structural credential hashes (password_hash) out of egress server packets.

dependencies.py (Session Evaluation Layer): Extracts authentication payloads out of secure, client-hidden HttpOnly cookie paths. Verifies cryptographic hashes, catches expiration flags (ExpiredSignatureError), and screens account states to block users administratively disabled mid-session.

crud.py (Relational Mutator & Password Hashing): Coordinates write-loops to the physical database file. Computes highly secure password storage structures by wrapping inputs in computationally heavy salt layers via the Bcrypt cryptographic algorithm, maintaining absolute defense against lookup-table or timing attacks.

routes/events.py (Incident Orchestration Routing Matrix): Controls incident logging workflows. Protects write operations via administrative role checks and includes the PATCH mitigation workflow that rejects analyst requests if they attempt to modify system fields (such as changing an incident's severity or changing its assigned owner).

Architecture Note: While the current frontend requirements only mandate displaying and modifying status metrics for the pre-seeded incidents, the POST and DELETE endpoints are fully built, authenticated, and structurally complete inside this router. This decouples the layers completely: extending the system to support a live ingestion pipeline or administrative record purging from the user interface requires absolutely zero backend refactoring—only wiring up corresponding UI components.

Event Ingestion & Purging Rationale: The endpoints for creating and purging logs exist to mirror a real-world security product framework. In real SIEM environments, security incidents are never hand-keyed into a UI by a human analyst; they are dynamically ingested via external automated ingestion pipelines and sensors monitoring infrastructure endpoints. The POST route represents this automated gateway, validating incoming telemetry integrity and mapping events to active users. Conversely, the DELETE route is restricted under a rigid administrative RBAC guardrail to demonstrate explicit protection against Log Tampering—preventing a malicious, compromised analyst account from wiping log files to erase footprints of corporate espionage or lateral movement.

routes/users.py (Identity Space Administration): Empowers administrative configurations to control user profiles. Implements specialized defensive loops to prevent an authenticated admin from accidentally altering their own status to disabled or removing their profile, preventing administrative lockout loops.

Administrative Self-Action Rationale: In this execution framework, administrators are fully empowered to manage, modify, or delete other administrative profiles, but are strictly blocked from executing status alterations or deletion queries on their own active sessions to prevent accidental self-lockout. In an enterprise production deployment, this threshold would be significantly tightened by implementing a Dual Control / Two-Man Rule configuration pattern. Any security action targeting a management-level core profile would require separate authorization from a secondary independent administrator, preventing a single compromised admin account from executing privilege escalation or locking out the remaining security team.

💻 Frontend Structural Implementation (src/)
App.tsx & main.tsx (Ecosystem Frame & Routing Matrix): Establishes the virtual layout frame of the Single Page Application. Wraps standard DOM rendering arrays with strict conditional switches via react-router-dom, connecting client session flags to physical paths.

UI Architecture Rationale: The login portal interface is intentionally implemented as a strict Conditional Root Component directly inside App.tsx rather than a standard client-side page Route. This structural pattern explicitly targets the mitigation of Client-Side Route Bypass. By completely withholding the rendering of dashboard components, internal data models, or layouts from the browser memory layout entirely until a user completes successful cryptographic authentication, the framework achieves hermetic presentation isolation. It prevents any structural Layout Leakage or codebase visibility to unauthenticated or anonymous network connections.

context/AuthContext.tsx (Session State Synchronization Core): Acts as the centralized authentication lifecycle monitor. Polls the backend interface (/auth/me) upon mount to determine user identity contexts, propagating validation attributes down to every dependent application screen.

components/ProtectedRoute.tsx (Client-Side Virtual Barrier): Intercepts client navigation tasks before interface compilation occurs. Evaluates current role claims against route-level conditions, dropping non-authenticated tracking routines back to the base route.

components/EventViewModal.tsx (Granular Telemetry Panel): A responsive administrative portal window that adapts its interactive interface elements based on user roles. If accessed by a Read-Only Viewer, input nodes swap to unmodifiable elements. If accessed by an Analyst, it opens workflow controls for updating status and comments while blocking administrative fields. For Admins, it grants full system configuration permissions.

Evidence & Audit Integrity Rationale: Preserving the raw JSON payload terminal block at the base of the event modal represents a foundational Cyber Security Best Practice. During live Incident Response (IR) operations, forensic analysts require untampered, non-manipulated access to the original source telemetry compiled by remote infrastructure sensors. Displaying this raw telemetry block safeguards evidence integrity, empowers deeper forensic analysis of metadata parameters that are unrendered in standard form views, and serves as an interactive confirmation that the API data contract remains fully populated and structurally accurate.

components/WelcomeBanner.tsx (Branding Separation Frame): Isolates systemic authentication workflows from core interface structures. Visually abstracts corporate greeting statements completely outside primary card containment areas to elevate scanning efficiency.

pages/EventsPage.tsx (Live Workspace Monitor): Drives the primary interface of the portal. Leverages memoized filtering algorithms (useMemo) to enable lightning-fast client-side categorization of active security incidents by text patterns or severity levels, and includes automated JSON file generation routines for exporting records.

pages/UsersPage.tsx (Administrative Control Console): An enterprise management workspace exposed exclusively to administrators. It maps live endpoints to edit grids, allowing real-time account creation, permission updates, and profile deactivation loops.

api.ts (Unified Connection Pipeline): Translates standard JavaScript fetch operations into strongly-typed asynchronous backend requests. Includes an error-parsing handler (parseApiError) that breaks down structural validation trace records from the API into actionable, human-readable notifications.

👥 User Lifecycle & Telemetry Integration
Seed Profiles: The initial registry bootstrap script injects designated testing accounts with persistent hardcoded IDs matching the static mock_events.json data source out of the box. This architecture populates the security monitoring UI with relevant data instantly upon setup, linking sample events to real user models.

Dynamic Provisioning Control: New user profiles created via the Administrative Control Console are safely provisioned using standard UUID v4 identifiers to guarantee robust, cryptographically unguessable BOLA/IDOR protection. Any telemetry logs generated after dynamic account provisioning must be mapped explicitly against these auto-generated database string IDs.

User Erasure Management (Hard vs Soft Delete Semantics): The database User model supports an explicit deleted_at timestamp column to enable theoretical Soft Delete configurations. However, to closely align with single-page application frontend state behaviors and inherently prevent unique constraint conflicts (e.g., if an administrator attempts to re-register an identical corporate email that was previously removed), a standardized Hard Delete execution loop was prioritized inside the administrative user deletion portal.

Future Schema Upgrade Strategy: In the next structural iteration of the user lifecycle, the deletion pipeline will migrate to a full Soft Delete model. The auth dependencies will be upgraded to automatically filter out users possessing a valid deletion timestamp, and registration constraints will resolve conflict blocks by checking and reactivating historical soft-deleted entries.

📉 Known Scope Limitations & Data Contract Drift
Telemetry Tags Contract Drift: In the original API specifications contract, security incidents are defined with a contextual list array of tags. However, during the initial architecture phase of the persistence layer, this field was temporarily omitted from structural database columns to maintain a clean, flat relational entity table.

To handle this drift safely, a Frontend Normalization Pattern was built into the UI data parsing layer. It evaluates incoming records and automatically binds an empty array structure ([]) to any missing tag parameters, preventing client-side property validation crashes. In subsequent versions, a native SQLite JSON extension column or text-serialized array mapping will be integrated into create_db.py to preserve full tag telemetry structures permanently across database updates.

🚀 Deployment Instructions & Ecosystem Initialization
PenguWave utilizes a zero-configuration automated bootstrapper capable of setting up and launching the full-stack environment across any host OS (Windows, macOS, Linux).

Prerequisites
Ensure your local host machine has the following foundational runtimes installed:

Python 3.10+

Node.js 18+ (with npm)

1. Initialize Configuration Environment
Clone the repository to your local path directory and duplicate the provided blueprint environment template inside the root directory:
cp backend/.env.example backend/.env

Open your local configuration file (backend/.env) and define your explicit operational attributes:
DATABASE_URL=sqlite:///./users.db
JWT_SECRET_KEY=penguwave_super_secret_security_operations_key_2026

USER_001_EMAIL=admin@penguwave.io
USER_001_PASSWORD=admin_secure_pass_123

2. Execute the Automated Bootstrapper
Run the centralized launch utility in your terminal window. The script will dynamically evaluate your host operating system, create an isolated virtual workspace (.venv), install all required libraries cleanly, build database structures, inject mock metrics, and spin up both microservice runtimes simultaneously:

python run.py

Once initialized, the platform endpoints become accessible:

SOC Portal Interface Client Dashboard: http://localhost:5173

Automated REST API Documentation Portal (Swagger): http://localhost:8000/docs

📈 Future Security Enhancements Roadmap
The current implementation keeps the structural user and incident models intentionally simple and tightly focused on satisfying the core assignment metrics. However, the decoupled design allows for seamless integration of specialized security extensions:

Authentication Audit Logging Engine: Integrate a dedicated system audit table to record all identity and authentication activities. This forensic logging table would dynamically capture:

Event timestamps and absolute execution markers.

Success or failure flags for authentication and authorization requests.

Incoming network communication source context (source_ip).

Targeted user profile lockout states and administrative restriction events.

User-Agent metadata signatures to trace client system footprints.

This extension directly bolsters robust threat monitoring, rapid incident response verification, automated brute-force threat modeling, and regulatory compliance logging without inflating the baseline properties of the core User profile model.

Derived Temporal Metrics: Derive temporal tracking statistics—such as an active analyst's last successful system login time—on-the-fly by parsing forensic audit data logs using optimized database indexes, avoiding the need to store fluid, high-write state variables directly on the primary identity tables.

Decoupled Asynchronous Ingestion Buffer: Route high-velocity log creation flows (POST /events) through a distributed streaming cluster (such as Apache Kafka or AWS Kinesis) rather than executing direct synchronous database writes. This insulates database availability during distributed denial-of-service (DDoS) log flooding events.

Distributed Storage Layer Migration: Transition the internal lightweight file-bound SQLite engine to an elastic relational database cluster (such as a multi-AZ PostgreSQL deployment or Amazon Aurora) managed through optimized server connection pools (e.g., PgBouncer).

Stateless Clustering & Shared Cache Tiering: Containerize the FastAPI gateway layer using stateless engine replicas (Docker / Kubernetes topologies) managed behind an application load balancer. Migrate the token revocation matrix (BlacklistedToken) out of standard disk entities and into a low-latency, high-performance distributed key-value cache memory space (such as Redis).