#!/bin/bash

echo "🚀 RAG PDF Chat - Quick Start"
echo "=============================="
echo ""

# Check if backend is running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Backend already running on port 8000"
else
    echo "❌ Backend not running. Start it with:"
    echo "   uvicorn main:app --reload"
    echo ""
fi

# Check if frontend is running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Frontend already running on port 3000"
else
    echo "❌ Frontend not running. Start it with:"
    echo "   python3 serve_frontend.py"
    echo ""
fi

echo ""
echo "📍 Access Points:"
echo "   HTML Frontend:      http://localhost:3000"
echo "   Streamlit Frontend: http://localhost:8501"
echo "   Backend API:        http://localhost:8000"
echo ""
echo "📧 Email Configuration:"
if grep -q "SMTP_EMAIL=your-email" .env 2>/dev/null; then
    echo "   ⚠️  Email not configured (optional)"
    echo "   Edit .env to enable email notifications"
else
    echo "   ✅ Email configured"
fi
echo ""
echo "📚 Documentation:"
echo "   Setup Guide:    FRONTEND_SETUP.md"
echo "   Quick Ref:      QUICK_REFERENCE.md"
echo "   Implementation: IMPLEMENTATION.md"
echo ""
