#!/bin/bash
echo "🚀 Iniciando Sanaris Pro..."
/home/administrador/sanaris-pro/sanaris/scripts/start_backend.sh > /home/administrador/sanaris-pro/sanaris/logs/backend/uvicorn.log 2>&1 &
BACKEND_PID=$!
sleep 5
/home/administrador/sanaris-pro/sanaris/scripts/start_frontend.sh
trap "kill $BACKEND_PID" EXIT
