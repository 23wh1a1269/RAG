from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from llama_index.core import Document
from llama_index.readers.file import PDFReader
from sentence_transformers import SentenceTransformer
from groq import Groq
import uuid
import tempfile
from inngest import Inngest, TriggerEvent

load_dotenv()

app = FastAPI()
inngest_client = Inngest(app_id="document-chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Create collection if it doesn't exist
collection_name = "documents"
try:
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
except:
    pass

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

@inngest_client.create_function(
    fn_id="process-document",
    trigger=TriggerEvent(event="document/uploaded")
)
async def process_document(ctx, step):
    file_path = ctx.event.data["file_path"]
    filename = ctx.event.data["filename"]
    
    # Read PDF
    reader = PDFReader()
    documents = reader.load_data(file_path)
    
    # Process chunks
    points = []
    for i, doc in enumerate(documents):
        text = doc.text
        chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
        
        for j, chunk in enumerate(chunks):
            if len(chunk.strip()) > 50:
                embedding = embedding_model.encode(chunk)
                point_id = str(uuid.uuid4())
                
                points.append(PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk,
                        "filename": filename,
                        "page": i + 1,
                        "chunk": j + 1
                    }
                ))
    
    # Store in Qdrant
    if points:
        qdrant_client.upsert(collection_name=collection_name, points=points)
    
    # Clean up
    os.unlink(file_path)
    
    return {"processed_chunks": len(points)}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    # Process document directly instead of using Inngest for now
    try:
        result = await process_document_sync(tmp_file_path, file.filename)
        return {"message": f"Document {file.filename} uploaded and processed successfully", "chunks": result["processed_chunks"]}
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

async def process_document_sync(file_path: str, filename: str):
    """Process document synchronously"""
    # Read PDF
    reader = PDFReader()
    documents = reader.load_data(file_path)
    
    # Extract text and create chunks with page tracking
    text_chunks = []
    for page_num, doc in enumerate(documents):
        # Split text into chunks
        text = doc.text
        chunk_size = 1000
        overlap = 200
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                text_chunks.append({
                    "text": chunk,
                    "page": page_num + 1  # 1-indexed page numbers
                })
    
    # Create embeddings
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedding_model.encode([chunk["text"] for chunk in text_chunks])
    
    # Create points for Qdrant
    points = []
    for i, (chunk_data, embedding) in enumerate(zip(text_chunks, embeddings)):
        points.append({
            "id": str(uuid.uuid4()),
            "vector": embedding.tolist(),
            "payload": {
                "text": chunk_data["text"],
                "filename": filename,
                "chunk_id": i,
                "page": chunk_data["page"]
            }
        })
    
    # Store in Qdrant
    collection_name = "documents"
    if points:
        qdrant_client.upsert(collection_name=collection_name, points=points)
    
    # Clean up
    os.unlink(file_path)
    
    return {"processed_chunks": len(points)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Get embeddings for the question
    question_embedding = embedding_model.encode(request.question)
    
    # Search in Qdrant
    search_results = qdrant_client.query_points(
        collection_name=collection_name,
        query=question_embedding.tolist(),
        limit=5
    ).points
    
    if not search_results:
        return ChatResponse(answer="No relevant documents found.", sources=[])
    
    # Prepare context and sources
    context_chunks = []
    sources = set()
    
    for result in search_results:
        context_chunks.append(result.payload["text"])
        # Handle both old format (chunk_id) and new format (page)
        if 'page' in result.payload:
            sources.add(f"{result.payload['filename']} (Page {result.payload['page']})")
        else:
            sources.add(f"{result.payload['filename']} (Chunk {result.payload['chunk_id']})")
    
    context = "\n\n".join(context_chunks)
    
    # Generate response using Groq
    prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say so.

Context:
{context}

Question: {request.question}

Answer:"""
    
    response = groq_client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.1
    )
    
    answer = response.choices[0].message.content
    
    return ChatResponse(answer=answer, sources=list(sources))

@app.get("/documents")
async def list_documents():
    # Get unique documents from Qdrant
    scroll_result = qdrant_client.scroll(
        collection_name=collection_name,
        limit=1000,
        with_payload=True
    )
    
    documents = {}
    for point in scroll_result[0]:
        filename = point.payload["filename"]
        if filename not in documents:
            documents[filename] = {"filename": filename, "chunks": 0}
        documents[filename]["chunks"] += 1
    
    return {"documents": list(documents.values())}

# Inngest endpoint
@app.get("/api/inngest")
async def inngest_endpoint():
    return {"status": "Inngest endpoint ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
