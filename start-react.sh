#!/bin/bash

echo "🚀 Starting RAG React Frontend..."
echo ""

cd "$(dirname "$0")/rag-react"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "✨ Starting development server..."
npm run dev
