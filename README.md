# IRF QR Tracking System

A full-stack web application for tracking IRF QR codes.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: React, Vite, Tailwind CSS
- **Database**: PostgreSQL with JSONB support

## Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL

### Setup

1.  Clone the repository.
2.  Copy `.env.example` to `.env` and configure your environment variables.

### Running Locally

You can run both the backend and frontend using the provided script (Windows):

```batch
.\scripts\dev_all.bat
```

Or run them individually:

**Backend:**

```bash
cd backend
# Create and activate venv
python -m venv venv
.\venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Run server
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## 🚀 Local Development with Docker

To run the complete development stack (Postgres + Backend + Frontend):

### 1. Start Dev Stack
```batch
scripts\dev_compose.bat
```

### 2. Access Services
Backend: http://localhost:8000  
Frontend: http://localhost:5173  

### 3. Stop Dev Stack
```bash
docker-compose -f docker-compose.dev.yml down
```

This setup uses volume mounts so backend/frontend source code updates reflect instantly inside the running containers.

---
