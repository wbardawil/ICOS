@echo off
REM ICOS Daily Sync - Windows Task Scheduler Script
REM 
REM To schedule this:
REM 1. Open Task Scheduler (taskschd.msc)
REM 2. Create Basic Task > Name: "ICOS Daily Sync"
REM 3. Trigger: Daily at 6:00 AM
REM 4. Action: Start a Program
REM 5. Program: This batch file path
REM 6. Start in: The folder containing daily_sync.py

cd /d "%~dp0"
python daily_sync.py >> sync_log.txt 2>&1
