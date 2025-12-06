# QA Checklist

## Setup
- [ ] Start Docker environment: `scripts\dev_compose.bat`
- [ ] Run migrations: `docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head`
- [ ] Seed users: `docker-compose -f docker-compose.dev.yml exec backend python app/initial_data.py` (if exists) or manual seed.

## Manual Verification
- [ ] **Login**:
    - Navigate to http://localhost:5173/login
    - Login with admin credentials
    - Verify redirect to Dashboard
- [ ] **Dashboard**:
    - Verify KPI cards show numbers
- [ ] **Vendors**:
    - Create a new vendor
    - Verify it appears in list
- [ ] **Items**:
    - Create a new item
    - Verify it appears in list
- [ ] **CSV Import**:
    - Navigate to Import Items
    - Upload CSV with `commit=false` -> Check preview
    - Upload CSV with `commit=true` -> Check success
- [ ] **Engraving**:
    - Simulate engraving flow (if UI exists)

## Automated Testing
- [ ] **Backend Tests**:
    ```bash
    docker-compose -f docker-compose.dev.yml exec backend pytest
    ```
- [ ] **Frontend Tests**:
    ```bash
    cd frontend
    npm test
    ```
- [ ] **CI Pipeline**:
    - Push changes to GitHub
    - Verify Actions workflow passes
