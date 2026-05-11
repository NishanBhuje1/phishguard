# PhishGuard — Project Reference Document

> This file is the single source of truth for the PhishGuard project.
> Start every AI session with: "Follow the architecture defined in PROJECT.md"

---

## Project Summary

**Name:** PhishGuard  
**Type:** URL Phishing Detection System  
**Purpose:** Analyze URLs and classify them as safe, suspicious, or phishing using machine learning and heuristic analysis  
**Assessment:** ICT306 Advanced Cybersecurity — Assessment 3  
**Framework:** Secure Software Development Lifecycle (SSDLC)  

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Tailwind CSS + Axios |
| Backend | Python + FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy |
| Auth | bcrypt + JWT (python-jose) + TOTP (pyotp) |
| ML Model | scikit-learn Random Forest |
| Rate Limiting | slowapi |
| Security Testing | Bandit (SAST) + OWASP ZAP (DAST) |
| External API | PhishTank (known phishing domain lookup) |

---

## Folder Structure

```
phishguard/
├── PROJECT.md                      ← this file
├── README.md
├── .env                            ← environment variables (never commit)
├── .env.example                    ← template for .env
│
├── backend/
│   ├── main.py                     ← FastAPI app entry point
│   ├── config.py                   ← loads env vars, app settings
│   ├── database.py                 ← SQLite connection, table creation
│   │
│   ├── models/
│   │   ├── user.py                 ← User SQLAlchemy model
│   │   └── scan.py                 ← Scan result SQLAlchemy model
│   │
│   ├── routers/
│   │   ├── auth.py                 ← /auth/register /auth/login /auth/verify-2fa
│   │   ├── scan.py                 ← /scan (POST - analyze a URL)
│   │   └── admin.py                ← /admin/scans /admin/users
│   │
│   ├── services/
│   │   ├── auth_service.py         ← bcrypt hashing, JWT creation/validation, TOTP
│   │   ├── url_analyzer.py         ← URL feature extraction (9 features)
│   │   ├── ml_classifier.py        ← loads model.pkl, runs prediction
│   │   └── logger.py               ← structured audit logging
│   │
│   ├── middleware/
│   │   └── rate_limiter.py         ← slowapi: 10 req/min per IP on /scan
│   │
│   ├── ml/
│   │   ├── train.py                ← one-time training script
│   │   ├── model.pkl               ← saved trained Random Forest model
│   │   └── dataset.csv             ← UCI phishing dataset (11,000 labeled URLs)
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx           ← email + password + TOTP code
│   │   │   ├── Scanner.jsx         ← URL input + ResultCard
│   │   │   └── AdminDashboard.jsx  ← scan history table (admin only)
│   │   ├── components/
│   │   │   ├── ResultCard.jsx      ← safe/suspicious/phishing verdict display
│   │   │   └── ScanHistory.jsx     ← paginated table of past scans
│   │   └── services/
│   │       └── api.js              ← all axios calls to backend
│   └── package.json
│
└── docs/
    ├── architecture.png            ← system diagram for report
    ├── threat_model.md             ← STRIDE analysis
    ├── bandit_report.txt           ← SAST output
    └── zap_report.html             ← DAST output
```

---

## Database Schema

### users table
```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,        -- bcrypt hash, never plain text
    totp_secret   TEXT NOT NULL,        -- pyotp secret for Google Authenticator
    role          TEXT DEFAULT 'user',  -- 'user' or 'admin'
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### scans table
```sql
CREATE TABLE scans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    url_hash    TEXT NOT NULL,      -- SHA256 of original URL (privacy by design)
    verdict     TEXT NOT NULL,      -- 'safe' | 'suspicious' | 'phishing'
    confidence  REAL NOT NULL,      -- 0.0 to 1.0 from ML model
    ip_hash     TEXT NOT NULL,      -- SHA256 of requester IP
    scanned_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

### Auth
| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | /auth/register | No | Register new user, returns TOTP secret |
| POST | /auth/login | No | Login with email + password, returns temp token |
| POST | /auth/verify-2fa | Temp token | Submit TOTP code, returns full JWT |

### Scan
| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | /scan | JWT (user or admin) | Analyze a URL, returns verdict + confidence |
| GET | /scan/history | JWT (user) | Get current user's scan history |

### Admin
| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /admin/scans | JWT (admin only) | Get all scans across all users |
| GET | /admin/users | JWT (admin only) | Get all registered users |

### Health
| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /health | No | Returns {"status": "ok"} |

---

## URL Features Extracted (url_analyzer.py)

These 9 features are extracted from every URL and fed into the ML model:

| Feature | Description | Phishing Signal |
|---|---|---|
| url_length | Total character length of URL | > 75 chars = suspicious |
| special_char_count | Count of @ . - _ ? = & % | High count = suspicious |
| subdomain_count | Number of subdomains | > 3 = suspicious |
| has_ip_address | IP instead of domain name | True = strong phishing signal |
| suspicious_tld | TLD in risk list | True = suspicious |
| has_brand_typo | Lookalike brand keywords | True = strong phishing signal |
| is_url_shortener | Known shortener service | True = suspicious |
| path_depth | Number of / in URL path | > 5 = suspicious |
| phishtank_match | Found in PhishTank database | True = confirmed phishing |

### Suspicious TLD List
`.xyz .tk .ml .ga .cf .gq .pw .top .click .link`

### Brand Typo Keywords
`paypa1, g00gle, arnazon, micosoft, app1e, faceb00k, netfl1x`

### URL Shortener Domains
`bit.ly, tinyurl.com, t.co, goo.gl, ow.ly, short.io, rb.gy`

---

## ML Model

**Algorithm:** Random Forest Classifier (scikit-learn)  
**Dataset:** UCI Machine Learning Repository — Phishing Websites Dataset  
**Size:** ~11,000 labeled URLs (phishing and legitimate)  
**Expected Accuracy:** 94–97% on test split  
**Output:** verdict (safe/suspicious/phishing) + confidence score (0.0–1.0)  
**Saved as:** `backend/ml/model.pkl` using joblib  

### Verdict Thresholds
- `confidence >= 0.75` → phishing
- `confidence >= 0.45` → suspicious
- `confidence < 0.45` → safe

---

## Security Controls

### Authentication
- Passwords hashed with **bcrypt** (cost factor 12)
- Sessions managed via **JWT** (HS256, 24hr expiry)
- Two-factor auth via **TOTP** (pyotp, Google Authenticator compatible)
- JWT secret loaded from environment variable — never hardcoded

### Authorization (RBAC)
- Role `user`: can submit URLs, view own scan history
- Role `admin`: can view all scans, all users
- RBAC enforced at API level, not just UI level

### Rate Limiting
- `/scan` endpoint: **10 requests per minute per IP**
- Returns HTTP 429 when exceeded
- Implemented via `slowapi` middleware

### Input Validation
- All URLs validated before processing
- Rejects: empty strings, non-URL strings, URLs > 2048 chars
- Returns HTTP 400 for invalid input

### Audit Logging
- Every scan logged: timestamp, hashed IP, hashed URL, verdict
- Raw URLs and IPs never stored (privacy by design)
- Logs written to scans table and optionally to file

### Secrets Management
- All secrets in `.env` file
- `.env` in `.gitignore` — never committed
- `.env.example` committed as template

---

## Environment Variables

```env
# .env.example — copy to .env and fill in values

SECRET_KEY=your-jwt-secret-key-here-make-it-long-and-random
DATABASE_URL=sqlite:///./phishguard.db
PHISHTANK_API_KEY=your-phishtank-api-key-here
ENVIRONMENT=development
ACCESS_TOKEN_EXPIRE_MINUTES=1440
RATE_LIMIT_PER_MINUTE=10
```

---

## Backend Dependencies (requirements.txt)

```
fastapi==0.111.0
uvicorn==0.29.0
sqlalchemy==2.0.30
bcrypt==4.1.3
python-jose[cryptography]==3.3.0
pyotp==2.9.0
slowapi==0.1.9
scikit-learn==1.4.2
pandas==2.2.2
joblib==1.4.2
requests==2.31.0
python-dotenv==1.0.1
python-multipart==0.0.9
```

---

## Frontend Dependencies (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.23.1",
    "axios": "^1.6.8",
    "tailwindcss": "^3.4.3"
  }
}
```

---

## Data Flow

```
User submits URL via React frontend
        │
        ▼
POST /scan with JWT token in Authorization header
        │
        ▼
Rate limiter checks IP ──── over limit? ──► 429 Too Many Requests
        │
        ▼
JWT validated ───────────── invalid/expired? ► 401 Unauthorized
        │
        ▼
Input validation ────────── malformed URL? ──► 400 Bad Request
        │
        ▼
url_analyzer.py extracts 9 features from URL
        │
        ▼
PhishTank API checked for known bad domain
        │
        ▼
ml_classifier.py runs Random Forest prediction
  → returns verdict + confidence score
        │
        ▼
Audit log written to scans table
  (timestamp, hashed IP, hashed URL, verdict)
        │
        ▼
Response returned: { verdict, confidence, features }
        │
        ▼
ResultCard renders result in React UI
```

---

## Build Order (Session by Session)

| Session | What to Build | Verify By |
|---|---|---|
| 1 | Project scaffold + FastAPI health check | GET /health returns {"status":"ok"} |
| 2 | SQLite setup + register + login + JWT | Register user via /docs, get JWT back |
| 3 | TOTP 2FA + rate limiting | Login requires TOTP code; 429 after 10 req/min |
| 4 | URL feature extractor | Print feature dict for 3 test URLs |
| 5 | ML model training | Accuracy printed > 94%, model.pkl saved |
| 6 | Scan endpoint (full pipeline) | Submit phishing URL via /docs, get verdict |
| 7 | React frontend | Login → scan URL → see ResultCard |
| 8 | Security testing | bandit_report.txt + ZAP results saved to docs/ |

---

## STRIDE Threat Model Summary

| Threat | Component | Mitigation |
|---|---|---|
| Spoofing | Login endpoint | bcrypt + TOTP 2FA |
| Tampering | Scan results | JWT validation, server-side processing only |
| Repudiation | All actions | Audit log in scans table |
| Information Disclosure | URL data | URL and IP stored as SHA256 hashes only |
| Denial of Service | /scan endpoint | Rate limiting (10 req/min per IP) |
| Elevation of Privilege | Admin endpoints | RBAC enforced at API level |

---

## SSDLC Phase Mapping

| SSDLC Phase | What Was Done |
|---|---|
| Phase 1: Security Requirements | CIA triad defined, stakeholders identified, acceptance criteria set |
| Phase 2: Threat Modeling | Architecture diagram created, STRIDE applied to all components |
| Phase 3: Secure Design | Least privilege (RBAC), defense in depth (auth + rate limit + validation), fail-secure defaults |
| Phase 4: Secure Implementation | OWASP guidelines followed, bcrypt, JWT, TOTP, input validation, parameterized queries |
| Phase 5: Security Testing | Bandit SAST, OWASP ZAP DAST, manual pen testing on auth and scan endpoints |
| Phase 6: Secure Deployment | TLS, env vars for secrets, debug mode off, dependency versions pinned |
| Phase 7: Maintenance & Monitoring | Structured audit logging, vulnerability disclosure plan, patch management plan |

---

## Advanced Security Features Implemented

- ✅ **Rate Limiting & DoS Protection** — slowapi middleware on /scan endpoint
- ✅ **Secure Login with RBAC + 2FA** — bcrypt + JWT + pyotp TOTP
- ✅ **ML-based Phishing Classification** — Random Forest trained on UCI dataset

---

## Key Rules for All AI Sessions

1. Always follow this PROJECT.md — do not deviate from the folder structure or schema
2. Never hardcode secrets — always use environment variables from config.py
3. Never store raw URLs or IPs — always hash with SHA256 before storing
4. JWT secret must come from SECRET_KEY env var
5. Passwords must always be hashed with bcrypt — never stored plain
6. Rate limiting must be applied before any processing logic
7. Input validation must happen before feature extraction
8. RBAC must be enforced at the router level, not just the frontend
