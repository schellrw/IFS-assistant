@echo off
echo Starting IFS Assistant Application...

echo Starting Backend Server...
start cmd /k "cd /d %~dp0 && .\.venv\Scripts\Activate.ps1 && python direct_pg_run.py"

echo Starting Frontend Server...
start cmd /k "cd /d %~dp0\frontend && npm start"

echo Both servers are starting. Please wait...
echo Backend will be available at http://localhost:5000
echo Frontend will be available at http://localhost:3000 