# Database Connection Established

## Connection Status
- **Backend Verified**: The backend is successfully connected to the PostgreSQL database at `127.0.0.1:5432/qrtrack`.
- **Tables Verified**: `items` table exists and contains ~125 records.
- **Configuration**: Using credentials from `full_website/.env`.

## How to Run
I have created a startup script to easily launch both the backend and frontend.

1.  **Run the script**:
    ```powershell
    .\start_app.ps1
    ```
    This will open two new PowerShell windows:
    - One for the **Backend** (FastAPI) running on default port `8000`.
    - One for the **Frontend** (Vite) running on a free port (usually `5173`).

2.  **Access the Website**:
    - Open your browser to the URL shown in the Frontend window (e.g., `http://localhost:5173`).
    - The frontend is configured to communicate with `http://localhost:8000` (Backend).

## Troubleshooting
- If the backend fails to start, ensure you have Python installed and the virtual environment (`backend/venv`) is valid.
- If the frontend fails, ensure `npm install` has been run in `frontend/`.
