@echo off
echo ============================================
echo   Geni_Electrique — Demarrage Dev
echo ============================================

:: Backend
echo [1/2] Demarrage Backend FastAPI (port 8000)...
start "Backend" cmd /k "cd /d %~dp0backend && uvicorn main:app --reload --port 8000"

:: Attendre 3 secondes
timeout /t 3 /nobreak > nul

:: Frontend
echo [2/2] Demarrage Frontend Vue (port 5173)...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo  Backend  : http://localhost:8000
echo  Frontend : http://localhost:5173
echo  API docs : http://localhost:8000/docs
echo.
pause
