#!/usr/bin/env bash
cd "$(dirname "$0")" && docker compose stop && echo "Stopped. Data is kept; ./start.sh brings it back in seconds."
