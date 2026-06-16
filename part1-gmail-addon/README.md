# Part 1: PenguWave Threat Intel – Gmail Add-on

A lightweight, enterprise-grade Google Workspace Add-on designed to intercept, analyze, and score inbound email threats in real-time.

The add-on acts as a security sensor, extracting contextual metadata and communicating with a centralized intelligence hub.

---

# 🏗️ Architectural Reasoning & Design Decisions

During development, we evaluated two architectural paths for managing Scan History and Domain Blocklists:

### Option A — Monolithic DB Integration

Coupling the Add-on directly to the Analyst Portal's core database.

### Option B — Decoupled Stateless Sensor (**Chosen Approach**)

Keeping the Add-on's operational storage containerized leveraging Google Workspace's native `PropertiesService`, while offloading the core threat analysis matrices to the central FastAPI gateway.

## Why this approach was chosen

### Fault Tolerance & Resilience (Fail-Secure)

If the centralized backend gateway or database experiences downtime, the Add-on does not crash or degrade the user's email experience.

It gracefully falls back to local sandbox heuristics, ensuring continuous operational visibility.

### Separation of Concerns

The Analyst Portal (Part 2) is built for global SOC operations, while the Gmail Add-on is an endpoint sensor.

Isolating local user preferences (like a personal blocklist) inside Google's secure user-space prevents database bloat and schema cross-contamination.

### Horizontal Scalability

The FastAPI backend remains entirely stateless for email evaluation, allowing it to handle thousands of concurrent API requests from multiple corporate endpoints without bottlenecking on database I/O write locks.

---

# 🌐 Secure Tunneling vs. Production Engineering

## Local Sandbox Environment

Ngrok was utilized strictly as a temporary staging sandbox tool to bridge contextual webhooks from Google's cloud servers to our localhost backend over an encrypted HTTPS tunnel.

## Enterprise Risk Awareness

We are fully aware that deploying long-term exposure layers via Ngrok or similar tunneling tools in a production environment introduces corporate risks, including:

* Shadow IT vectors
* Firewall perimeter bypasses

## Production Architecture Target

The production blueprint dictates that the Add-on targets an official, permanent, and secured enterprise domain:

```text
api.penguwave.com
```

Protected behind:

* Enterprise WAF
* Rate limiting
* Centralized API Gateway

---

# ⚡ Key Features

### Contextual Maliciousness Analyzer

Evaluates risk metrics based on:

* Sender reputation
* Urgent sentiment analysis
* Structural email indicators

### Fail-Secure Fallback Strategy

Implements an asynchronous network exception handler.

If the central FastAPI hub is unreachable, a local sandbox fallback mode triggers seamlessly, maintaining UI integrity.

### Native Defensive Controls

Allows analysts or users to block suspicious sender domains on the fly, persisting state securely within Google's `PropertiesService`.

### Recent Session History

Caches a rolling window of recent telemetry scans for local audit trails without querying cross-origin data structures.

---

# 🛡️ Security Configuration (Manifest)

To comply with enterprise security constraints and restrict malicious data exfiltration, the Add-on implements strict OAuth scopes and network isolation policies inside `appsscript.json`.

### gmail.addons.execute

Restricts code execution strictly to contextual user interactions.

### gmail.readonly

Grants minimum viable compliance access to parse headers and body content without mutation rights.

### urlFetchWhitelist

Strict network whitelisting, permitting outbound API traffic exclusively to the trusted PenguWave gateway domain.

---

# 🚀 Deployment Instructions

## Step 1 – Fire up the Backend & Secure Tunnel

Ensure your FastAPI server is running locally on port `8000`:

```bash
uvicorn app.main:app --reload
```

Expose it through Ngrok:

```bash
ngrok http 8000
```

Copy the generated HTTPS forwarding URL.

---

## Step 2 – Inject Code into Google Apps Script

1. Create a new Google Apps Script project.
2. Copy the contents of `Code.gs`.
3. Update the `API_URL` constant with your Ngrok URL.
4. Enable the manifest file view.
5. Copy the contents of `appsscript.json`.
6. Add your Ngrok domain to `urlFetchWhitelist`.
7. Save the project.

---

## Step 3 – Install and Run in Gmail

1. Click **Deploy → Test deployments**
2. Click **Install**
3. Open Gmail
4. Refresh the page
5. Open any email
6. Launch the PenguWave Add-on

---

## Fallback Behavior

If the backend infrastructure or Ngrok tunnel is unavailable:

* The Add-on does not crash
* Network failures are intercepted gracefully
* Local heuristic simulation is activated
* UI functionality remains operational

---

# 🔮 Future Architecture & Production Roadmap

## Current Implementation — The Ingestion Core

The current architectural blueprint serves as a robust Ingestion Core.

The endpoint sensor parses foundational metadata:

* Sender
* Recipient
* Subject
* Body

The backend normalizes and securely maps this information into the central database.

---

## 1. Extended Data Ingestion Layer

Future iterations will extend analysis beyond raw email text.

### Authentication Headers

* SPF
* DKIM
* DMARC

### Network Traversal Routing

* Hop IP extraction
* Relay path validation
* Origin tracing

### Attachment Artifact Extraction

* SHA-256 hashing
* Malware reputation matching

---

## 2. Multi-Engine Backend Analyzer Pipeline

```text
                  ┌──> [ Layer A: Local Regex / Heuristics Matrix ]
                  │
[ Ingest Payload ]├──> [ Layer B: Secure Local NLP / LLM Semantic Analyzer ]
                  │
                  ├──> [ Layer C: Async Threat Intelligence APIs ]
                  │
                  └──> [ Layer D: File Artifact Sandbox Isolation ]
```

### Layer A – AI / NLP Semantic Inspection

Utilizing dedicated LLM and Transformer-based models to detect:

* Social engineering
* Administrative coercion
* Prompt injection patterns

### Layer B – Threat Intelligence Enrichment

External telemetry sources:

* AbuseIPDB
* VirusTotal
* Urlscan.io

### Layer C – Sandbox Virtualization

Attachment detonation environments:

* Cuckoo Sandbox
* Any.Run

---

## Architectural Scaling Summary

The current `analyze_email` routine establishes the ingestion foundation.

When scaled to production, telemetry from:

* AbuseIPDB
* WHOIS
* Sandbox systems

will be merged asynchronously into a unified Composite Risk Score and surfaced directly within the SOC analyst portal.
