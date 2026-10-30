@echo off
rem Removes the containers AND the volumes (Chroma collections, ServiceNow data, profile, drafts). The next start rebuilds everything.
cd /d "%~dp0" && docker compose down -v && echo Reset done. Run start.cmd to rebuild from scratch. && pause
