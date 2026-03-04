# Projects

A portfolio of software projects spanning systems programming, AI, full-stack web, and CLI tooling.

---

## 🔐 Encrypted Password Manager  `C · OpenSSL`

A command-line password manager that encrypts your credentials with **AES-256-GCM** authenticated encryption and **PBKDF2-HMAC-SHA256** key derivation — the same primitives used by industry-grade tools.

**Highlights**
- AES-256-GCM: any tampering with the vault file is detected before decryption
- 200 000 PBKDF2 iterations slow down brute-force attacks
- Cryptographically random password generator
- Key material is zeroed from memory after every operation
- Single portable binary file (~50 KB), no runtime dependencies beyond OpenSSL

```bash
cd securevault && make
./securevault new my.vault
./securevault add my.vault
./securevault gen 32
```

→ [encrypted-password-manager/](encrypted-password-manager/)

---

## 🤖 AI Document Assistant  `Python · LangChain · ChromaDB · Ollama`

A fully **local** RAG (Retrieval-Augmented Generation) AI assistant. Load any PDF or text file, then have a natural conversation about it — no API keys, no cloud, no data leaving your machine.

**Highlights**
- Chunking + embedding pipeline via `nomic-embed-text` (Ollama)
- ChromaDB persistent vector store — survives restarts
- Conversation history — follow-up questions work naturally
- Source attribution — shows which document page each answer came from
- Swap models with `/model mistral` mid-conversation
- 100% offline after initial model pull

```bash
cd docuchat && pip install -r requirements.txt
ollama pull llama3 && ollama pull nomic-embed-text
python app.py
# > /load ./report.pdf
# > What were the key findings?
```

→ [ai-document-assistant/](ai-document-assistant/)

---

## ✅ Go Task Manager  `Go · Bubble Tea · Lip Gloss`

A fast, keyboard-driven task manager that lives in your terminal. Beautiful TUI that works on any platform without a GUI.

**Highlights**
- Full keyboard navigation (vim-style `j`/`k` supported)
- Three priority levels with live colour coding
- Tag system with instant `/` filter
- Atomic JSON save — write-then-rename prevents corruption
- Tasks stored in `~/.gotask/tasks.json` — survives restarts
- Single binary, zero dependencies at runtime

```bash
cd gotask && go mod tidy
go run .
```

→ [go-task-manager/](go-task-manager/)

---

## 🏎️ F1 Race Strategy Analyzer  `Python · FastF1 · Plotly Dash`

An interactive web dashboard that pulls **live, official Formula 1 timing data** and renders six telemetry-driven views for any race, qualifying session, or practice session from 2018 – 2024.

**Highlights**
- Lap-time chart coloured by tyre compound – exactly like the F1 broadcast overlay
- Cumulative race-gap chart with green/red shaded fill showing who is ahead
- Tyre strategy visualisation: horizontal stacked-bar per driver matching the F1 pit-wall graphic
- 4-panel fastest-lap telemetry trace: Speed / Throttle / Brake / Gear vs Distance
- Full finishing order bar chart colour-coded by constructor
- Air & track temperature with rainfall overlay
- Reactive Dash callbacks — change year → race → session → drivers with zero page reloads
- FastF1 caches session data locally; subsequent loads are instant

```bash
cd f1-race-strategy-analyzer
pip install -r requirements.txt
python app.py
# Open http://localhost:8050
```

→ [f1-race-strategy-analyzer/](f1-race-strategy-analyzer/)

---

## 🔒 UCrypt — Secure Encryption Web App  `Java Spring Boot · Angular · OWASP ZAP · Selenium`

A full-stack encryption portal where authenticated users can **encrypt and decrypt text and files** using industry-standard ciphers. Built as part of a rigorous software engineering course (SENG 426) covering the full SDLC — from requirements through security hardening.

**Highlights**
- Multi-algorithm encryption: **AES-256-GCM**, **Triple DES**, and **Blowfish** — user-selectable per operation
- Eliminated a **path traversal vulnerability** (CWE-22) found during OWASP ZAP security scan
- Replaced insecure CBC mode with **AES/GCM** authenticated encryption to prevent tampering
- Input validation and sanitization applied across all API endpoints
- Role-based access control: admin dashboard for user management, scoped permissions per role
- **CI/CD pipeline** on Azure DevOps — automated build, test, and Docker image push on every commit
- **95+ Selenium/TestNG automated tests** covering login, encryption flows, file upload, and edge cases
- Performance & load testing with Apache JMeter; stress-tested to 200 concurrent users
- SonarQube static analysis integrated into the pipeline — zero critical findings at merge

**Security work specifically**
- Ran OWASP ZAP active scan → triaged findings → patched path traversal + insecure direct object reference
- Replaced MD5 password hashing with BCrypt (cost factor 12)
- Added CSRF token validation on all state-changing endpoints
- Enforced HTTPS-only cookies (`Secure`, `HttpOnly`, `SameSite=Strict`)

```bash
# Backend
cd ucrypt-web-app/crypto-back && mvn spring-boot:run

# Frontend
cd ucrypt-web-app/UCryptPortal && npm install && ng serve
# Open http://localhost:4200
```

→ [ucrypt-web-app/](ucrypt-web-app/)


---

## ?? Neuroevolution Snake AI  `Python � NumPy � Streamlit � Genetic Algorithm`

A genetic algorithm that evolves neural-network weights to play Snake � **no backprop, no gradient descent**. Each agent is a tiny feedforward net (24 ? 16 ? 16 ? 4); the GA selects, crosses over, and mutates weight vectors until agents learn to chase food and dodge walls.

**Highlights**
- Custom feedforward neural net in pure NumPy � zero ML framework overhead
- 8-direction vision rays (wall / body / food distance) as the 24-dimensional input
- Fitness function: `score� � 1000 + steps_survived` � quadratic reward for eating
- Elitism + tournament selection + uniform crossover + Gaussian micro/macro mutations
- Real-time Streamlit dashboard: live fitness curves, per-generation agent preview, animated replay of the champion agent
- Fully configurable sidebar: population size, mutation rate/s, hidden layer widths, grid size

```bash
cd neuroevolution-snake
pip install -r requirements.txt
streamlit run app.py   # opens http://localhost:8501
```

? [neuroevolution-snake/](neuroevolution-snake/)
---

## Tech matrix

| Project | Language | Key libs | Domain |
|---|---|---|---|
| Encrypted Password Manager | C | OpenSSL | Security / Systems |
| AI Document Assistant | Python | LangChain, ChromaDB, Ollama | AI / NLP |
| Go Task Manager | Go | Bubble Tea, Lip Gloss | CLI / TUI |
| F1 Race Strategy Analyzer | Python | FastF1, Plotly, Dash | Data Vis / Sports Analytics |
| Neuroevolution Snake AI | Python | NumPy, Streamlit, Plotly | AI / Neuroevolution |
| UCrypt Encryption Portal | Java / TypeScript | Spring Boot, Angular, Selenium, OWASP ZAP | Cybersecurity / Full-Stack |
