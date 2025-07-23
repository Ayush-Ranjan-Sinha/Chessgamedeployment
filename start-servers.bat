@echo off
echo Starting TSP Route Optimizer...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Users\Ayush\tsp-route-optimizer\backend && npm start"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d C:\Users\Ayush\tsp-route-optimizer\frontend && npm start"

echo.
echo ===============================================
echo   TSP Route Optimizer is starting up!
echo   Backend:  http://localhost:3001
echo   Frontend: http://localhost:3000
echo ===============================================
echo.
echo Press any key to exit...
pause > nul
