#!/bin/bash
# Start the FastAPI backend server with Uvicorn (development mode)

cd "$(dirname "$0")/.."  # Go to backend root

if [ -d "venv" ]; then
  source venv/bin/activate
fi

exec uvicorn src.app:app --reload --port 8088
