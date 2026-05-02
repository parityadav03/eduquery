from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import time
import shutil
import os
from dotenv import load_dotenv

load_dotenv()

from src.rag.groq_chain import ask
from src.ingestion.loader import load_pdfs_from_folder
from src.ingestion.chunker import chunk_pages
from src.ingestion.embedder import embed_and_store
from src.ingestion.logger import log_ingestion
from src.api.db import create_session, log_query, get_history

app = FastAPI(title="EduQuery API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class QueryRequest(BaseModel):
    session_id: str
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    latency_ms: int

# ── POST /query ───────────────────────────────────────────
@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    start = time.time()

    # auto-create session if it doesn't exist
    try:
        create_session(req.session_id)
    except Exception:
        pass  # session already exists, that's fine

    try:
        result = ask(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    latency = round((time.time() - start) * 1000)
    log_query(
        session_id=req.session_id,
        question=req.question,
        answer=result["answer"],
        sources=result["sources"],
        latency_ms=latency
    )

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        latency_ms=latency
    )

# ── GET /history ──────────────────────────────────────────
@app.get("/history/{session_id}")
def history(session_id: str):
    rows = get_history(session_id)
    return {"session_id": session_id, "history": rows}

# ── POST /upload ──────────────────────────────────────────
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    save_path = f"data/pdfs/{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    pages = load_pdfs_from_folder("data/pdfs")
    chunks = chunk_pages(pages)
    embed_and_store(chunks)
    log_ingestion(file.filename, len(chunks))

    return {"message": f"Uploaded and indexed {file.filename}", "chunks": len(chunks)}

# ── GET /session ──────────────────────────────────────────
@app.get("/session")
def new_session():
    session_id = str(uuid.uuid4())
    create_session(session_id)
    return {"session_id": session_id}