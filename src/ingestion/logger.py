from sqlalchemy import create_engine, text
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("MYSQL_URL"))

def log_ingestion(filename: str, chunk_count: int):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO uploaded_docs (filename, chunk_count, ingested_at)
            VALUES (:filename, :chunk_count, :ingested_at)
        """), {
            "filename": filename,
            "chunk_count": chunk_count,
            "ingested_at": datetime.utcnow()
        })
        conn.commit()
    print(f"Logged: {filename} ({chunk_count} chunks)")