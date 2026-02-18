#!/bin/bash
# Complete startup script - run backend and frontend

echo "🚀 Starting RAG PDF Chat Application"
echo ""

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Run: cp .env.example .env"
    echo "   Then edit .env and add GROQ_API_KEY"
    exit 1
fi

# Check Qdrant
if ! curl -s http://localhost:6333 > /dev/null 2>&1; then
    echo "⚠️  Qdrant not running on localhost:6333"
    echo "   Start it with: docker run -d -p 6333:6333 qdrant/qdrant"
    echo ""
fi

# Activate venv if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Start backend in background
echo "📦 Starting backend on http://localhost:8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "❌ Backend failed to start. Check backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend running"
echo ""
echo "🌐 Starting frontend on http://localhost:3000..."
cd frontend
python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"

sleep 2
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Application started successfully!"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop both services..."

# Wait for interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
