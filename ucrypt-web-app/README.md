# UCrypt — Secure Encryption Web Application

UCrypt is a full-stack web application that lets authenticated users **encrypt and decrypt text and files** using industry-standard algorithms (AES-256-GCM, Triple DES, Blowfish). It was built as a lab project for **SENG 426 (Software Quality Assurance & Testing)** at UVic, Summer 2025, covering the full software development lifecycle — from CI/CD setup and requirements engineering through automated testing, performance analysis, and hands-on **security hardening**.

The project started as an existing codebase with known weaknesses. Over 5 lab deliverables, security vulnerabilities were identified, assessed, and remediated — treating it the way a real security audit would.

---

## What I Built / Changed

### Cybersecurity Work
- **Discovered and patched a path traversal vulnerability (CWE-22)** — OWASP ZAP active scan flagged it; fixed by sanitizing and canonicalizing all user-supplied file paths server-side
- **Upgraded encryption mode**: replaced insecure AES/CBC (no authentication) with **AES-256-GCM** (authenticated encryption), preventing ciphertext tampering
- **Fixed password storage**: replaced MD5 hashing with **BCrypt** (cost factor 12) — MD5 is fully reversible with rainbow tables
- **Added CSRF token validation** on all state-changing API endpoints
- **Enforced secure cookie flags**: `Secure`, `HttpOnly`, `SameSite=Strict` to prevent session hijacking and XSS cookie theft
- **Input validation & sanitization** added across all API endpoints to block injection attacks
- Ran **SonarQube static analysis** in the CI pipeline — resolved all critical and high severity findings before merge

### Testing
- **95+ Selenium WebDriver / TestNG automated tests** covering login, encryption/decryption flows, file upload, role-based access, and edge cases
- **JMeter load testing**: stress-tested to 200 concurrent users; identified and documented throughput limits
- CI/CD pipeline on **Azure DevOps** — automated build, test run, SonarQube scan, and Docker image push on every commit

### Features
- Multi-algorithm encryption: AES-256-GCM, Triple DES, Blowfish — user-selectable per operation
- Secure file upload and download
- Role-based access control (RBAC): admin dashboard for user management, scoped permissions per role
- Key management system

---

## Project Structure

```
ucrypt-web-app/
├── crypto-back/          # Java Spring Boot backend — encryption services, REST API
├── UCryptPortal/         # Angular frontend — TypeScript, HTML/CSS
├── testing/              # Selenium / TestNG automated test suite
└── azure-pipelines.yml   # CI/CD pipeline (Azure DevOps)
```

---

## Lab Context (SENG 426 — Summer 2025)

| Deliverable | Topic | Weight |
|---|---|---|
| Part 1 | CI/CD Pipeline Setup (Azure DevOps + Docker) | 2% |
| Part 2 | Requirements & Backlog (user stories, acceptance criteria) | 5% |
| Part 3 | Automated Functional Testing (Selenium + TestNG) | 14% |
| Part 4 | Performance & Scalability Testing (JMeter) | 14% |
| Part 5 | Security Testing (OWASP ZAP + remediation) | 10% |

---

## Technologies

| Layer | Stack |
|---|---|
| Backend | Java Spring Boot, Maven, JPA / Hibernate |
| Frontend | Angular, TypeScript, HTML / CSS |
| Testing | Selenium WebDriver, TestNG, Cucumber |
| Security | OWASP ZAP, SonarQube, BCrypt, AES-GCM |
| Deployment | Docker, Azure DevOps |

---

## Screenshots

<img width="1906" height="942" alt="UCrypt dashboard" src="https://github.com/user-attachments/assets/b6c88fb9-c8c4-48d7-a0a3-41a4c91c8211" />
<img width="1906" height="937" alt="UCrypt encryption page" src="https://github.com/user-attachments/assets/fb953d87-c085-4f94-a4f8-a54e34658054" />

---

## Running Locally

```bash
# Backend
cd crypto-back && mvn spring-boot:run

# Frontend (separate terminal)
cd UCryptPortal && npm install && ng serve
# Open http://localhost:4200
```
