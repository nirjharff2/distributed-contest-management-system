@echo off
title DCMS Launcher v2.0
color 0A
echo.
echo  
echo       DCMS - Contest Management System
echo          v2.0 (Client-Side Execution)
echo 
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found! Please install Python 3.8+
    echo.
    pause
    exit /b 1
)

REM Check/Install dependencies
echo  [1/4] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo  Installing dependencies...
    pip install fastapi uvicorn websockets requests -q
)

REM Setup database
echo  [2/4] Setting up database...
if not exist dcms.db (
    python db_setup.py
) else (
    echo  Database already exists.
)

REM Start server
echo  [3/4] Starting server...
start "DCMS Server" cmd /k "color 0B && title DCMS Server && python main.py"

REM Wait for server
echo  [4/4] Waiting for server to start...
timeout /t 3 /nobreak >nul

echo.
echo  =============================================
echo   Server running at http://127.0.0.1:8000
echo  =============================================
echo.
echo   Choose an option:
echo     1. Open Admin Dashboard
echo     2. Open Client (Participant)
echo     3. Open Both
echo     4. Reset Database
echo     5. Exit
echo.

:menu
choice /c 12345 /n /m "  Enter choice (1-5): "

if errorlevel 5 goto exit
if errorlevel 4 goto reset
if errorlevel 3 goto both
if errorlevel 2 goto client
if errorlevel 1 goto admin

:admin
echo.
echo  Starting Admin Dashboard...
start "DCMS Admin" cmd /k "color 0E && title DCMS Admin && python admin_gui.py"
echo.
echo  Admin Dashboard started!
echo.
goto menu

:client
echo.
echo  Starting Client...
start "DCMS Client" cmd /k "color 0B && title DCMS Client && python client_gui.py"
echo.
echo  Client started!
echo.
goto menu

:both
echo.
echo  Starting Admin Dashboard...
start "DCMS Admin" cmd /k "color 0E && title DCMS Admin && python admin_gui.py"
timeout /t 1 /nobreak >nul
echo  Starting Client...
start "DCMS Client" cmd /k "color 0B && title DCMS Client && python client_gui.py"
echo.
echo  Both applications started!
echo.
goto menu

:reset
echo.
echo  WARNING: This will delete all contest data!
choice /c YN /n /m "  Are you sure? (Y/N): "
if errorlevel 2 goto menu
if errorlevel 1 (
    del dcms.db 2>nul
    echo  Database deleted.
    echo  Recreating database...
    python db_setup.py
    echo  Database reset complete!
)
echo.
goto menu

:exit
echo.
echo  Goodbye!
echo.
exit /b 0