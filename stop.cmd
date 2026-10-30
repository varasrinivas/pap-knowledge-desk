@echo off
cd /d "%~dp0" && docker compose stop && echo Stopped. Data is kept; start.cmd brings it back in seconds. && pause
