from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "eduquery")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output size

def get_embedder():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def setup_collection(client: QdrantClient):
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")

def embed_and_store(chunks: list[dict], batch_size: int = 100):
    embedder = get_embedder()
    client = QdrantClient(url=QDRANT_URL)
    setup_collection(client)

    total = len(chunks)
    print(f"Embedding {total} chunks in batches of {batch_size}...")

    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        vectors = embedder.embed_documents(texts)

        points = [
            PointStruct(
                id=i + j,
                vector=vectors[j],
                payload={
                    "text": batch[j]["text"],
                    **batch[j]["metadata"]
                }
            )
            for j in range(len(batch))
        ]

        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  Stored {min(i + batch_size, total)}/{total} chunks")

    print(f"\nDone! {total} chunks stored in Qdrant collection '{COLLECTION_NAME}'")