from fastapi import FastAPI
from pydantic import BaseModel

from src.search import (
    load_documents,
    get_top_chunks,
    create_context,
    generate_answer
)


app = FastAPI(
    title="Local RAG API"
)


documents = load_documents()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():

    return {
        "message": "Local RAG API is running"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        return {
            "answer": "Lütfen bir soru girin.",
            "sources": []
        }

    chunks = get_top_chunks(
        question,
        documents,
        top_k=4,
        similarity_threshold=0.40
    )

    if not chunks:
        return {
            "answer": "Bu konuda yeterli bilgim bulunmadı.",
            "sources": []
        }

    context = create_context(chunks)

    answer = generate_answer(
        question,
        context
    )

    sources = []

    for i, (text, similarity) in enumerate(chunks, 1):

        sources.append({
            "chunk": i,
            "similarity": round(similarity, 4)
        })

    return {
        "answer": answer,
        "sources": sources
    }