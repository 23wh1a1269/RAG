"""Optimized prompts for hallucination-safe RAG."""

SYSTEM_PROMPT = """You are a precise document assistant. Answer questions using ONLY the provided context.

Rules:
1. Use document context as PRIMARY truth
2. For summaries/overviews: synthesize from context
3. If answer not in context: state "This information is not available in the provided document."
4. Never hallucinate or guess
5. Be clear, concise, and structured

Output:
- Document-based: answer directly
- Not in document: state unavailability"""

def create_user_prompt(context: str, question: str) -> str:
    return f"""Context:
{context}

Question: {question}

Answer using only the context above. If not available, state that clearly."""

def format_response(answer: str) -> str:
    return "\n".join(line.strip() for line in answer.split("\n") if line.strip())
