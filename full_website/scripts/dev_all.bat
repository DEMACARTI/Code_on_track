@echo off
echo Starting Backend and Frontend...

start "Backend" cmd /k "cd backend && if exist venv\Scripts\activate (call venv\Scripts\activate) else (echo venv not found, please setup backend first) && uvicorn main:app --reload"
start "Frontend" cmd /k "cd frontend && npm run dev"

echo Servers started in new windows.
