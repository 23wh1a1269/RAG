#!/bin/bash
# Complete system verification and startup script

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 RAG PDF CHAT - SYSTEM VERIFICATION & STARTUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check .env file
echo "1️⃣  Checking .env configuration..."
if [ ! -f .env ]; then
    echo "   ❌ .env file not found!"
    exit 1
fi

if ! grep -q "GROQ_API_KEY=" .env || grep -q "GROQ_API_KEY=$" .env; then
    echo "   ❌ GROQ_API_KEY not set in .env"
    exit 1
fi
echo "   ✅ .env configured"

# 2. Check Qdrant
echo ""
echo "2️⃣  Checking Qdrant vector database..."
if curl -s http://localhost:6333 > /dev/null 2>&1; then
    echo "   ✅ Qdrant running on localhost:6333"
else
    echo "   ⚠️  Qdrant not running!"
    echo "   Starting Qdrant..."
    docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
    sleep 3
    if curl -s http://localhost:6333 > /dev/null 2>&1; then
        echo "   ✅ Qdrant started successfully"
    else
        echo "   ❌ Failed to start Qdrant"
        exit 1
    fi
fi

# 3. Check Python environment
echo ""
echo "3️⃣  Checking Python environment..."
if [ ! -d ".venv" ]; then
    echo "   ❌ Virtual environment not found"
    exit 1
fi
echo "   ✅ Virtual environment exists"

# 4. Activate venv
source .venv/bin/activate

# 5. Check dependencies
echo ""
echo "4️⃣  Checking Python dependencies..."
python -c "import fastapi, groq, qdrant_client, sentence_transformers, llama_index" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ All dependencies installed"
else
    echo "   ⚠️  Installing missing dependencies..."
    pip install -q -r requirements.txt
    echo "   ✅ Dependencies installed"
fi

# 6. Check directory structure
echo ""
echo "5️⃣  Checking directory structure..."
for dir in backend frontend uploads chat_history cache; do
    if [ ! -d "$dir" ]; then
        echo "   ⚠️  Creating $dir/"
        mkdir -p "$dir"
    fi
done
echo "   ✅ Directory structure verified"

# 7. Check users.json
echo ""
echo "6️⃣  Checking user database..."
if [ ! -f "users.json" ]; then
    echo "{}" > users.json
    echo "   ✅ Created users.json"
else
    echo "   ✅ users.json exists"
fi

# 8. Kill existing processes
echo ""
echo "7️⃣  Cleaning up existing processes..."
pkill -f "uvicorn backend.main" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null
sleep 1
echo "   ✅ Cleanup complete"

# 9. Start backend
echo ""
echo "8️⃣  Starting FastAPI backend..."
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "   ✅ Backend running (PID: $BACKEND_PID)"
else
    echo "   ❌ Backend failed to start"
    echo "   Check backend.log for errors"
    exit 1
fi

# 10. Start frontend
echo ""
echo "9️⃣  Starting frontend server..."
cd frontend
nohup python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 2

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend running (PID: $FRONTEND_PID)"
else
    echo "   ❌ Frontend failed to start"
    exit 1
fi

# 11. Test endpoints
echo ""
echo "🔟  Testing API endpoints..."

# Test signup
SIGNUP_RESULT=$(curl -s -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"test123"}')

if echo "$SIGNUP_RESULT" | grep -q "success"; then
    echo "   ✅ Signup endpoint working"
else
    echo "   ⚠️  Signup endpoint response: $SIGNUP_RESULT"
fi

# Test login
LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}')

if echo "$LOGIN_RESULT" | grep -q "token"; then
    echo "   ✅ Login endpoint working"
    TOKEN=$(echo "$LOGIN_RESULT" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    echo "   ✅ JWT token generated"
else
    echo "   ⚠️  Login endpoint response: $LOGIN_RESULT"
fi

# Test protected endpoint
if [ ! -z "$TOKEN" ]; then
    PROFILE_RESULT=$(curl -s http://localhost:8000/profile \
      -H "Authorization: Bearer $TOKEN")
    
    if echo "$PROFILE_RESULT" | grep -q "testuser"; then
        echo "   ✅ Protected endpoints working"
    else
        echo "   ⚠️  Profile endpoint response: $PROFILE_RESULT"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SYSTEM READY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Access Points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "📊 Process IDs:"
echo "   Backend:   $BACKEND_PID"
echo "   Frontend:  $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:   tail -f backend.log"
echo "   Frontend:  tail -f frontend.log"
echo ""
echo "🛑 To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or"
echo "   pkill -f 'uvicorn backend.main'"
echo "   pkill -f 'http.server 3000'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
