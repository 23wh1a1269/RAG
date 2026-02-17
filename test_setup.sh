#!/bin/bash

echo "🔍 Testing RAG Application Setup"
echo "================================"
echo ""

# Test 1: Check if backend is running
echo "1. Checking backend (port 8000)..."
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is NOT running"
    echo "   Start with: uvicorn main:app --reload"
    exit 1
fi

# Test 2: Check if frontend is running
echo "2. Checking frontend (port 3000)..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is NOT running"
    echo "   Start with: python3 serve_frontend.py"
    exit 1
fi

# Test 3: Test signup endpoint
echo "3. Testing signup endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser123","email":"test@example.com","password":"test123"}')

if echo "$RESPONSE" | grep -q "success"; then
    echo "   ✅ Signup endpoint works"
else
    echo "   ❌ Signup endpoint failed"
    echo "   Response: $RESPONSE"
fi

# Test 4: Test login endpoint
echo "4. Testing login endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser123","password":"test123"}')

if echo "$RESPONSE" | grep -q "success"; then
    echo "   ✅ Login endpoint works"
else
    echo "   ❌ Login endpoint failed"
    echo "   Response: $RESPONSE"
fi

echo ""
echo "✅ All tests passed!"
echo ""
echo "📍 Access the app at: http://localhost:3000"
