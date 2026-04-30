from llama_cpp import Llama
from src.rag.retriever import get_relevant_docs
from src.rag.prompt import ACADEMIC_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH")

_llm = None

def load_llm():
    global _llm
    if _llm is None:
        print("Loading LLaMA model...")
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=4096,
            n_threads=4,
            verbose=False
        )
        print("Model loaded!")
    return _llm

def format_context(docs) -> str:
    parts = []
    for doc in docs:
        parts.append(
            f"[Source: {doc.metadata['source_file']}, Page {doc.metadata['page_num']}]\n{doc.page_content}"
        )
    return "\n\n".join(parts)

def ask(question: str, k: int = 5) -> dict:
    docs = get_relevant_docs(question, k=k)
    context = format_context(docs)

    prompt_text = ACADEMIC_PROMPT.format(
        context=context,
        question=question
    )

    llm = load_llm()
    response = llm(
        prompt_text,
        max_tokens=1024,
        temperature=0.3,
        stop=["Student Question:", "\n\n\n"]
    )

    answer = response["choices"][0]["text"].strip()

    sources = list(set([
        f"{d.metadata['source_file']} (p.{d.metadata['page_num']})"
        for d in docs
    ]))

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }