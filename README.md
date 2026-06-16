# Upwind Security – Software Engineering Home Assignment

This repository contains a complete security workflow composed of two connected components:

1. **Part 1 – PenguWave Threat Intel (Gmail Add-on)**
   A Google Workspace Add-on that analyzes opened emails, calculates a risk score, and forwards suspicious findings to the backend.

2. **Part 2 – Secure Operations Portal (Full-Stack SOC)**
   A secure FastAPI backend and React dashboard used to manage users, authenticate analysts, store incidents, and review security events.

Although each assignment can be reviewed independently, they are also integrated into a single end-to-end security workflow.

---

# 📐 End-to-End Architecture

```text
 Gmail Email
      │
      ▼
 Gmail Add-on
 (Part 1)
      │
      │ POST /api/v1/addon/analyze
      ▼
 FastAPI Backend
 (Part 2)
      │
      ├── Threat Scoring
      ├── RDAP Domain Enrichment
      ├── User Correlation
      └── Incident Creation
      │
      ▼
 SQLite Database
      │
      ▼
 React Analyst Portal
```

---

# 📧 Email Analysis Flow

1. A user opens an email inside Gmail.
2. The Gmail Add-on extracts email metadata:

   * Sender
   * Recipient
   * Subject
   * Body
3. The Add-on sends the metadata to the backend endpoint:

```text
POST /api/v1/addon/analyze
```

4. The backend evaluates phishing indicators using local heuristics.
5. The backend performs RDAP domain enrichment to inspect domain age.
6. A risk score and verdict are generated.
7. Emails scoring above the configured threshold are persisted as SecurityEvent records.
8. Created incidents become visible through the React analyst dashboard.

# 📂 Repository Structure


```text
repository-root/
├── README.md
├── requirements.txt
├── run.py
│
├── part1-gmail-addon/
│   ├── Code.gs
│   ├── appsscript.json
│   └── README.md
│
└── part2-secure-portal/
    ├── backend/
    │   ├── app/
    │   │   ├── routes/
    │   │   ├── config.py
    │   │   ├── crud.py
    │   │   ├── database.py
    │   │   ├── dependencies.py
    │   │   ├── main.py
    │   │   ├── models.py
    │   │   └── schemas.py
    │   │
    │   ├── create_db.py
    │   ├── .env.example
    │   └── README.md
    │
    ├── src/
    │   ├── components/
    │   ├── context/
    │   ├── pages/
    │   ├── utils/
    │   ├── api.ts
    │   ├── App.tsx
    │   └── main.tsx
    │
    ├── package.json
    └── vite.config.ts
     
```
</details>
# 🚀 Quick Start

The repository includes a cross-platform bootstrapper capable of preparing and launching the complete environment on Windows, macOS, and Linux.

## Prerequisites

Before running the system for the first time, create the required environment files from their corresponding template files:

```text
.env
part2-secure-portal/.env
part2-secure-portal/backend/.env
```

using:

```text
.env.example
part2-secure-portal/.env.example
part2-secure-portal/backend/.env.example
```

The provided template values are sufficient for evaluation purposes and can be used without modification.

Detailed environment configuration instructions, variable descriptions, security settings, and seed-user initialization behavior are documented in:

* `part2-secure-portal/backend/README.md`

## Platform Requirements

### Python

Python 3.10 or newer is required.

### Node.js

Node.js (and npm) are required to build and launch the React dashboard.

If Node.js is unavailable, the launcher automatically skips the frontend startup sequence while keeping the FastAPI backend and Swagger documentation fully operational.

## Launching the Platform

Navigate to the repository root directory and execute:

### Windows

```bash
python run.py
```

### macOS / Linux

```bash
python3 run.py
```

## Automated Bootstrap Actions

The launcher automatically:

* Creates a Python virtual environment (`.venv`) if missing
* Detects and repairs incompatible virtual environments created on different operating systems
* Installs all Python dependencies from the root `requirements.txt`
* Initializes and seeds the SQLite database
* Installs frontend Node.js dependencies
* Launches the FastAPI backend
* Launches the React frontend when Node.js is available

## Available Services

### React Dashboard

```text
http://localhost:5173
```

### FastAPI Backend

```text
http://127.0.0.1:8000
```

### Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

---

## Database Persistence

During the first execution, the launcher automatically creates and initializes the local SQLite database.

If the database already exists, subsequent executions preserve all previously created users, incidents, and application state.

To start from a completely clean environment, delete the database file and rerun the launcher.


---

# 🌐 Optional Gmail Integration

To test the live Gmail Add-on against the local backend:

1. Ensure the FastAPI backend is running on port 8000.
2. Start an HTTPS tunnel using Ngrok:

```bash
ngrok http 8000
```

3. Copy the generated HTTPS URL.
4. Update the `BACKEND_URL` variable inside `Code.gs`.
5. Add the Ngrok domain to `urlFetchWhitelist` in `appsscript.json`.
6. Deploy the Apps Script project as a Test Deployment.
7. Open Gmail and test the Add-on against real emails.

If the backend is unavailable, the Add-on automatically falls back to a local demonstration mode and displays a fallback verdict without crashing the user interface.

---

# 🛡️ Security Highlights

### Authentication & Session Security

* JWT-based authentication
* Password hashing using bcrypt
* Session validation on protected routes
* Account status verification on authenticated requests

### Authorization

* Role-Based Access Control (RBAC)
* User ownership validation
* Administrative route protection

### Backend Protection

* Rate limiting using SlowAPI
* Generic error responses
* Soft-delete support for user records

### Email Threat Analysis

* Phishing keyword detection
* Domain age enrichment through RDAP
* Explainable scoring signals
* Automatic incident creation for suspicious emails

### Unknown Recipient Handling

If an email recipient does not match an existing user record, the generated incident is associated with a fallback identifier (`usr-unidentified`) to preserve the event while preventing incorrect user attribution.

---

# 📚 Additional Documentation

Detailed implementation notes are available in:

* `part1-gmail-addon/README.md`
* `part2-secure-portal/backend/README.md`
* `part2-secure-portal/THREAT_THINKING.md`
