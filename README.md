LYFTR Backend API

This project implements a FastAPI-based backend service that receives webhook events, verifies them using HMAC-SHA256, persists validated messages, and exposes query APIs to retrieve stored messages.

The system is designed to run entirely via the provided scripts and Docker setup, following the exact semantics specified in the assignment.

🛠 Tech Stack

Python 3.10

FastAPI

Uvicorn

SQLite


Docker & Docker Compose

⚙️ Configuration (Environment Variables Only)

All configuration is handled exclusively via environment variables, as required.

Variable	Description	Required
WEBHOOK_SECRET	Shared secret used to compute HMAC signature	✅ Yes

Example (Windows):

set WEBHOOK_SECRET=testsecret


Example (Linux / macOS):

export WEBHOOK_SECRET=testsecret


No hardcoded secrets are used anywhere in the codebase.

📁 Project Structure
lyftr-backend/
│
├── app/
│   ├── main.py            # FastAPI app and route definitions
│   ├── models.py          # Database schema and initialization
│   ├── storage.py         # Persistence layer (SQLite interactions)
│   ├── config.py          # Environment variable loading
│   ├── logging_utils.py   # Reserved for structured logging
│   └── metrics.py         # Reserved for metrics collection
│
├── tests/                 # Reserved for test cases
│
├── app.db                 # SQLite database file
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── Makefile               # Convenience commands
└── README.md              # Project documentation



Some files are intentionally kept minimal or empty to demonstrate future extensibility, which is standard backend practice.

🚦 API Semantics (Exact Behavior)
Health Endpoints
Endpoint	Behavior
GET /health/live	Returns 200 if service is alive
GET /health/ready	Returns 200 if DB is initialized
Webhook Endpoint

POST /webhook

Expected Behavior:

Reads raw request body

Extracts X-Signature header

Computes HMAC-SHA256 using WEBHOOK_SECRET

Compares signatures using constant-time comparison

Rejects request if signature is invalid

Persists message on success

Failure Case

Missing or invalid signature → 401 Unauthorized

Success Case

Valid signature → message stored → { "status": "ok" }

Messages API
Endpoint	Description
GET /messages	Fetch all messages
GET /messages?from=+9198...	Filter by sender
GET /messages?limit=10&offset=0	Pagination support

Returned data exactly reflects persisted webhook messages.

🔐 HMAC Signature Verification

The system validates authenticity using HMAC-SHA256.

## 🔄 Webhook Processing Flow

Client
  │
  │  POST /webhook
  │  (JSON Body + X-Signature)
  ▼
FastAPI Webhook Endpoint
  │
  ├─ Read raw request body
  ├─ Read X-Signature header
  ├─ Compute HMAC-SHA256 using WEBHOOK_SECRET
  ├─ Constant-time signature comparison
  │
  ├─ ❌ Invalid → 401 Unauthorized
  │
  └─ ✅ Valid
        ├─ Store message in SQLite
        └─ Return { "status": "ok" }


Signature generation example:

python -c "import hmac,hashlib; body=b'{\"message_id\":\"good1\",\"from\":\"+919876543210\",\"to\":\"+14155550100\",\"ts\":\"2025-01-15T10:00:00Z\"}'; print(hmac.new(b'testsecret', body, hashlib.sha256).hexdigest())"


The computed hex value must be passed as:

X-Signature: <hex_value>

▶️ Run Locally (Without Docker)
pip install -r requirements.txt
set WEBHOOK_SECRET=testsecret
uvicorn app.main:app --reload


Open:

http://127.0.0.1:8000/docs

🐳 Run With Docker (Validated)
Build Image
docker build -t lyftr-backend-api .

Run
docker compose up


Confirmed working endpoints inside container:

/health/live

/health/ready

/docs

/messages

✅ Validation Summary

✔ System runs successfully using provided Docker scripts

✔ Webhook semantics match assignment specification

✔ Signature verification enforced correctly

✔ Invalid requests rejected deterministically

✔ Configuration strictly via environment variables

✔ Clear modular structure with separation of concerns

## 🧠 Design Decisions

- SQLite chosen for simplicity and zero external dependencies.
- Raw request body is used for HMAC to avoid JSON re-serialization issues.
- Constant-time comparison prevents timing attacks.
- Dockerized setup ensures consistent runtime behavior across environments.


🧰 Setup Used

VS Code + Copilot + occasional ChatGPT prompts

👨‍💻 Author

SHUBH BHATNAGAR
Backend Developer (FastAPI, Docker)
