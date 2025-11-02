#!/bin/bash
cd /home/administrador/sanaris-pro/sanaris/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
