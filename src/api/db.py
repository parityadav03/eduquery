from sqlalchemy import create_engine, text
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("MYSQL_URL"))

def create_session(session_id: str):
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO sessions (id) VALUES (:id)"
        ), {"id": session_id})
        conn.commit()

def log_query(session_id: str, question: str, answer: str, sources: list, latency_ms: int):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO query_history (session_id, question, answer, sources, latency_ms)
            VALUES (:session_id, :question, :answer, :sources, :latency_ms)
        """), {
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "sources": json.dumps(sources),
            "latency_ms": latency_ms
        })
        conn.commit()

def get_history(session_id: str) -> list:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT question, answer, sources, latency_ms, created_at
            FROM query_history
            WHERE session_id = :session_id
            ORDER BY created_at DESC
            LIMIT 20
        """), {"session_id": session_id})
        rows = []
        for r in result:
            rows.append({
                "question": r[0],
                "answer": r[1],
                "sources": json.loads(r[2]),
                "latency_ms": r[3],
                "created_at": str(r[4])
            })
        return rows