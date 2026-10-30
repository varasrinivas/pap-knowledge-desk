#!/usr/bin/env bash
# Removes the containers AND the volumes. The next start rebuilds everything from scratch.
cd "$(dirname "$0")" && docker compose down -v && echo "Reset done. Run ./start.sh to rebuild from scratch."
