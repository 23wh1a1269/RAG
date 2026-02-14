#!/bin/bash

# Document Chat App Startup Script
echo "🚀 Starting Document Chat Application..."

# Start Qdrant in Docker
echo "📊 Starting Qdrant database..."
docker rm -f qdrant-db 2>/dev/null || true
docker run -d -p 6333:6333 --name qdrant-db qdrant/qdrant

# Wait for Qdrant to start
echo "⏳ Waiting for Qdrant to initialize..."
sleep 10

# Start FastAPI server
echo "🔧 Starting FastAPI server..."
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Start Inngest dev server
echo "⚡ Starting Inngest dev server..."
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery &

# Start Streamlit app
echo "🎨 Starting Streamlit UI..."
streamlit run streamlit_app.py &

echo "✅ All services started!"
echo "📱 Streamlit UI: http://localhost:8501"
echo "🔧 FastAPI: http://localhost:8000"
echo "📊 Qdrant: http://localhost:6333"

# Keep script running
wait
