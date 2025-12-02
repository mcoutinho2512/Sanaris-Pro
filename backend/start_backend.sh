#!/bin/bash
cd /home/sanaris/sanaris-pro/backend
source venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8888 --workers 4
