#!/bin/bash
echo "🔄 REINICIANDO SANARIS PRO..."
pkill -f "uvicorn app.main:app"
pkill -f "next dev"
sleep 3
cd ~/sanaris-pro/sanaris/backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8888 > ~/backend.log 2>&1 &
sleep 5
cd ~/sanaris-pro/sanaris/frontend
rm -f .next/dev/lock
nohup npm run dev > ~/frontend.log 2>&1 &
sleep 5
echo "✅ Backend: http://localhost:8888"
echo "✅ Frontend: http://localhost:3001"
