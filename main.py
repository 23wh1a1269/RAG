import logging
import uuid
import os

from fastapi import FastAPI
from pydantic import BaseModel
import inngest
import inngest.fast_api
from groq import Groq
from dotenv import load_dotenv

from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage

load_dotenv()

# Model configuration with fallback
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
FALLBACK_MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

app = FastAPI()

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer(),
)


# ---------- INGEST FUNCTION ----------

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
)
async def rag_ingest_pdf(ctx: inngest.Context):

    def load_step():
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get(
            "source_id", os.path.basename(pdf_path)
        )
        chunks = load_and_chunk_pdf(pdf_path)
        return {"chunks": chunks, "source_id": source_id}

    def upsert_step(data: dict):
        chunks = data["chunks"]
        source_id = data["source_id"]

        vectors = embed_texts(chunks)
        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}"))
            for i in range(len(chunks))
        ]
        payloads = [{"text": c, "source": source_id} for c in chunks]

        QdrantStorage().upsert(ids, vectors, payloads)
        return {"ingested": len(chunks)}

    data = await ctx.step.run("load-pdf", load_step)
    return await ctx.step.run("embed-upsert", lambda: upsert_step(data))

class IngestRequest(BaseModel):
    pdf_path: str
    source_id: str | None = None


@app.post("/rag/ingest")
async def ingest_http(req: IngestRequest):
    """
    HTTP endpoint used by Streamlit.
    This ONLY triggers the Inngest ingestion workflow.
    """
    await inngest_client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": req.pdf_path,
                "source_id": req.source_id or os.path.basename(req.pdf_path),
            },
        )
    )
    return {"status": "ingestion triggered"}

# ---------- QUERY FUNCTION (INNGEST) ----------

@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))

    store = QdrantStorage()
    query_vector = embed_texts([question])[0]
    found = store.search(query_vector, top_k)

    if not found["contexts"]:
        return {
            "answer": "No relevant context found.",
            "sources": [],
            "num_contexts": 0,
        }

    context_block = "\n\n".join(found["contexts"])

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Try models with fallback
    for model in FALLBACK_MODELS:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Answer only using the context."},
                    {
                        "role": "user",
                        "content": f"Context:\n{context_block}\n\nQuestion:\n{question}",
                    },
                ],
                temperature=0.2,
                max_tokens=1024,
            )
            break
        except Exception as e:
            if "model_decommissioned" in str(e) and model != FALLBACK_MODELS[-1]:
                continue
            raise

    return {
        "answer": completion.choices[0].message.content.strip(),
        "sources": found["sources"],
        "num_contexts": len(found["contexts"]),
    }


# ---------- HTTP QUERY (for Streamlit) ----------

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


@app.post("/rag/query")
async def query(req: QueryRequest):
    try:
        store = QdrantStorage()

        query_vector = embed_texts([req.question])[0]
        found = store.search(query_vector, req.top_k)

        if not found["contexts"]:
            return {
                "answer": "No relevant context found in the uploaded documents.",
                "sources": [],
                "num_contexts": 0,
            }

        context_block = "\n\n".join(found["contexts"])

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Try models with fallback
        for model in FALLBACK_MODELS:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Answer ONLY using the provided context.",
                        },
                        {
                            "role": "user",
                            "content": f"Context:\n{context_block}\n\nQuestion:\n{req.question}",
                        },
                    ],
                    temperature=0.2,
                    max_tokens=1024,
                )
                break
            except Exception as e:
                if "model_decommissioned" in str(e) and model != FALLBACK_MODELS[-1]:
                    continue
                raise

        return {
            "answer": completion.choices[0].message.content.strip(),
            "sources": found["sources"],
            "num_contexts": len(found["contexts"]),
        }

    except Exception as e:
        # IMPORTANT: surface backend error
        import traceback
        return {
            "answer": "Backend error while processing query.",
            "sources": [],
            "num_contexts": 0,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


# ---------- REGISTER FUNCTIONS ----------

inngest.fast_api.serve(
    app,
    inngest_client,
    functions=[rag_ingest_pdf, rag_query_pdf_ai],
)
