#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║          🎨 RAG React Frontend - Quick Start 🚀           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Project: RAG PDF Chat Application"
echo "🎨 Design: Apple-inspired with Bento Grid + Glassmorphism"
echo "⚡ Tech: React 19 + Vite + TailwindCSS + Framer Motion"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -d "rag-react" ]; then
    echo "❌ Error: rag-react directory not found"
    echo "   Please run this script from /home/user/Downloads/RAG1"
    exit 1
fi

cd rag-react

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    echo ""
    npm install
    echo ""
fi

echo "✅ Dependencies ready!"
echo ""
echo "🚀 Starting React development server..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Frontend URL: http://localhost:5173"
echo "📍 Backend URL:  http://localhost:8000"
echo ""
echo "💡 Make sure the backend is running:"
echo "   cd /home/user/Downloads/RAG1"
echo "   source .venv/bin/activate"
echo "   uvicorn backend.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

npm run dev
