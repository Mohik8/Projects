# Projects

A portfolio of software projects spanning systems programming, AI, full-stack web, and developer tooling.

---

## Go Task Manager  `Go · Bubble Tea · Lip Gloss`

A fast, keyboard-driven task manager that lives in your terminal. Beautiful TUI that works on any platform without a GUI.

**Highlights**
- Full keyboard navigation (vim-style `j`/`k` supported)
- Three priority levels with live colour coding
- Tag system with instant `/` filter
- Atomic JSON save - write-then-rename prevents corruption
- Tasks stored in `~/.gotask/tasks.json` - survives restarts
- Single binary, zero dependencies at runtime

```bash
cd gotask && go mod tidy
go run .
```

-> [go-task-manager/](go-task-manager/)

---

## F1 Race Strategy Analyzer  `Python · FastF1 · Plotly Dash`

An interactive web dashboard that pulls **live, official Formula 1 timing data** and renders six telemetry-driven views for any race, qualifying session, or practice session from 2018 to 2024.

**Highlights**
- Lap-time chart coloured by tyre compound - exactly like the F1 broadcast overlay
- Cumulative race-gap chart with green/red shaded fill showing who is ahead
- Tyre strategy visualisation: horizontal stacked-bar per driver matching the F1 pit-wall graphic
- 4-panel fastest-lap telemetry trace: Speed / Throttle / Brake / Gear vs Distance
- Full finishing order bar chart colour-coded by constructor
- Air and track temperature with rainfall overlay
- Reactive Dash callbacks - change year, race, session, drivers with zero page reloads
- FastF1 caches session data locally; subsequent loads are instant

```bash
cd f1-race-strategy-analyzer
pip install -r requirements.txt
python app.py
# Open http://localhost:8050
```

-> [f1-race-strategy-analyzer/](f1-race-strategy-analyzer/)

---

## UCrypt - Secure Encryption Web App  `Java Spring Boot · Angular · OWASP ZAP · Selenium`

A full-stack encryption portal where authenticated users can **encrypt and decrypt text and files** using industry-standard ciphers. Worked across the full SDLC including CI/CD setup, automated testing, load testing, and security hardening.

**Highlights**
- Multi-algorithm encryption: **AES-256-GCM**, **Triple DES**, and **Blowfish** - user-selectable per operation
- Eliminated a **path traversal vulnerability** (CWE-22) found during OWASP ZAP security scan
- Replaced insecure CBC mode with **AES/GCM** authenticated encryption to prevent tampering
- Input validation and sanitization applied across all API endpoints
- Role-based access control: admin dashboard for user management, scoped permissions per role
- **CI/CD pipeline** on Azure DevOps - automated build, test, and Docker image push on every commit
- **95+ Selenium/TestNG automated tests** covering login, encryption flows, file upload, and edge cases
- Performance and load testing with Apache JMeter; stress-tested to 200 concurrent users
- SonarQube static analysis integrated into the pipeline - zero critical findings at merge

**Security work**
- Ran OWASP ZAP active scan, triaged findings, patched path traversal + insecure direct object reference
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

-> [ucrypt-web-app/](ucrypt-web-app/)

---

## Neuroevolution Snake AI  `Python · NumPy · Streamlit · Genetic Algorithm`

A genetic algorithm that evolves neural-network weights to play Snake with no backprop, no gradient descent. Each agent is a tiny feedforward net (24 -> 16 -> 16 -> 4); the GA selects, crosses over, and mutates weight vectors until agents learn to chase food and dodge walls.

**Highlights**
- Custom feedforward neural net in pure NumPy - zero ML framework overhead
- 8-direction vision rays (wall / body / food distance) as the 24-dimensional input
- Fitness function: `score^2 * 1000 + steps_survived` - quadratic reward for eating
- Elitism + tournament selection + uniform crossover + Gaussian micro/macro mutations
- Real-time Streamlit dashboard: live fitness curves, per-generation agent preview, animated replay of the champion agent
- Fully configurable sidebar: population size, mutation rate, hidden layer widths, grid size

```bash
cd neuroevolution-snake
pip install -r requirements.txt
streamlit run app.py   # opens http://localhost:8501
```

-> [neuroevolution-snake/](neuroevolution-snake/)

---

## Tech matrix

| Project | Language | Key libs | Domain |
|---|---|---|---|
| Go Task Manager | Go | Bubble Tea, Lip Gloss | CLI / TUI |
| F1 Race Strategy Analyzer | Python | FastF1, Plotly, Dash | Data Vis / Sports Analytics |
| Neuroevolution Snake AI | Python | NumPy, Streamlit, Plotly | AI / Neuroevolution |
| UCrypt Encryption Portal | Java / TypeScript | Spring Boot, Angular, Selenium, OWASP ZAP | Cybersecurity / Full-Stack |
