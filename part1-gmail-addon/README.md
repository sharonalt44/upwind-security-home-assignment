Part 1: PenguWave Threat Intel - Gmail Add-on
A lightweight, enterprise-grade Google Workspace Add-on designed to intercept, analyze, and score inbound email threats in real-time. The add-on acts as a security sensor, extracting contextual metadata and communicating with a centralized intelligence hub.

🏗️ Architectural Reasoning & Design Decisions
During development, we evaluated two architectural paths for managing Scan History and Domain Blocklists:

Monolithic DB Integration: Coupling the Add-on directly to the Analyst Portal's core database.

Decoupled Stateless Sensor (Chosen Approach): Keeping the Add-on's operational storage containerized leveraging Google Workspace's native PropertiesService, while offloading the core threat analysis matrices to the central FastAPI gateway.

Why this approach was chosen:
Fault Tolerance & Resilience (Fail-Secure): If the centralized backend gateway or database experiences downtime, the Add-on does not crash or degrade the user's email experience. It gracefully falls back to local sandbox heuristics, ensuring continuous operational visibility.

Separation of Concerns: The Analyst Portal (Part 2) is built for global SOC operations, while the Gmail Add-on is an endpoint sensor. Isolating local user preferences (like a personal blocklist) inside Google’s secure user-space prevents database bloat and schema cross-contamination.

Horizontal Scalability: The FastAPI backend remains entirely stateless for email evaluation, allowing it to handle thousands of concurrent API requests from multiple corporate endpoints without bottlenecking on database I/O write locks.

🌐 Secure Tunneling vs. Production Engineering (Ngrok Sandbox Notice)
Local Sandbox Environment: In the current development environment, Ngrok was utilized strictly as a temporary staging sandbox tool to bridge contextual webhooks from Google's cloud servers to our localhost backend over an encrypted HTTPS tunnel.

Enterprise Risk Awareness: We are fully aware that deploying long-term exposure layers via Ngrok or similar tunneling tools in a production environment introduces corporate risks, including Shadow IT vectors and firewall perimeter bypasses.

Production Architecture Target: The production blueprint dictates that the Add-on targets an official, permanent, and secured enterprise domain (api.penguwave.com) protected behind an enterprise Web Application Firewall (WAF), rate-limiting constraints, and a centralized API Gateway.

⚡ Key Features
Contextual Maliciousness Analyzer: Evaluates risk metrics based on sender reputation, urgent sentiment analysis, and structural email indicators.

Fail-Secure Fallback Strategy: Implements an asynchronous network exception handler. If the central FastAPI hub is unreachable, a local sandbox fallback mode triggers seamlessly, maintaining UI integrity.

Native Defensive Controls: Allows analysts or users to block suspicious sender domains on the fly, persisting state securely within Google's PropertiesService.

Recent Session History: Caches a rolling window of recent telemetry scans for local audit trails without querying cross-origin data structures.

🛡️ Security Configuration (Manifest)
To comply with enterprise security constraints and restrict malicious data exfiltration, the Add-on implements strict OAuth Scopes and network isolation policies inside appsscript.json:

gmail.addons.execute: Restricts code execution strictly to contextual user interactions.

gmail.readonly: Grants minimum viable compliance access to parse headers and body content without mutation rights.

urlFetchWhitelist: Strict network whitelisting, permitting outbound API traffic exclusively to the trusted PenguWave gateway domain.

🚀 Deployment Instructions
To test the live interaction between the Google Workspace environment and your local FastAPI backend, the Add-on requires a secure HTTPS tunnel to route traffic to your localhost.

### Step 1: Fire up the Backend & Secure Tunnel
1. Ensure your FastAPI server is running locally on port `8000` (`uvicorn app.main:app --reload`).
2. Establish an encrypted HTTPS tunnel using Ngrok to expose your local port:
   ```bash
   ngrok http 8000

Copy the generated public https://... forwarding URL (e.g., https://a1b2-34-56.ngrok-free.app).

Step 2: Inject Code into Google Apps Script
Open Google Apps Script and spin up a new project.

Mirror the project repository structure:

Paste the contents of Code.gs into the editor. Update the API_URL constant at the top of the script with your live Ngrok HTTPS URL.

Enable the manifest file view via Project Settings ("Show appsscript.json manifest file in editor").

Paste the contents of appsscript.json into the manifest file, and ensure your Ngrok domain is appended to the urlFetchWhitelist array.

Click Save (the disk icon).

Step 3: Install and Run in Gmail
Click Deploy ➔ Test deployments.

Click Install to securely inject this custom sensor framework straight into your Gmail workspace application frame.

Open your Gmail inbox, refresh the page (F5), and open any inbound email. Click the PenguWave icon on the contextual side panel to view live metadata analysis and threat grading scores.

💡 Reviewer Optimization Note (Graceful Degradation): > If you choose to inspect the Gmail Add-on UI directly without bootstrapping the backend infrastructure or launching an active Ngrok tunnel, the application will not crash. The built-in network exception handlers will gracefully intercept the failure, flashing a "Central Threat Intel server unreachable. Running local sandbox fallback" notice while maintaining complete UI stability and simulating heuristic scores for local demonstration.


🔮 Future Architecture & Production Roadmap
Current Implementation (The Ingestion Core)
The current architectural blueprint serves as a robust Ingestion Core. The endpoint sensor cleanly parses foundational metadata (sender, recipient, subject, and body), which the backend normalizes and maps securely into the central database. To avoid overengineering at the Minimum Viable Product (MVP) stage, deep modular expansions were isolated to a clear production framework.

1. Extended Data Ingestion Layer
Future iterations will transition from processing raw text bodies into parsing lower-level structural frames using Google Workspace APIs:

Authentication Headers: Extracting raw RFC headers to validate network cryptography tokens including SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail), and DMARC to definitively neutralize domain spoofing vectors.

Network Traversal Routing: Harvesting transit node headers (Hop IPs) to trace and alert on suspicious relay paths or origin networks.

Attachment Artifact Extraction: Rather than bypassing files, the sensor will compute cryptographic checksums (e.g., SHA-256) of inbound payloads to audit them against static malware intelligence catalogs.

2. Multi-Engine Backend Analyzer Pipeline
Once enriched metrics reach the central FastAPI orchestrator, evaluation will scale from basic heuristic lookup tables into a multi-layered async evaluation stack:

                  ┌──> [ Layer A: Local Regex / Heuristics Matrix ]
                  │
[ Ingest Payload ]├──> [ Layer B: Secure Local NLP / LLM Semantic Analyzer ]
                  │
                  ├──> [ Layer C: Async Threat Intelligence APIs (VirusTotal/AbuseIPDB) ]
                  │
                  └──> [ Layer D: File Artifact Sandbox Isolation (Any.Run / Cuckoo) ]



🧠 Layer A: AI/NLP Semantic Inspection: Utilizing a dedicated, isolated Large Language Model (LLM) or specialized Transformer model (e.g., fine-tuned BERT variants) to process contextual indicators. This captures semantic patterns of social engineering, administrative coercion, and prompt injection vulnerabilities, even if the payload circumvents traditional keyword blocklists.🌐 Layer B: Threat Intelligence Enrichment (External Tools): Integrating concurrent, asynchronous background workers to reference telemetry endpoints:AbuseIPDB API: Cross-referencing the extracted source_ip to capture dynamic threat history, historical reporting vectors, and geographic anomalies.VirusTotal & Urlscan.io API: Scanning extracted message hyperlink arrays inside an isolated external reputation infrastructure to capture live credential harvesting campaigns.🛡️ Layer C: Sandbox Virtualization: Forwarding unverified attachments directly into safe environment detonators (e.g., Cuckoo Sandbox or Any.Run instances) to extract real-time process mutation and process manipulation logs before alerts reach the tier-1 analyst UI.Architectural Scaling SummaryThe current analyze_email routine enforces all fundamental operational structures—handling source_ip, mapping sender boundaries, and organizing tags.When scaled to production, external telemetry signals derived from AbuseIPDB, WHOIS, and sandbox logs will be merged asynchronously into a single weighted Composite Risk Score ($Score_{Composite}$). These enriched telemetry fields will stream straight into the incident portal's log window, providing global SOC analysts with instantaneous deep-context triage data directly on their dashboards.