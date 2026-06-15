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

| Path | Purpose |
|--------|---------|
| `part1-gmail-addon/` | Gmail Add-on implementation |
| `part2-secure-portal/backend/app/routes/` | Authentication, user, event and email analysis APIs |
| `part2-secure-portal/backend/README.md` | Backend setup and configuration guide |
| `part2-secure-portal/src/` | React frontend application |
| `run.py` | Project bootstrap and startup script |



# 🚀 Quick Start

The repository includes an automated launcher script that prepares the environment and starts all required services.

## Prerequisites

Before running the system for the first time, create a local `.env` file based on the provided `.env.example` template.

The application requires environment-specific configuration such as secrets, seed user configuration, and runtime settings.

Detailed setup instructions, environment variable descriptions, and user initialization options are documented in:

- `part2-secure-portal/backend/README.md`


```bash
python run.py
```

The launcher automatically:

* Creates a Python virtual environment if missing
* Installs backend dependencies
* Initializes the SQLite database
* Installs frontend dependencies
* Starts the FastAPI backend
* Starts the React frontend

After startup:

**React Dashboard**

```text
http://localhost:5173
```

**FastAPI Backend**

```text
http://127.0.0.1:8000
```

**Swagger Documentation**

```text
http://127.0.0.1:8000/docs
```

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
