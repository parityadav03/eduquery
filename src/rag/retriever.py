from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "eduquery")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY if QDRANT_API_KEY else None
)

def get_relevant_docs(query: str, k: int = 5) -> list[Document]:
    query_vector = embedder.embed_query(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=k,
        with_payload=True
    ).points

    docs = []
    for hit in results:
        payload = hit.payload
        docs.append(Document(
            page_content=payload.get("text", ""),
            metadata={
                "source_file": payload.get("source_file", "unknown"),
                "page_num": payload.get("page_num", 0),
                "subject_tag": payload.get("subject_tag", ""),
                "chunk_index": payload.get("chunk_index", 0),
                "score": round(hit.score, 4)
            }
        ))
    return docs